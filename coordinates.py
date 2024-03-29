from astropy import wcs
from astropy.io import fits

from meteor import Meteor

from main import AstrometryClient
import logging

def pixels_to_world(path: str, meteor: Meteor) -> list[list[float]]:
    """Convert pixel data to RA and Dec
    
    Args:
        path (str): WCS file path
        meteor (Meteor): Meteor instance containing path in pixel coordinates

    Returns:
        list[list[float]]: Meteor path in RA and Dec coordinates
    """

    # Load WCS from file
    hdulist = fits.open(path)
    w = wcs.WCS(hdulist[0].header)

    # Convert pixel coordinates to world coordinates
    world = []
    for point in meteor.pixels:
        world.append(w.pixel_to_world(point[0], point[1]))

    return world

def load_meteors(path: str) -> list[Meteor]:
    """Load meteor data from data file
    
    Args:
        path (str): data.txt file path

    Returns:
        list[Meteor]: list of Meteor instances
    """

    file = open(path, 'r').read().split('\n')

    # Cut off file and star data
    stars = int(file[8][16:])
    file = file[9+stars:]

    # Loop through meteors
    meteory = []
    for _ in range(int(file[0][18:])):
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

# TODO: Currently handles only a single meteor from observation, should handle all included in the data.txt file
# TODO: Separate downloading a WCS file into it's own function
def get_meteor_coordinates(client: AstrometryClient, img_path: str, data_path) -> list[list[float]]:
    """Do astrometry and return meteor path in RA and Dec
    
    Args:
        client (AstrometryClient): client to use for API communication
        img_path (str): Image to use for astrometry
        data_path (str): Observation data.txt path

    Returns:
        list[list[float]]: Meteor path in RA and Dec
    """
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
    client.get_wcs_file(submission_id, wcs_path)

    meteors = load_meteors(data_path)
    
    world = pixels_to_world(wcs_path, meteors[0])
    return world

if __name__ == '__main__':
    client = AstrometryClient()
    client.authenticate()

    print(get_meteor_coordinates(client, './data/2024-01-08-21-35-44.jpg', './data/data.txt'))
