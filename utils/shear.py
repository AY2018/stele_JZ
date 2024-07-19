import os
import random
import json
from PIL import Image
import numpy as np
import math

# Define the directories
image_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/dataset/images/train'
label_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/dataset/labels/train'

# Function to shear image and save with new name
def shear_image(image_path, new_image_path, shear_angle):
    try:
        image = Image.open(image_path)
        width, height = image.size

        # Convert angle to radians
        angle_rad = math.radians(shear_angle)
        
        # Shear transformation matrix
        shear_matrix = (1, angle_rad, 0, 0, 1, 0)
        
        # Apply shear transformation
        sheared_image = image.transform((width, height), Image.AFFINE, shear_matrix, resample=Image.BICUBIC)
        sheared_image = sheared_image.convert('RGB')
        sheared_image.save(new_image_path, format='JPEG')
    except Exception as e:
        print(f"Failed to process image {image_path}: {e}")

# Function to shear YOLO coordinates and save with new name
def shear_yolo_coordinates_opposite(label_path, new_label_path, shear_angle, image_width, image_height):
    try:
        with open(label_path, 'r') as file:
            lines = file.readlines()

        # Convert angle to radians
        angle_rad = math.radians(shear_angle)
        opposite_angle_rad = -angle_rad  # Apply the opposite shear angle
        
        new_lines = []
        for line in lines:
            data = line.strip().split()
            class_id = data[0]
            coords = list(map(float, data[1:]))

            sheared_coords = []
            for i in range(0, len(coords), 2):
                x = coords[i] * image_width
                y = coords[i + 1] * image_height

                # Apply the opposite shear transformation
                sheared_x = x + opposite_angle_rad * y
                sheared_y = y

                # Normalize coordinates
                sheared_x_norm = sheared_x / image_width
                sheared_y_norm = sheared_y / image_height

                # Only include coordinates that are within the [0, 1] range
                if 0 <= sheared_x_norm <= 1 and 0 <= sheared_y_norm <= 1:
                    sheared_coords.append(sheared_x_norm)
                    sheared_coords.append(sheared_y_norm)

            # If we have valid coordinates, write them to the new file
            if sheared_coords:
                new_line = f"{class_id} {' '.join(map(str, sheared_coords))}\n"
                new_lines.append(new_line)

        with open(new_label_path, 'w') as file:
            file.writelines(new_lines)
    except Exception as e:
        print(f"Failed to process label {label_path}: {e}")

# Process each image and its corresponding label
for image_file in os.listdir(image_dir):
    if image_file.endswith('.jpg'):
        image_path = os.path.join(image_dir, image_file)
        label_path = os.path.join(label_dir, image_file.replace('.jpg', '.txt'))
        
        if os.path.exists(label_path):
            shear_angle = random.uniform(-45, 45)  # Random shear angle between -45 and 45 degrees
            new_image_path_shear = os.path.join(image_dir, image_file.replace('.jpg', '_shear.jpg'))
            new_label_path_shear_opposite = os.path.join(label_dir, image_file.replace('.jpg', '_shear.txt'))

            image = Image.open(image_path)
            width, height = image.size
            

            shear_image(image_path, new_image_path_shear, shear_angle)
            shear_yolo_coordinates_opposite(label_path, new_label_path_shear_opposite, shear_angle, width, height)
        else:
            print(f"Label file does not exist: {label_path}")
