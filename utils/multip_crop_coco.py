import json
from PIL import Image, ImageDraw
import numpy as np
import os

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

# Define the directories
images_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/images'
annotations_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/annotations'
output_images_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/intext_images'
output_annotations_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/intext_annotations'

# Ensure output directories exist
os.makedirs(output_images_dir, exist_ok=True)
os.makedirs(output_annotations_dir, exist_ok=True)

# List to keep track of errors
errors = []

# Process each JSON file in the annotations directory
for file_name in os.listdir(annotations_dir):
    if file_name.endswith('.json'):
        base_name = os.path.splitext(file_name)[0]
        image_path = os.path.join(images_dir, f"{base_name}.jpg")
        json_path = os.path.join(annotations_dir, file_name)
        output_image_path = os.path.join(output_images_dir, f"{base_name}_intext.jpg")
        output_json_path = os.path.join(output_annotations_dir, f"{base_name}_intext.json")
        
        if os.path.exists(image_path):
            try:
                crop_image_and_adjust_annotations(image_path, json_path, output_image_path, output_json_path)
                print(f"Cropped image saved to {output_image_path}")
                print(f"Adjusted annotations saved to {output_json_path}")
            except Exception as e:
                errors.append((file_name, str(e)))
                print(f"Error processing {file_name}: {e}")
        else:
            error_message = f"Image file {image_path} does not exist."
            errors.append((file_name, error_message))
            print(error_message)

# Print out all errors at the end
if errors:
    print("\nSummary of errors:")
    for file_name, error in errors:
        print(f"{file_name}: {error}")
