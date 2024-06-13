# This file will be removed after the code is cleaned up and structured
# It is only for testing purposes

import cv2
import numpy as np
from matplotlib import pyplot as plt

# Load the image
image_path = "/home/foglar/Programming/Projects/OV2024-Project/meteory/Ondrejov/2024-01-09-01-30-23/2024-01-09-01-30-23.jpg"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Get image dimensions
height, width = image.shape

# Calculate the center and radius of the circle
center_x, center_y = width // 2, height // 2
radius = min(center_x, center_y)

# Calculate the size of each quadrant
quadrant_size = radius * 2 // 3


# Function to get quadrant coordinates
def get_quadrant_coordinates(center_x, center_y, radius, quadrant_size):
    coordinates = []
    for i in range(3):
        for j in range(3):
            x1 = center_x - radius + j * quadrant_size
            y1 = center_y - radius + i * quadrant_size
            x2 = x1 + quadrant_size
            y2 = y1 + quadrant_size
            coordinates.append(((x1, y1), (x2, y2)))
    return coordinates


# Calculate quadrant coordinates
quadrant_coordinates = get_quadrant_coordinates(
    center_x, center_y, radius, quadrant_size
)

# Draw the 3x3 grid and the meteor's path
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.imshow(image, cmap="gray")

# Draw the grid
for i in range(1, 3):
    # Horizontal lines
    ax.plot(
        [center_x - radius, center_x + radius],
        [center_y - radius + i * quadrant_size, center_y - radius + i * quadrant_size],
        color="red",
    )
    # Vertical lines
    ax.plot(
        [center_x - radius + i * quadrant_size, center_x - radius + i * quadrant_size],
        [center_y - radius, center_y + radius],
        color="red",
    )

# Define the start and end coordinates of the meteor
start_coords = (370.5, 244.5)
end_coords = (392.5, 253.5)

# Calculate from which quadrant the meteor is coming from
for i, (top_left, bottom_right) in enumerate(quadrant_coordinates):
    if (
        top_left[0] <= start_coords[0] <= bottom_right[0]
        and top_left[1] <= start_coords[1] <= bottom_right[1]
    ):
        print(f"The meteor is coming from quadrant {i+1}")
        break

# Calculate in which quadrant the meteor is going to
for i, (top_left, bottom_right) in enumerate(quadrant_coordinates):
    if (
        top_left[0] <= end_coords[0] <= bottom_right[0]
        and top_left[1] <= end_coords[1] <= bottom_right[1]
    ):
        print(f"The meteor is going to quadrant {i+1}")
        break

# Draw the meteor's path
ax.plot(
    [start_coords[0], end_coords[0]],
    [start_coords[1], end_coords[1]],
    color="yellow",
    linewidth=2,
)

# Display the image with the quadrants and meteor's path
plt.show()

# Print the quadrant coordinates
for i, coord in enumerate(quadrant_coordinates):
    print(f"Quadrant {i+1}: {coord}")

