import os
import logging
import datetime
from modules import ConfigLoader

# Enable or disable logging
logging.basicConfig(
    # filename="app.log",
    # filemode="a",
    format="%(asctime)s > %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)

TIME_TOLERANCE = int(ConfigLoader().get_value_from_data("time_tolerance"))


class FolderComparator:
    """
    A class that compares two folders and finds matching subfolders.

    Attributes:
        config (ConfigLoader): An instance of the ConfigLoader class.
        home_dir (str): The home directory obtained from the ConfigLoader.

    Methods:
        find_matching_folders: Finds matching subfolders between two given folders.

    """

    def __init__(self):
        self.config = ConfigLoader()
        self.home_dir = self.config.get_home_dir()

    def parse_folder_name(self, folder):
        """
        Parses the folder name to extract the date and time information.

        Args:
            folder (str): The name of the folder.

        Returns:
            tuple: A tuple containing the date and time information.

        """

        folder = folder.split("-")

        year = folder[0]
        month = folder[1]
        day = folder[2]
        hour = folder[3]
        minute = folder[4]
        second = folder[5]

        return datetime.datetime(
            int(year), int(month), int(day), int(hour), int(minute), int(second)
        )

    def compare_folders(self, folder1, folder2):
        """
        Compares two folders based on their date and time information.

        Args:
            folder1 (str): The name of the first folder.
            folder2 (str): The name of the second folder.

        Returns:
            bool: True if the folders are within the time tolerance, False otherwise.

        """
        date1 = self.parse_folder_name(folder1)
        date2 = self.parse_folder_name(folder2)

        time_difference = abs(date1 - date2).total_seconds()
        logging.debug(
            f"Time difference: {time_difference}, Time tolerance: {TIME_TOLERANCE} - date1: {date1}, date2: {date2}"
        )

        if time_difference <= TIME_TOLERANCE:
            return time_difference
        else:
            return None

    def find_matching_folders(self, folder1, folder2):
        """
        Finds matching subfolders between two given folders.

        Args:
            folder1 (str): The name of the first folder.
            folder2 (str): The name of the second folder.

        Returns:
            list: A list of tuples containing the paths of matching subfolders, and whether the data.txt file exists in each folder.

        """
        path1 = os.path.join(self.home_dir, folder1)
        logging.info(f"Path 1: {path1}")
        path2 = os.path.join(self.home_dir, folder2)
        logging.info(f"Path 2: {path2}")

        folders1 = [
            f for f in os.listdir(path1) if os.path.isdir(os.path.join(path1, f))
        ]

        logging.info(f"Subfiles in {folder1}: {folders1}")

        folders2 = [
            f for f in os.listdir(path2) if os.path.isdir(os.path.join(path2, f))
        ]

        logging.info(f"Subfiles in {folder2}: {folders2}")

        matching_folders = []
        for folder in folders1:
            for folder2 in folders2:
                time_dif = self.compare_folders(folder, folder2)
                if time_dif is not None:

                    # Check if data.txt exists in both folders
                    data_file_exists = True
                    data_file_exists1 = True
                    if not os.path.exists(os.path.join(path1, folder, "data.txt")):
                        logging.info(f"Data.txt file not found in {folder}")
                        data_file_exists = False
                    elif not os.path.exists(os.path.join(path2, folder2, "data.txt")):
                        logging.info(f"Data.txt file not found in {folder2}")
                        data_file_exists1 = False

                    logging.info(f"Matching folders: {folder}, {folder2}")
                    matching_folders.append(
                        (
                            (os.path.join(path1, folder), data_file_exists),
                            (os.path.join(path2, folder2), data_file_exists1),
                            time_dif,
                        )
                    )

        return matching_folders


if __name__ == "__main__":
    comparator = FolderComparator()
    matching_folders = comparator.find_matching_folders("Kunzak", "Ondrejov")
    print("Matching fireballs folders:")
    for folder in matching_folders:
        print(folder[0][0], folder[1][0])
        print("Time difference:", folder[2])
    print("Number of meteors observed from both observatories:", len(matching_folders))
