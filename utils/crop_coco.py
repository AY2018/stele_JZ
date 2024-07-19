import json
from PIL import Image, ImageDraw
import numpy as np
import os

# Define the file name (without extension) as a variable
file_name = '00065'

# Define the input paths
image_path = f'/Users/ayoub/Documents/GitHub/stele_JZ/images/{file_name}.jpg'
json_path = f'/Users/ayoub/Documents/GitHub/stele_JZ/annotations/{file_name}.json'

# Define the output paths
output_image_path = f'/Users/ayoub/Documents/GitHub/stele_JZ/intext_images/{file_name}_intext.jpg'
output_json_path = f'/Users/ayoub/Documents/GitHub/stele_JZ/intext_annotations/{file_name}_intext.json'

def adjust_annotations(coco_data, crop_box, intext_polygon):
    adjusted_annotations = []
    for annotation in coco_data['annotations']:
        if annotation['category_id'] == 2:  # Category ID = "text"
            new_segmentation = []
            for i in range(0, len(annotation['segmentation'][0]), 2):
                x = int(annotation['segmentation'][0][i] - crop_box[0])
                y = int(annotation['segmentation'][0][i + 1] - crop_box[1])
                new_segmentation.extend([x, y])
            
            new_bbox = [
                int(annotation['bbox'][0] - crop_box[0]),
                int(annotation['bbox'][1] - crop_box[1]),
                int(annotation['bbox'][2]),
                int(annotation['bbox'][3])
            ]
            
            adjusted_annotations.append({
                "id": annotation['id'],
                "iscrowd": annotation['iscrowd'],
                "image_id": annotation['image_id'],
                "category_id": annotation['category_id'],
                "segmentation": [new_segmentation],
                "bbox": new_bbox,
                "area": annotation['area']
            })
    
    return adjusted_annotations

def crop_image_and_adjust_annotations(image_path, json_path, output_image_path, output_json_path):
    with open(json_path) as f:
        coco_data = json.load(f)

    image = Image.open(image_path)

    intext_polygon = None
    for annotation in coco_data['annotations']:
        if annotation['category_id'] == 7:  # Category ID = "Intext"
            intext_polygon = annotation['segmentation'][0]
            break

    if intext_polygon is None:
        raise ValueError("No polygon found for the 'Intext' category.")

    polygon = [(intext_polygon[i], intext_polygon[i + 1]) for i in range(0, len(intext_polygon), 2)]

    # Create a mask
    mask = Image.new('L', image.size, 0)
    ImageDraw.Draw(mask).polygon(polygon, outline=1, fill=1)
    mask = np.array(mask)

    # Create a new image
    new_image = Image.new('RGBA', image.size)
    new_image.paste(image, (0, 0), mask=Image.fromarray(mask * 255))

    # Crop the image to the bounding box of the polygon
    bbox = mask.nonzero()
    crop_box = (int(min(bbox[1])), int(min(bbox[0])), int(max(bbox[1])), int(max(bbox[0])))
    cropped_image = new_image.crop(crop_box)

    # Convert RGBA to RGB
    cropped_image = cropped_image.convert('RGB')
    cropped_image.save(output_image_path, 'JPEG')

    # Adjust annotations
    adjusted_annotations = adjust_annotations(coco_data, crop_box, intext_polygon)

    new_coco_data = {
        "info": coco_data["info"],
        "images": [{
            "id": coco_data["images"][0]["id"],
            "width": crop_box[2] - crop_box[0],
            "height": crop_box[3] - crop_box[1],
            "file_name": os.path.basename(output_image_path)  # Ensure the file name matches the cropped image
        }],
        "annotations": adjusted_annotations,
        "categories": [cat for cat in coco_data["categories"] if cat["id"] == 2]
    }

    with open(output_json_path, 'w') as f:
        json.dump(new_coco_data, f, indent=4)

# Example usage
crop_image_and_adjust_annotations(
    image_path=image_path,
    json_path=json_path,
    output_image_path=output_image_path,
    output_json_path=output_json_path
)

print(f"Cropped image saved to {output_image_path}")
print(f"Adjusted annotations saved to {output_json_path}")
