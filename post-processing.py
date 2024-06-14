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

logging.basicConfig(
    format="%(asctime)s > %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)


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


def plot_images_with_grid(image1, image2, coords1, coords2, start_coords1, end_coords1, start_coords2, end_coords2):
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    axes = axes.ravel()

    images = [image1, image2]
    coords = [coords1, coords2]
    starts = [start_coords1, start_coords2]
    ends = [end_coords1, end_coords2]

    for ax, image, quadrant_coordinates, start_coords, end_coords in zip(axes, images, coords, starts, ends):
        height, width = image.shape
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)
        quadrant_size = radius * 2 // 3

        ax.imshow(image, cmap="gray")
        ax.set_title("Meteor Detection", fontsize=16)

        for i in range(1, 3):
            ax.plot(
                [center_x - radius, center_x + radius],
                [
                    center_y - radius + i * quadrant_size,
                    center_y - radius + i * quadrant_size,
                ],
                color="red",
            )
            ax.plot(
                [
                    center_x - radius + i * quadrant_size,
                    center_x - radius + i * quadrant_size,
                ],
                [center_y - radius, center_y + radius],
                color="red",
            )

        ax.plot(
            [start_coords[0], end_coords[0]],
            [start_coords[1], end_coords[1]],
            color="yellow",
            linewidth=2,
        )

    plt.show()


def determine_quadrant(start_coords, end_coords, quadrant_coordinates):
    start_location = end_location = None
    for i, (top_left, bottom_right) in enumerate(quadrant_coordinates):
        if (
            top_left[0] <= start_coords[0] <= bottom_right[0]
            and top_left[1] <= start_coords[1] <= bottom_right[1]
        ):
            start_location = i + 1
            logging.info(f"The meteor first point from quadrant {i+1}")

        if (
            top_left[0] <= end_coords[0] <= bottom_right[0]
            and top_left[1] <= end_coords[1] <= bottom_right[1]
        ):
            end_location = i + 1
            logging.info(f"The meteor second point from quadrant {i+1}")

        if start_location and end_location:
            break

    return start_location, end_location


def process_detection(result, index):
    if result[index][1]:
        detection_type = "Ma"
        meteor_position = get_meteor_start_end_coordinates(result[index][0] + "/data.txt")

        if meteor_position == (None, None) or None:
            logging.error(f"Could not get meteor coordinates for {result[index][0]}, skipping...")
            return None, None, None, None, None

        logging.info(f"Processing meteor coordinates for {result[index][0]}")
        start_coords, end_coords = meteor_position
        meteor_img_path = result[index][0] + "/" + result[index][0].split("/")[-1] + ".jpg"

        if not meteor_img_path:
            logging.error(f"Meteor image not found {meteor_img_path}, skipping...")
            return None, None, None, None, None

        logging.info(f"Processing meteor image {meteor_img_path}")
        image = cv.imread(meteor_img_path, cv.IMREAD_GRAYSCALE)
        height, width = image.shape
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)
        quadrant_size = radius * 2 // 3

        quadrant_coordinates = get_quadrant_coordinates(center_x, center_y, radius, quadrant_size)
        start_location, end_location = determine_quadrant(start_coords, end_coords, quadrant_coordinates)

        return detection_type, start_location, end_location, result[index][3], result[index][2], image, start_coords, end_coords, quadrant_coordinates

    return "D", None, None, result[index][3], result[index][2], None, None, None, None


def handle_meteor_detection(result, writer, num):
    meteor_date = datetime.strptime(result[0][2], "%d.%m.%Y")
    meteor_month = meteor_date.strftime("%m")
    meteor_time = datetime.strptime(result[0][3], "%H:%M:%S")

    if meteor_month == "10":
        meteor_month = "A"
    elif meteor_month == "11":
        meteor_month = "B"
    elif meteor_month == "12":
        meteor_month = "C"

    meteor_number = str(num).zfill(3)
    num += 1

    detection_type, start_location, end_location, time, date, image1, start_coords1, end_coords1, coords1 = process_detection(result, 0)
    detection_type1, start_location1, end_location1, time1, date1, image2, start_coords2, end_coords2, coords2 = process_detection(result, 1)

    if detection_type is None or detection_type1 is None:
        return num

    meteor = meteor_date.strftime("%Y") + meteor_month + meteor_date.strftime("%d") + meteor_number

    writer.writerow(
        [
            meteor,
            date,
            time,
            detection_type,
            start_location,
            time1,
            detection_type1,
            end_location1,
            result[2],
        ]
    )
    logging.info(
        f"{meteor},{date},{time},{detection_type},{start_location},{time1},{detection_type1},{end_location1},{result[2]}"
    )

    if image1 is not None and image2 is not None:
        plot_images_with_grid(image1, image2, coords1, coords2, start_coords1, end_coords1, start_coords2, end_coords2)

    return num


def main():
    # Get the matching folders and non-matching folders
    comparison_results = compare.find_matching_folders()
    print(comparison_results)
    logging.debug(f"Comparison results: {comparison_results}")

    # TODO: Sort the unmatched and matched cases so that they are in order and numbered correctly
    # TODO: Remake the returned values from find_matching_folders to be only one array of tuples with all the data (match and non-match data together sorted by date and time)

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
        num = 0
        for result in comparison_results:
            logging.debug(result)
            # Process the meteor detection for each case
            num = handle_meteor_detection(result, writer, num)


if __name__ == "__main__":
    main()
