import cv2
import numpy as np
import os

def draw_polygons(image_path, yolo_txt_path):
    # Load the image
    image = cv2.imread(image_path)
    img_height, img_width = image.shape[:2]

    with open(yolo_txt_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split()
        class_id = int(parts[0])
        coordinates = list(map(float, parts[1:]))

        # Denormalize the coordinates
        points = []
        for i in range(0, len(coordinates), 2):
            x = int(coordinates[i] * img_width)
            y = int(coordinates[i + 1] * img_height)
            points.append((x, y))

        # Convert points to a numpy array and reshape it
        points = np.array(points, np.int32).reshape((-1, 1, 2))

        # Draw the polygon
        cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=2)

    # Display the image with polygons
    cv2.imshow('Image with Polygons', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Define the file name 
file_name = '00383-21_inv_color_shear'  

# Construct the input paths
image_path = f'/Users/ayoub/Documents/GitHub/stele_JZ/dataset/images/train/{file_name}.jpg'
yolo_txt_path = f'/Users/ayoub/Documents/GitHub/stele_JZ/dataset/labels/train/{file_name}.txt'
# Draw polygons on the image and display it
draw_polygons(
    image_path=image_path,
    yolo_txt_path=yolo_txt_path
)

print("Image displayed with polygons.")

