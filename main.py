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
            for i in range(10):
                status_a = obs_a.is_job_done(job_id_a)
                status_b = obs_b.is_job_done(job_id_b)

                if status_a == True and status_b == True:
                    break
                
                logging.info(f"Job status after {timeout*(i+1)} seconds: Status of submission A: {status_a}, Status of submission B: {status_b}")
                sleep(timeout)

                if i == 9:
                    raise Exception(f"Job status not successful after {timeout*10} seconds. Status of submission A: {status_a}, Status of submission B: {status_b}. Aborting...")

            calibration_a = obs_a.get_calibration(job_id_a)
            calibration_b = obs_b.get_calibration(job_id_b)

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


def main():
    client = AstrometryClient(api_key=ConfigLoader.get_astrometry_key)
    client.authenticate()
    submission_id = client.upload_image("./data/2024-01-08-21-35-44.jpg")

    if not submission_id:
        logging.error("Image upload failed.")
        return

    logging.info("Submission ID: %s", submission_id)

    status = client.check_job_status(submission_id)
    if not status:
        logging.warning("Failed to check job status.")
        return

    logging.info("Job status: %s", status)

    if status != "success":
        logging.warning("Job is not successful. Aborting...")
        return
    
    timeout = ConfigLoader().get_value_from_data("timeout")
    for i in range(10):
        status = client.check_job_status(submission_id)
        if status == True:
            break
        sleep(timeout)

        if i == 9:
            logging.error(f"Job status not successful after {10*timeout} seconds. Aborting...")
            raise Exception(f"Job status not successful after {timeout*10} seconds. Aborting...")
        

    client.get_wcs_file(submission_id, "./test.wcs")

    calibration_info = client.get_calibration(submission_id)
    if calibration_info:
        print("Calibration information:", calibration_info)
    else:
        print("Failed to retrieve calibration information.")


if __name__ == "__main__":
    meteors = MeteorsList()
    ra_dec_list = meteors.compare()
