import os
import logging
from time import sleep

from astrometry import AstrometryClient
from compare import FolderComparator


class MeteorComparator:
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

            for i in range(10):
                status_a = obs_a.check_job_status(job_id_a)
                status_b = obs_b.check_job_status(job_id_b)

                if status_a == "success" and status_b == "success":
                    break

                sleep(0.5)

                if i == 9:
                    raise Exception("Job status not successful")

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
    def check_job_status(self, job_id):
        """Check status of a job"""
        if not self.session:
            logging.warning("Please authenticate first.")
            return None

        url = f"http://nova.astrometry.net/api/jobs/{job_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("status")
        else:
            logging.warning(
                f"Error checking job status. Status code: {response.status_code}"
            )
            return None

    def get_calibration(self, job_id):
        """Get calibration information for a job"""
        if not self.session:
            logging.warning("Please authenticate first.")
            return None

        url = f"http://nova.astrometry.net/api/jobs/{job_id}/calibration/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(
                f"Error getting calibration information. Status code: {response.status_code}"
            )
            return None

    def download_wcs_file(self, job_id, save_path):
        """Download WCS file from given URL and save to disk"""
        if not self.session:
            logging.warning("Please authenticate first.")
            return

        url = f"http://nova.astrometry.net/wcs_file/{job_id}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            logging.info("WCS file downloaded successfully.")
        else:
            logging.error("Failed to download WCS file.")


def main():
    client = AstrometryClient(api_key=secret.A_TOKEN)
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

    client.download_wcs_file(submission_id, "./test.wcs")

    calibration_info = client.get_calibration(submission_id)
    if calibration_info:
        print("Calibration information:", calibration_info)
    else:
        print("Failed to retrieve calibration information.")


if __name__ == "__main__":
    comparator = MeteorComparator()
    ra_dec_list = comparator.compare()
