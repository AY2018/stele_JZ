import os

def find_outliers(images_dir, labels_dir):
    # Get the list of file names without extensions
    image_files = {os.path.splitext(f)[0] for f in os.listdir(images_dir) if f.endswith('.jpg')}
    label_files = {os.path.splitext(f)[0] for f in os.listdir(labels_dir) if f.endswith('.txt')}
    
    # Find outliers
    images_without_labels = image_files - label_files
    labels_without_images = label_files - image_files

    return images_without_labels, labels_without_images

def print_outliers(images_without_labels, labels_without_images, images_dir, labels_dir):
    if images_without_labels:
        print("Images without corresponding labels:")
        for img in images_without_labels:
            print(os.path.join(images_dir, img + '.jpg'))
    else:
        print("No images without corresponding labels.")

    if labels_without_images:
        print("\nLabels without corresponding images:")
        for lbl in labels_without_images:
            print(os.path.join(labels_dir, lbl + '.txt'))
    else:
        print("No labels without corresponding images.")

# Define the directories
images_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/dataset/images/train'
labels_dir = '/Users/ayoub/Documents/GitHub/stele_JZ/dataset/labels/train'

# Find and print outliers
images_without_labels, labels_without_images = find_outliers(images_dir, labels_dir)
print_outliers(images_without_labels, labels_without_images, images_dir, labels_dir)
