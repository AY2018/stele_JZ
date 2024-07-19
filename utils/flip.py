import os
from PIL import Image, ImageOps

# Define the directories
image_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/dataset/images/train'
label_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/dataset/labels/train'

# Get list of images and labels
image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
label_files = [f for f in os.listdir(label_dir) if f.endswith('.txt')]

# Function to flip image and save with new name
def flip_image(image_path, new_image_path):
    try:
        image = Image.open(image_path)
        flipped_image = image.transpose(method=Image.FLIP_LEFT_RIGHT)
        flipped_image = flipped_image.convert('RGB')
        flipped_image.save(new_image_path, format='JPEG')
        print(f"Flipped image saved: {new_image_path}")
    except Exception as e:
        print(f"Failed to process image {image_path}: {e}")

# Function to flip YOLO coordinates and save with new name
def flip_yolo_coordinates(label_path, new_label_path):
    try:
        with open(label_path, 'r') as file:
            lines = file.readlines()

        new_lines = []
        for line in lines:
            data = line.strip().split()
            class_id = data[0]
            coords = list(map(float, data[1:]))

            flipped_coords = []
            for i in range(0, len(coords), 2):
                x = coords[i]
                flipped_x = 1 - x  # Flip x-coordinate
                flipped_coords.append(flipped_x)
                flipped_coords.append(coords[i + 1])

            new_line = f"{class_id} {' '.join(map(str, flipped_coords))}\n"
            new_lines.append(new_line)

        with open(new_label_path, 'w') as file:
            file.writelines(new_lines)
        print(f"Flipped label saved: {new_label_path}")
    except Exception as e:
        print(f"Failed to process label {label_path}: {e}")

# Function to invert image colors and save with new name
def invert_colors(image_path, new_image_path):
    try:
        image = Image.open(image_path)
        inverted_image = ImageOps.invert(image.convert("RGB"))
        inverted_image.save(new_image_path, format='JPEG')
        print(f"Inverted colors image saved: {new_image_path}")
    except Exception as e:
        print(f"Failed to process image {image_path}: {e}")

# Process each image and its corresponding label
for image_file in image_files:
    image_path = os.path.join(image_dir, image_file)
    
    # Flipping
    new_image_path_flip = os.path.join(image_dir, image_file.replace('.jpg', '_flip.jpg'))
    label_path = os.path.join(label_dir, image_file.replace('.jpg', '.txt'))
    new_label_path_flip = os.path.join(label_dir, image_file.replace('.jpg', '_flip.txt'))
    
    # Inverting colors
    new_image_path_invert = os.path.join(image_dir, image_file.replace('.jpg', '_inv_color.jpg'))
    new_label_path_invert = os.path.join(label_dir, image_file.replace('.jpg', '_inv_color.txt'))
    
    # Flipping and Inverting colors
    new_image_path_flip_invert = os.path.join(image_dir, image_file.replace('.jpg', '_flip_inv_color.jpg'))
    new_label_path_flip_invert = os.path.join(label_dir, image_file.replace('.jpg', '_flip_inv_color.txt'))

    if os.path.exists(label_path):
        print(f"Processing {image_path} and {label_path}")
        # Flipping
        flip_image(image_path, new_image_path_flip)
        flip_yolo_coordinates(label_path, new_label_path_flip)
        
        # Inverting colors
        invert_colors(image_path, new_image_path_invert)
        # Copy the original label file for the inverted color image
        if os.path.exists(label_path):
            with open(label_path, 'r') as original_file, open(new_label_path_invert, 'w') as new_file:
                new_file.write(original_file.read())
            print(f"Copied original label to: {new_label_path_invert}")

        # Flipping and Inverting colors
        flip_image(image_path, new_image_path_flip_invert)
        invert_colors(new_image_path_flip_invert, new_image_path_flip_invert)
        flip_yolo_coordinates(label_path, new_label_path_flip_invert)
    else:
        print(f"Label file does not exist: {label_path}")
