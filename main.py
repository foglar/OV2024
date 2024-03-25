import json
import logging
import secret
import requests

# Enable or disable logging
logging.basicConfig(
    # filename="app.log",
    # filemode="a",
    format="%(asctime)s > %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.INFO,
)


class AstrometryClient:
    """Client for getting wcs data"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = None

    def authenticate(self):
        """Authenticate user and obtain session key"""
        response = requests.post(
            "http://nova.astrometry.net/api/login",
            data={"request-json": json.dumps({"apikey": self.api_key})},
        )
        data = response.json()
        if data["status"] == "success":
            self.session = data["session"]
            logging.info("Authentication successful.")
        else:
            logging.critical("Authentication failed.")

    def upload_image(self, image_path):
        """Upload image and return submission ID"""
        if not self.session:
            logging.warning("Please authenticate first.")
            return None

        files = {
            "request-json": (None, json.dumps({"session": self.session})),
            "file": (image_path, open(image_path, "rb"), "application/octet-stream"),
        }
        response = requests.post("http://nova.astrometry.net/api/upload", files=files)

        if response.status_code == 200:
            logging.info("Image upload successful.")
            return response.json()["subid"]
        else:
            logging.error("Image upload failed.")
            return None

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
    main()
