import os
import logging
from modules import ConfigLoader

# Enable or disable logging
logging.basicConfig(
    # filename="app.log",
    # filemode="a",
    format="%(asctime)s > %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)
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

    def find_matching_folders(self, folder1, folder2):
        """
        Finds matching subfolders between two given folders.

        Args:
            folder1 (str): The name of the first folder.
            folder2 (str): The name of the second folder.

        Returns:
            list: A list of tuples containing the paths of matching subfolders.

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
            if folder in folders2:
                matching_folders.append(
                    (os.path.join(path1, folder), os.path.join(path2, folder))
                )

        return matching_folders


if __name__ == "__main__":
    comparator = FolderComparator()
    matching_folders = comparator.find_matching_folders("Kunzak", "Ondrejov")
    print("Matching fireballs folders:", matching_folders)
    print("Number of meteors observed from both observatories:", len(matching_folders))
