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

    def get_dir(self, num):
        # List all directories in the home directory
        dirs = [
            d
            for d in os.listdir(self.home_dir)
            if os.path.isdir(os.path.join(self.home_dir, d))
        ]

        dirs.sort()

        if num > len(dirs):
            raise ValueError(f"Directory {num} does not exist.")
        
        if len(dirs) > 2:
            logging.warning("More than two directories detected. Using the first two directories.")

        return dirs[num - 1]

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

    def find_matching_folders(self, folder1=None, folder2=None):
            """
            Finds matching subfolders between two given folders and also lists folders without matches.

            Args:
                folder1 (str): The name of the first folder.
                folder2 (str): The name of the second folder.

            Returns:
                tuple: A tuple containing a list of matching folder tuples and a list of non-matching folders.
            """
            if folder1 is None:
                logging.debug("No folder1 provided. Using the first directory.")
                folder1 = self.get_dir(1)
            if folder2 is None:
                logging.debug("No folder2 provided. Using the second directory.")
                folder2 = self.get_dir(2)

            path1 = os.path.join(self.home_dir, folder1)
            logging.info(f"Path 1: {path1}")
            path2 = os.path.join(self.home_dir, folder2)
            logging.info(f"Path 2: {path2}")

            folders1 = [f for f in os.listdir(path1) if os.path.isdir(os.path.join(path1, f))]
            logging.info(f"Subfolders in {folder1}: {folders1}")

            folders2 = [f for f in os.listdir(path2) if os.path.isdir(os.path.join(path2, f))]
            logging.info(f"Subfolders in {folder2}: {folders2}")

            matching_folders = []
            non_matching_folders = []

            for folder in folders1:
                matched = False
                for folder2 in folders2:
                    time_dif = self.compare_folders(folder, folder2)
                    if time_dif is not None:
                        matched = True
                        data_file_exists1 = os.path.exists(os.path.join(path1, folder, "data.txt"))
                        data_file_exists2 = os.path.exists(os.path.join(path2, folder2, "data.txt"))

                        date1 = self.parse_folder_name(folder)
                        date2 = self.parse_folder_name(folder2)

                        time1 = date1.strftime("%H:%M:%S")
                        time2 = date2.strftime("%H:%M:%S")
                        date1_str = date1.strftime("%d.%m.%Y")
                        date2_str = date2.strftime("%d.%m.%Y")

                        logging.info(f"Matching folders: {folder}, {folder2}")
                        matching_folders.append(
                            (
                                (os.path.join(path1, folder), data_file_exists1, date1_str, time1),
                                (os.path.join(path2, folder2), data_file_exists2, date2_str, time2),
                                time_dif,
                            )
                        )
                        break

                if not matched:
                    non_matching_folders.append(os.path.join(path1, folder))

            return matching_folders, non_matching_folders


if __name__ == "__main__":
    comparator = FolderComparator()
    matching_folders = comparator.find_matching_folders("Kunzak", "Ondrejov")
    print("Matching fireballs folders:")
    for folder in matching_folders:
        print(folder[0][0], folder[1][0])
        print("Time difference:", folder[2])
        print(
            "Number of meteors observed from both observatories:", len(matching_folders)
        )
