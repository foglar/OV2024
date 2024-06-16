import csv
import logging

import cv2 as cv
import numpy as np

# Should be always before local imports
logging.basicConfig(
    format="%(asctime)s > %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)

from datetime import datetime
from matplotlib import pyplot as plt
from os import path

from compare import FolderComparator
from modules import ConfigLoader
from coordinates import get_meteor_start_end_coordinates

HOME_DIR = ConfigLoader().get_home_dir()
compare = FolderComparator()


# TODO: Append name of observatory to the meteor array
# TODO: Add the checks of data in each function
# TODO: Simplify the code, ensure that its readable and understandable
# TODO: Add docstrings to the functions
# TODO: Change the look of the plots from config file
# TODO: JSON format instead of list


class post_processing:
    """Post processing class for meteor analysis and graph plotting"""

    def __init__(self, path=None):
        """Initializes the post processing class
        Creates a list of processed meteors
        [meteor_id, date, time, time1, detection_type1, detection_type2, quadrant1, quadrant2, time_difference]
        """

        if path is None:
            meteors_list = compare.find_matching_folders()
            path = HOME_DIR
        else:
            folders = compare.get_dir(2, path)
            meteors_list = compare.find_matching_folders(folders)

        OUTPUT_FILNAME = ConfigLoader().get_value_from_data(
            "output_file", "post_processing"
        )
        if OUTPUT_FILNAME:
            self.output_file = f"{path}/{OUTPUT_FILNAME}"
        else:
            self.output_file = f"{path}/overview.csv"

        processed_meteors = []
        id = 0
        for meteor_object in meteors_list:
            # Meteor ID
            processed_meteors.append(self._parse_meteor_id_time(meteor_object, id))
            id += 1

            # Detection type
            # For each meteor, check if the data.txt file exists in the folder
            processed_meteors[-1].append(self._parse_detection_type(meteor_object, 0))
            processed_meteors[-1].append(self._parse_detection_type(meteor_object, 1))

            # Meteor start and end coordinates
            if meteor_object[0] is not None:
                meteor_position = get_meteor_start_end_coordinates(
                    f"{meteor_object[0][0]}/data.txt"
                )

            if meteor_object[1] is not None:
                meteor_position1 = get_meteor_start_end_coordinates(
                    f"{meteor_object[1][0]}/data.txt"
                )

            # Meteor quadrants

            # First meteor
            if meteor_object[0] is not None:
                image_path = (
                    meteor_object[0][0]
                    + "/"
                    + meteor_object[0][0].split("/")[-1]
                    + ".jpg"
                )

                logging.debug(f"Processing meteor {meteor_object[0][0]}")
                quad_A = self.get_meteor_quadrant_position(meteor_position, image_path)
                processed_meteors[-1].append(quad_A)
            else:
                processed_meteors[-1].append(None)

            # Second meteor
            if meteor_object[1] is not None:
                image_path1 = (
                    meteor_object[1][0]
                    + "/"
                    + meteor_object[1][0].split("/")[-1]
                    + ".jpg"
                )

                logging.debug(f"Processing meteor {meteor_object[1][0]}")
                quad_B = self.get_meteor_quadrant_position(
                    meteor_position1, image_path1
                )
                processed_meteors[-1].append(quad_B)
            else:
                processed_meteors[-1].append(None)

            # Time difference
            if meteor_object[2] is not None:
                processed_meteors[-1].append(meteor_object[2])

            # Path to images
            processed_meteors[-1].append(image_path)
            processed_meteors[-1].append(image_path1)

            # Coordinates
            processed_meteors[-1].append(meteor_position)
            processed_meteors[-1].append(meteor_position1)

        self.meteor_data_table = processed_meteors
        logging.debug(processed_meteors)
        logging.info("Post processing done.")

    def _parse_meteor_id_time(self, meteor, num):
        """Parse meteor ID and time from meteor data"""

        meteor_data = meteor[0] if meteor[0] is not None else meteor[1]
        meteor_date = datetime.strptime(meteor_data[2], "%d.%m.%Y")
        meteor_month = meteor_date.strftime("%m")
        meteor_time = datetime.strptime(meteor_data[3], "%H:%M:%S")

        if meteor[1] is not None:
            meteor_time1 = datetime.strptime(meteor[1][3], "%H:%M:%S")
        else:
            meteor_time1 = None

        if meteor_month == "10":
            meteor_month = "A"
        elif meteor_month == "11":
            meteor_month = "B"
        elif meteor_month == "12":
            meteor_month = "C"

        meteor_number = str(num).zfill(3)
        meteor_id = (
            meteor_date.strftime("%Y")
            + meteor_month
            + meteor_date.strftime("%d")
            + meteor_number
        )
        return [
            meteor_id,
            meteor_date.strftime("%Y-%m-%d"),
            meteor_time.strftime("%H:%M:%S"),
            meteor_time1.strftime("%H:%M:%S") if meteor_time1 is not None else None,
        ]

    def _parse_detection_type(self, meteor_object, index):
        """Parse detection type from meteor data
        Args:
            meteor_object: meteor data
            index: index of the meteor object

        Returns:
            detection_type: detection type of the meteor
        """
        # TODO: Revise
        if meteor_object[0] is not None:
            if path.exists(f"{meteor_object[0][index]}/data.txt"):
                return "MA"
            else:
                return "D"
        else:
            return "N"

    def get_meteor_quadrant_position(self, meteor_coords, meteor_image):
        """Get the quadrant of the meteor
        Args:
            meteor_coords: coordinates of the meteor
            meteor_image: path to the image

        Returns:
            start_location: quadrant of the start coordinates
            end_location: quadrant of the end coordinates
        """
        img = cv.imread(meteor_image, cv.IMREAD_GRAYSCALE)
        height, width = img.shape
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)
        quadrant_size = radius * 2 // 3

        quadrant_coordinates = self.get_quadrant_coordinates(
            center_x, center_y, radius, quadrant_size
        )
        start_location, end_location = self.determine_meteor_quadrant(
            meteor_coords[0], meteor_coords[1], quadrant_coordinates
        )

        return start_location, end_location

    def get_quadrant_coordinates(self, center_x, center_y, radius, quadrant_size):
        """Get the coordinates of the quadrants of the image
        Args:
            center_x: x coordinate of the center of the image
            center_y: y coordinate of the center of the image
            radius: radius of the image
            quadrant_size: size of the quadrant

        Returns:
            coordinates: list of quadrant coordinates
        """
        coordinates = []
        for i in range(3):
            for j in range(3):
                x1 = center_x - radius + j * quadrant_size
                y1 = center_y - radius + i * quadrant_size
                x2 = x1 + quadrant_size
                y2 = y1 + quadrant_size
                coordinates.append(((x1, y1), (x2, y2)))
                logging.debug(f"Quadrant {i*3+j+1} coordinates: {((x1, y1), (x2, y2))}")
        return coordinates

    def determine_meteor_quadrant(self, start_coords, end_coords, quadrant_coordinates):
        """Determine the quadrant of the meteor
        Args:
            start_coords: start coordinates of the meteor
            end_coords: end coordinates of the meteor
            quadrant_coordinates: list of quadrant coordinates

        Returns:
            start_location: quadrant of the start coordinates
            end_location: quadrant of the end coordinates
        """
        start_location = end_location = None
        for i, (top_left, bottom_right) in enumerate(quadrant_coordinates):
            if (
                top_left[0] <= start_coords[0] <= bottom_right[0]
                and top_left[1] <= start_coords[1] <= bottom_right[1]
            ):
                start_location = i + 1
                logging.debug(f"The meteor first point from quadrant {i+1}")

            if (
                top_left[0] <= end_coords[0] <= bottom_right[0]
                and top_left[1] <= end_coords[1] <= bottom_right[1]
            ):
                end_location = i + 1
                logging.debug(f"The meteor second point from quadrant {i+1}")

            if start_location and end_location:
                break

        return start_location, end_location

    def _reorder_meteor_data(self, meteor_data):
        """Reorder the meteor data for writing to the CSV file
        Args:
            meteor_data: list of meteor data

        Returns:
            processed_meteors: list of reordered meteor data
        """
        processed_meteors = []

        for meteor in meteor_data:
            # Check if meteor is matched or unmatched
            if meteor[7] != None:
                reordered_meteor = [
                    meteor[0],  # Meteor
                    meteor[1],  # Date
                    meteor[2],  # Time
                    meteor[4],  # Detection Type
                    meteor[6],  # Quadrant
                    meteor[3],  # Time1
                    meteor[4],  # Detection Type1
                    meteor[6],  # Quadrant1
                    meteor[7],  # Time Difference
                ]
            else:
                reordered_meteor = [
                    meteor[0],  # Meteor
                    meteor[1],  # Date
                    meteor[2],  # Time
                    meteor[4],  # Detection Type
                    meteor[6],  # Quadrant
                ]
            processed_meteors.append(reordered_meteor)

        return processed_meteors

    def _create_meteor_figure(self, ax, image_path, coordinates):
        """Create a figure of the meteor with the coordinates on the image
        Args:
            ax: matplotlib axis
            image_path: path to the image
            coordinates: start and end coordinates of the meteor

        Returns:
            ax: matplotlib axis with the meteor plotted on the image"""
        image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
        height, width = image.shape
        center_x, center_y = width // 2, height // 2
        radius = min(center_x, center_y)
        quadrant_size = radius * 2 // 3

        observatory = image_path.split("/")[-3]
        ax.set_title(f"{observatory} - {image_path.split('/')[-1]}")

        # Draw the grid
        for i in range(1, 3):
            ax.plot(
                [center_x - radius, center_x + radius],
                [
                    center_y - radius + i * quadrant_size,
                    center_y - radius + i * quadrant_size,
                ],
                color="blue",
            )
            ax.plot(
                [
                    center_x - radius + i * quadrant_size,
                    center_x - radius + i * quadrant_size,
                ],
                [center_y - radius, center_y + radius],
                color="blue",
            )
        # Best cmap for the image is grey, hot, bone
        ax.imshow(image, cmap="grey")

        # Draw the meteor path
        ax.plot(
            [coordinates[0][0], coordinates[1][0]],
            [coordinates[0][1], coordinates[1][1]],
            color="yellow",
            label="Meteor",
        )

        return ax

    def plot_meteors(self, images_path, first_coords, second_coords=None):
        """Plot the meteor on the image
        Args:
            images_path: list of paths to the images [first_image, second_image]
            first_coords: start coordinates of the meteor [x, y]
            second_coords: end coordinates of the meteor [x, y]

        Returns:
            None"""
        # If matched meteor plot both images
        # If unmatched meteor plot only one image
        try:
            THEME = ConfigLoader().get_value_from_data("plt_style", "post_processing")
        except KeyError:
            THEME = "dark"
            logging.warning("No theme specified in the config file. Using dark theme.")

        if THEME == "light":
            plt.style.use("default")
        elif THEME == "dark":
            plt.style.use("dark_background")
        else:
            plt.style.use("dark_background")
            logging.warning("Invalid theme specified. Using dark theme.")

        if type(images_path) is list:
            fig, axes = plt.subplots(1, 2, figsize=(16, 8))

            self._create_meteor_figure(axes[0], images_path[0], first_coords)
            self._create_meteor_figure(axes[1], images_path[1], second_coords)

            leg = axes[0].legend(fancybox=True, shadow=True)
            leg = axes[1].legend(fancybox=True, shadow=True)

        else:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
            self._create_meteor_figure(ax, images_path, first_coords)
            leg = ax.legend(fancybox=True, shadow=True)

        #pickradius = 5
        # TODO: Add ability to toggle the meteor path on and off

        plt.show()

    def plot_all_meteors(self):
        # Plot all meteors in the list
        meteors = self.meteor_data_table
        logging.info(f"Plotting {len(meteors)} meteors.")
        for meteor in meteors:
            self.plot_meteors([meteor[-4], meteor[-3]], meteor[-2], meteor[-1])

    def write_to_csv(self, data=None):
        # Format the data to be written to the CSV file
        if data is None:
            data = self.meteor_data_table
            logging.warning("No data provided. Using the data from the class.")

        data = self._reorder_meteor_data(data)

        with open(self.output_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Meteor",
                    "Date",
                    "Time",
                    "Detection Type",
                    "Quadrant",
                    "Time",
                    "Detection Type",
                    "Quadrant",
                ]
            )
            writer.writerows(data)


if __name__ == "__main__":
    post_processing(path=HOME_DIR)
    post_processing().write_to_csv()
    post_processing().plot_all_meteors()
