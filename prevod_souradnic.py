# Load the WCS information from a fits header, and use it
# to convert pixel coordinates to world coordinates.

import numpy as np

from astropy import wcs
from astropy.io import fits

from meteor import Meteor

from main import AstrometryClient
import secret
import logging

def pixels_to_world(path: str, pixels: Meteor) -> list[list[float]]:
    """Convert pixel data to right ascension and declination"""
    # Load WCS from file
    hdulist = fits.open(path)
    w = wcs.WCS(hdulist[0].header)

    # Convert pixel coordinates to world coordinates
    world = []
    for point in pixels.pixels:
        world.append(w.pixel_to_world(point[0], point[1]))

    return world

def load_pixels(path: str) -> list[Meteor]:
    """Load meteor data from data file"""
    file = open(path, 'r').read().split('\n')

    # Cut off file and star data
    stars = int(file[8][16:])
    file = file[9+stars:]

    # Loop through meteors
    meteory = []
    for i in range(int(file[0][18:])):
        # Cut off unnecessary meteor data
        file = file[2:]
        
        # Loop through meteor positions
        pixels = []
        j = 1
        while file[j].startswith(' frame'):
            data = file[j].split(' ')
            pixels.append([float(data[6]), float(data[11])])
            j += 1

        meteory.append(Meteor(pixels))

        file = file[j:]

    return meteory

def get_meteor_coordinates(client: AstrometryClient, img_path: str, data_path) -> list[list[float]]:
    """Do astrometry and return meteor path in RA and Dec"""
    submission_id = client.upload_image(img_path)

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

    # Get wcs file and convert pixel coordinates to world coordinates
    wcs_path = 'calibration.wcs'
    client.download_wcs_file(submission_id, wcs_path)

    meteors = load_pixels(data_path)
    
    world = pixels_to_world(wcs_path, meteors[0])
    return world

if __name__ == '__main__':
    client = AstrometryClient(api_key=secret.A_TOKEN)
    client.authenticate()

    print(get_meteor_coordinates(client, './data/2024-01-08-21-35-44.jpg', './data/data.txt'))
