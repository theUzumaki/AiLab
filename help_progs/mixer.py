import numpy as np
from PIL import Image
import random

def mix_images(image_path1, image_path2, output_path):
    # Load images
    img1 = Image.open(image_path1).convert('RGB')
    img2 = Image.open(image_path2).convert('RGB')

    img1 = img1.resize((64, 64))
    img2 = img2.resize((64, 64))

    # Convert images to numpy arrays
    arr1 = np.array(img1)
    arr2 = np.array(img2)

    # Create an empty array for the mixed image
    mixed_arr = np.zeros_like(arr1)

    # Mix pixels pseudo-randomly
    for i in range(64):
        for j in range(64):
            if random.random() > 0.5:
                mixed_arr[i, j] = arr1[i, j]
            else:
                mixed_arr[i, j] = arr2[i, j]

    # Convert the mixed array back to an image
    mixed_img = Image.fromarray(mixed_arr)

    # Save the mixed image
    mixed_img.save(output_path)

# Example usage
mix_images('/Users/Mattia/Desktop/studio/uni/AiLab/JAVA_project/src/sprites/floors/floor1.png', '/Users/Mattia/Desktop/studio/uni/AiLab/JAVA_project/src/sprites/floors/grass1.png', '/Users/Mattia/Desktop/studio/uni/AiLab/JAVA_project/src/sprites/floors/floor2.png')