import os
import logging
from time import sleep

from astrometry import AstrometryClient
from compare import FolderComparator
from modules import ConfigLoader


class MeteorsList:
    """
    A class that compares meteor data from two locations.

    Attributes:
        location_a (str): The name of the first location.
        location_b (str): The name of the second location.
    """

    def __init__(self, location_a="Kunzak", location_b="Ondrejov"):
        """
        Initializes a new instance of the MeteorComparator class.

        Args:
            location_a (str, optional): The name of the first location. Defaults to "Kunzak".
            location_b (str, optional): The name of the second location. Defaults to "Ondrejov".
        """
        self.location_a = location_a
        self.location_b = location_b

    @staticmethod
    def make_img_path(folder):
        """
        Creates the image path for a given folder.

        Args:
            folder (str): The folder path.

        Returns:
            str: The image path.
        """
        name = folder.split("/")[-1]
        if os.path.exists(os.path.join(folder, f"{name}.jpg")):
            logging.info(f"Image path: {folder}/{name}.jpg")
            return f"{folder}/{name}.jpg"
        else:
            logging.error(f"Image not found in {folder}")
            return None

    def compare(self):
        """
        Compares meteor data from two locations.

        Returns:
            list: A list of tuples containing the right ascension and declination data for each meteor from both locations. In the format (ra_a, dec_a, ra_b, dec_b) for each meteor.
        """
        comparator = FolderComparator().find_matching_folders(
            self.location_a, self.location_b
        )

        # Remove time difference and data.txt file existence
        comparator = [(item[0][0], item[1][0]) for item in comparator]

        data = []

        # Get same meteors from two folders
        for folder in comparator:
            obs_a = AstrometryClient()
            obs_b = AstrometryClient()

            logging.info(f"Comparing {folder[0]} and {folder[1]}")

            obs_a.authenticate()
            obs_b.authenticate()

            if not obs_a.session or not obs_b.session:
                raise Exception("Authentication failed")

            job_id_a = obs_a.upload_image(self.make_img_path(folder[0]))
            job_id_b = obs_b.upload_image(self.make_img_path(folder[1]))
            
            timeout = ConfigLoader().get_value_from_data("timeout")
            for i in range(51):
                status_a = obs_a.is_job_done(job_id_a)
                status_b = obs_b.is_job_done(job_id_b)

                if status_a != False and status_b != False:
                    break
                
                logging.info(f"Job status after {timeout*(i+1)} seconds: Status of submission A: {status_a}, Status of submission B: {status_b}")
                sleep(timeout)

                if i == 50:
                    raise Exception(f"Job status not successful after {timeout*50} seconds. Status of submission A: {status_a}, Status of submission B: {status_b}. Aborting...")
            
            calibration_a = obs_a.get_calibration(status_a[0][0])
            calibration_b = obs_b.get_calibration(status_b[0][0])

            logging.info(f"Calibration A: {calibration_a}")
            logging.info(f"Calibration B: {calibration_b}")

            data.append(
                (
                    calibration_a["ra"],
                    calibration_a["dec"],
                    calibration_b["ra"],
                    calibration_b["dec"],
                )
            )

        logging.info(f"Ra and Dec data for each meteor from both stations: {data}")
        return data

if __name__ == "__main__":
    meteors = MeteorsList()
    ra_dec_list = meteors.compare()
    print(ra_dec_list)
