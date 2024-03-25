import os
from time import sleep

from astrometrycli import AstrometryClient
from compare import FolderComparator

class MeteorComparator:
    def __init__(self, location_a="Kunzak", location_b="Ondrejov"):
        self.location_a = location_a
        self.location_b = location_b

    @staticmethod
    def make_img_path(folder):
        name = folder.split("/")[-1]
        if os.path.exists(os.path.join(folder, f"{name}.jpg")):
            return f"{folder}/{name}.jpg"
        else:
            return None

    def compare(self):
        comparator = FolderComparator().find_matching_folders(self.location_a, self.location_b)

        data = []

        # Get same meteors from two folders
        for folder in comparator:
            obs_a = AstrometryClient()
            obs_b = AstrometryClient()

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

            data.append((calibration_a["ra"], calibration_a["dec"], calibration_b["ra"], calibration_b["dec"]))

        return data


if __name__ == "__main__":
    comparator = MeteorComparator()
    print(comparator.compare())