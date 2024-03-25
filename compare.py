import os
from modules import ConfigLoader


class FolderComparator:
    def __init__(self):
        self.config = ConfigLoader()
        self.home_dir = self.config.get_home_dir()

    def find_matching_folders(self, folder1, folder2):
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
