import json
import logging
from time import sleep

import requests
from modules import ConfigLoader

# Enable or disable logging
logging.basicConfig(
    # filename="app.log",
    # filemode="a",
    format="%(asctime)s > %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)

class AstrometryClient:
    """Client for interacting with the Astrometry API.

    This class provides methods for authenticating the user, uploading images to the Astrometry.net API,
    checking the status of a job, retrieving calibration information, and downloading WCS files.

    Attributes:
        api_key (str): The API key used for authentication.
        session (str): The session key obtained after successful authentication.

    """

    def __init__(self):
        self.api_key = ConfigLoader().get_astrometry_key()
        self.session = None

    def authenticate(self):
        """Authenticate user and obtain session key.

        This method sends a POST request to the Astrometry API to authenticate the user
        using the provided API key. If the authentication is successful, the session key
        is stored in the `session` attribute of the object. Otherwise, an error message
        is logged.

        Returns:
            None
        """
        response = requests.post(
            "http://nova.astrometry.net/api/login",
            data={"request-json": json.dumps({"apikey": self.api_key})},
        )
        data = response.json()
        if data["status"] == "success":
            self.session = data["session"]
            logging.info("Authentication successful. Session key: %s", self.session)
        else:
            logging.critical("Authentication failed. Session key not obtained.")

    def upload_image(self, image_path):
        """Uploads an image to the Astrometry.net API and returns the submission ID.

        Args:
            image_path (str): The path to the image file to be uploaded.

        Returns:
            str: The submission ID of the uploaded image, or None if the upload failed.
        """
        if not self.session:
            logging.warning("Please authenticate first.")
            return None

        files = {
            "request-json": (None, json.dumps({"session": self.session})),
            "file": (image_path, open(image_path, "rb"), "application/octet-stream"),
        }
        response = requests.post("http://nova.astrometry.net/api/upload", files=files)

        logging.info("Status code: %s", response.json())
        if response.status_code == 200:
            logging.info(
                "Image upload successful. Submission ID: %s", response.json()["subid"]
            )
            return response.json()["subid"]
        else:
            logging.error("Image upload failed. Status code: %s", response.status_code)
            return None

    def check_job_status(self, job_id):
        """Check the status of a job.

        Args:
            job_id (int): The ID of the job to check.

        Returns:
            str: The status of the job, or None if there was an error.

        """
        if not self.session:
            logging.warning(f"Please authenticate first, Job_ID: {job_id}")
            return None

        url = f"http://nova.astrometry.net/api/jobs/{job_id}"
        response = requests.get(url)

        if response.status_code == 200:
            logging.info(f"Job status: {response.json().get("status")}")
            return response.json().get("status")
        else:
            logging.warning(
                f"Error checking job status. Status code: {response.status_code}"
            )
            return None

    def check_submission_status(self, submission_id):
        """Check the status of a submission.

        Args:
            submission_id (int): The ID of the submission to check.

        Returns:
            str: The status of the submission, or None if there was an error.

        """
        if not self.session:
            logging.warning("Please authenticate first, Job_ID: {submission_id}")
            return None

        url = f"http://nova.astrometry.net/api/submissions/{submission_id}"
        response = requests.get(url)

        if response.status_code == 200:
            logging.info(f"Submission status: {response.json}, Job_ID: {submission_id}")
            return response.json().get("jobs")
        else:
            logging.warning(
                f"Error checking submission status. Status code: {response.status_code}, Job_ID: {submission_id}"
            )
            return None
        
    def is_job_done(self, job_id):
        """Check if a job is done.

        Args:
            job_id (int): The ID of the job to check.

        Returns:
            bool: True if the job is done, False otherwise.

        """
        url = f"http://nova.astrometry.net/api/submissions/{job_id}"
        response = requests.get(url)
        if response.json().get("job_calibrations") != []:
            logging.info(f"Job is done, Job_ID: {job_id}")
            return True
        else:
            logging.info(f"Job is not done, Job_ID: {job_id}")
            return False

    def get_calibration(self, job_id):
        """Get calibration information for a job.

        Args:
            job_id (int): The ID of the job for which to retrieve calibration information.

        Returns:
            dict or None: A dictionary containing the calibration information if successful,
            None otherwise.

        Raises:
            None

        """
        if not self.session:
            logging.warning(f"Please authenticate first, Job_ID: {job_id}")
            return None

        url = f"http://nova.astrometry.net/api/jobs/{job_id}/calibration/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(
                f"Error getting calibration information. Status code: {response.status_code}, Job_ID: {job_id}"
            )
            return None

    def get_wcs_file(self, job_id, save_path):
        """
        Get the URL of the WCS (World Coordinate System) file for a given job ID
        and download it to the specified save path.

        Args:
            job_id (int): The ID of the job.
            save_path (str): The path where the downloaded WCS file will be saved.

        Returns:
            str: The URL of the WCS file if successful, None otherwise.
        """
        if not self.session:
            logging.warning(f"Please authenticate first, Job_ID: {job_id}")
            return None

        url = f"http://nova.astrometry.net/wcs_file/{job_id}"
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            logging.info(f"WCS file downloaded successfully, Job_ID: {job_id}")
            return response.url
        else:
            logging.error(
                f"Error getting WCS file. Status code: {response.status_code}, Job_ID: {job_id}"
            )
            return None


def main():
    client = AstrometryClient()
    client.authenticate()
    submission_id = client.upload_image("./data/2024-01-08-21-35-44.jpg")

    if not submission_id:
        logging.error("Image upload failed.")
        return

    logging.info("Submission ID: %s", submission_id)

    status = client.check_job_status(submission_id)
    if not status:
        logging.warning(f"Failed to check job status, Job_ID: {submission_id}")
        return

    logging.info("Job status: %s", status)

    if status != "success":
        logging.warning(f"Job is not successful, Job_ID: {submission_id}. Aborting...")
        return
    
    # Check if job is done
    timeout = ConfigLoader().get_value_from_data("timeout")
    for i in range(10):
        status = client.is_job_done(submission_id)
        if status == True:
            break
        sleep(timeout)

        if i == 9:
            raise Exception(f"Job status not successful after {timeout*10} seconds. Aborting...")


    # Check submission status
    # while client.check_submission_status(
    #     submission_id
    # ) == [] or client.check_submission_status(submission_id) == [None]:
    #     sleep(ConfigLoader().get_value_from_data("timeout"))

    wcs_file_url = client.get_wcs_file(submission_id, "./test.wcs")
    if not wcs_file_url:
        logging.error("Failed to get WCS file URL.")
        return

    logging.info("WCS file URL: %s", wcs_file_url)

    calibration_info = client.get_calibration(submission_id)
    if calibration_info:
        print("Calibration information:", calibration_info)
    else:
        print("Failed to retrieve calibration information.")


if __name__ == "__main__":
    main()
