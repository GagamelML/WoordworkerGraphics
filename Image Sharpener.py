from PIL import Image
from collections import Counter
import numpy as np
import os


def euclidean_distance(color1, color2):
    """Calculate the Euclidean distance between two RGB colors."""
    return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5


def find_closest_color(color, palette):
    """Find the closest color from the palette to the given color."""
    return min(palette, key=lambda palette_color: euclidean_distance(color, palette_color))


def process_image(image_path, n_colors):
    """
    Process the image to retain only the top N colors and replace
    other pixels with the nearest of these colors.
    """
    if not os.path.exists(image_path):
        print(f"File {image_path} does not exist.")
        return

    # Load the image
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = np.array(img)
    pixel_list = pixels.reshape(-1, 3)

    # Calculate the color histogram
    color_counts = Counter(map(tuple, pixel_list))
    most_common_colors = [color for color, _ in color_counts.most_common(n_colors)]

    # Process pixels to replace colors with closest from the palette
    def replace_pixel(pixel):
        if tuple(pixel) in most_common_colors:
            return pixel
        return find_closest_color(pixel, most_common_colors)

    processed_pixels = np.array([replace_pixel(pixel) for pixel in pixel_list], dtype=np.uint8)
    processed_image_array = processed_pixels.reshape(pixels.shape)

    # Create a new image
    processed_img = Image.fromarray(processed_image_array, 'RGB')

    # Save and return the processed image
    output_path = os.path.splitext(image_path)[0] + f'_processed_{n_colors}.png'
    processed_img.save(output_path)
    print(f"Processed image saved to: {output_path}")
    return output_path


# Example usage
image_path = "D:\Eigene Dateien\Pictures\Laser\quija mit jascha\quija 2.png"  # Replace with your image path
n_colors = 5  # Replace with the desired number of colors
process_image(image_path, n_colors)