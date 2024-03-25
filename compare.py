import os
from modules import ConfigLoader


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
        path2 = os.path.join(self.home_dir, folder2)

        folders1 = [
            f for f in os.listdir(path1) if os.path.isdir(os.path.join(path1, f))
        ]
        folders2 = [
            f for f in os.listdir(path2) if os.path.isdir(os.path.join(path2, f))
        ]

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
