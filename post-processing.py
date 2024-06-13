import csv
import logging

import cv2 as cv
import numpy as np

from datetime import datetime
from matplotlib import pyplot as plt

from compare import FolderComparator
from modules import ConfigLoader
from coordinates import get_meteor_start_end_coordinates

home_dir = ConfigLoader().get_home_dir()
compare = FolderComparator()

# TODO: clean up and structure the code, now it's a mess

logging.basicConfig(
    # filename="app.log",
    # filemode="a",
    format="%(asctime)s > %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)

def get_quadrant_coordinates(
    center_x, center_y, radius, quadrant_size
):  # Function to get quadrant coordinates
    coordinates = []
    for i in range(3):
        for j in range(3):
            x1 = center_x - radius + j * quadrant_size
            y1 = center_y - radius + i * quadrant_size
            x2 = x1 + quadrant_size
            y2 = y1 + quadrant_size
            coordinates.append(((x1, y1), (x2, y2)))
    return coordinates

def main():
    comparison_results = compare.find_matching_folders()
    with open(f"{home_dir}/comparison_results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Meteor",
                "Date",
                "Time",
                "Detection Type",
                "Location",
                "Time",
                "Detection Type",
                "Location",
                "Time Difference",
            ]
        )
        num = 000
        for result in comparison_results:
            logging.debug(result)

            # Convert data to the format that will be written to the CSV file
            meteor_date = datetime.strptime(result[0][2], "%d.%m.%Y")
            meteor_month = meteor_date.strftime("%m")
            meteor_time = datetime.strptime(result[0][3], "%H:%M:%S")

            if meteor_month == 10:
                meteor_month = "A"
            elif meteor_month == 11:
                meteor_month = "B"
            elif meteor_month == 12:
                meteor_month = "C"

            # TODO: how to get the meteor number? - list all meteors in the folder with date and time before meteor time
            meteor_number = str(num).zfill(3)
            num += 1

            # TODO: if cannot get meteor coordinates, set detection type to "N"
            # First detection of the meteor
            if result[0][1]:
                detection_type = "Ma"
                meteor_position = get_meteor_start_end_coordinates(
                    result[0][0] + "/data.txt"
                )

                if meteor_position == (None, None) or None:
                    logging.error(
                        f"Could not get meteor coordinates for {result[0][0]}, skipping..."
                    )
                    continue

                start_coords = meteor_position[0]
                end_coords = meteor_position[1]
                # TODO: check if image exists, or find image path automatically
                meteor_img_path = (
                    result[0][0] + "/" + result[0][0].split("/")[-1] + ".jpg"
                )

                # Check if the image exists
                if not meteor_img_path:
                    logging.error(f"Meteor image not found {meteor_img_path}, skipping...")
                    continue

                image = cv.imread(meteor_img_path, cv.IMREAD_GRAYSCALE)
                height, width = image.shape

                # Calculate the center and radius of the circle
                center_x, center_y = width // 2, height // 2
                radius = min(center_x, center_y)

                # Calculate the size of each quadrant
                quadrant_size = radius * 2 // 3

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
                        [
                            center_y - radius + i * quadrant_size,
                            center_y - radius + i * quadrant_size,
                        ],
                        color="red",
                    )
                    # Vertical lines
                    ax.plot(
                        [
                            center_x - radius + i * quadrant_size,
                            center_x - radius + i * quadrant_size,
                        ],
                        [center_y - radius, center_y + radius],
                        color="red",
                    )

                # Calculate from which quadrant the meteor is coming from
                for i, (top_left, bottom_right) in enumerate(quadrant_coordinates):
                    if (
                        top_left[0] <= start_coords[0] <= bottom_right[0]
                        and top_left[1] <= start_coords[1] <= bottom_right[1]
                    ):
                        logging.info(f"The meteor first point from quadrant {i+1}")
                        location = i + 1
                        break

                # Calculate in which quadrant the meteor is going to
                for i, (top_left, bottom_right) in enumerate(quadrant_coordinates):
                    if (
                        top_left[0] <= end_coords[0] <= bottom_right[0]
                        and top_left[1] <= end_coords[1] <= bottom_right[1]
                    ):
                        logging.info(f"The meteor second point from quadrant {i+1}")
                        location1 = i + 1
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

            else:
                detection_type = "D"
            
            # Second detection of the meteor
            if result[1][1]:
                detection_type1 = "Ma"
            else:
                detection_type1 = "D"

            meteor = (
                meteor_date.strftime("%Y")
                + meteor_month
                + meteor_date.strftime("%d")
                + meteor_number
            )
            date = result[0][2]
            time = result[0][3]
            location = location
            time1 = result[1][3]
            location1 = location1

            string = f"{meteor},{date},{time},{detection_type},{location},{time1},{detection_type1},{location1},{result[2]}"
            logging.info(string)
            writer.writerow(
                [
                    meteor,
                    date,
                    time,
                    detection_type,
                    location,
                    time1,
                    detection_type1,
                    location1,
                    result[2],
                ]
            )


if __name__ == "__main__":
    main()
