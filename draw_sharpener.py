from PIL import Image
from sklearn.cluster import KMeans
import numpy as np
import os
from collections import Counter

def process_image(image_path, n_colors, forced_colors=None):
    # Open the image
    img = Image.open(image_path).convert("RGB")  # Ensure RGB mode
    img_array = np.array(img)

    # Reshape the image to a 2D array of pixels
    pixels = img_array.reshape(-1, 3)

    # Perform KMeans clustering to find the most common colors
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init='auto')
    kmeans.fit(pixels)

    # Get the most common colors
    most_common_colors = np.array(kmeans.cluster_centers_, dtype=np.uint8).tolist()

    # Add forced colors (if any)
    if forced_colors:
        # Convert forced colors to the correct format
        forced_colors = [tuple(map(int, color)) for color in forced_colors]
        for color in forced_colors:
            if color not in most_common_colors:
                most_common_colors.append(color)

        # Limit to n_colors total, if necessary
        most_common_colors = most_common_colors[:n_colors]

    # Map each pixel to the nearest color in the modified palette
    def find_closest_color(pixel):
        return min(most_common_colors, key=lambda c: np.linalg.norm(np.array(c) - np.array(pixel)))

    mapped_pixels = np.apply_along_axis(find_closest_color, axis=1, arr=pixels)
    mapped_image = np.array(mapped_pixels, dtype=np.uint8).reshape(img_array.shape)

    # Save the processed image
    output_img = Image.fromarray(mapped_image, mode="RGB")
    output_path = os.path.splitext(image_path)[0] + f'_processed_{n_colors}.png'
    output_img.save(output_path, format="PNG")
    print(f"Processed image saved to: {output_path}")

# Example usage
image_path = "C:\\Users\\lohoff\\Pictures\\Laser\\Ouija mit Jascha\\photo_2024-12-05_15-27-01.jpg"  # Replace with your image path
n_colors = 5  # Replace with the desired number of colors
forced_colors = [(255, 255, 255), (117, 118, 136)]  # White and Light Blue
process_image(image_path, n_colors, forced_colors)