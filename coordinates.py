from astropy import wcs
from astropy.io import fits
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
import astropy.units as u

from main import AstrometryClient
import logging
import re
import os

from time import sleep
from modules import ConfigLoader

def get_meteor_start_end_coordinates(path: str) -> list[float]:
    """Get meteor coordinates from data.txt file
    
    Args:
        path (str): data.txt file path

    Returns:
        list[float]: Meteor coordinates
    """

    if not os.path.exists(path):
        logging.error(f"File {path} does not exist.")
        return None

    file = open(path, 'r').read().split('\n')

    for line in file:
        if line.startswith("#Meteor 1:"):
            match = re.search(r'start \(([^)]+)\) end \(([^)]+)\)', line)
            if match:
                start = tuple(map(float, match.group(1).split(', ')))
                end = tuple(map(float, match.group(2).split(', ')))
                return start, end
    
    # TODO: Check this function and make sure regex is working correctly
    # Consider creating a separated file for parsing data.txt
    return None, None  # Return the coordinates of the meteor
    

def pixels_to_world(path: str, meteor: list[list[float]]) -> list[list[float]]:
    """Convert pixel data to RA and Dec
    
    Args:
        path (str): WCS file path
        meteor (list[list[float]]): Meteor path in pixel coordinates

    Returns:
        list[list[float]]: Meteor path in RA and Dec coordinates
    """

    # Load WCS from file
    hdulist = fits.open(path)
    w = wcs.WCS(hdulist[0].header)

    # Convert pixel coordinates to world coordinates
    world = []
    for point in meteor:
        skyCoord = w.pixel_to_world(point[0], point[1])
        world.append([skyCoord.ra.degree,skyCoord.dec.degree])

    return world

def world_to_pixel(path: str, meteor: list[list[float]]):
    """Convert RA and Dec to pixel coordinates
    
    Args:
        path (str): WCS file path
        meteor (list[list[float]]): Meteor path in RA and Dec

    Returns:
        list[list[float]]: Meteor path in pixel coordinates
    """

    # Load WCS from file
    hdulist = fits.open(path)
    w = wcs.WCS(hdulist[0].header)

    pixels = []
    for point in meteor:
        skyCoord = SkyCoord(ra=point[0], dec=point[1], unit='deg', frame='fk5')
        pixels.append(w.world_to_pixel(skyCoord))

    return pixels

def world_to_altaz(ra: float, dec: float, station) -> list[float]:
    """Converts RA and Dec to Alt and Az.
    
    Args:
        ra (float): Right ascension
        dec (float): Declination
        station: Dict containing information about the station
        
    Returns:
        list[float]: Altitude and azimuth of the object
    """

    skyCoord = SkyCoord(ra=ra, dec=dec, unit='deg', frame='fk5')
    time = Time(time) - u.hour * station['time_zone']
    observatory = EarthLocation(lat=station['lat'] * u.deg, lon=station['lon'] * u.deg, height=station['height'] * u.m)

    altaz = skyCoord.transform_to(AltAz(obstime=time, location=observatory))
    return [altaz.alt.degree, altaz.az.degree]

def load_meteors(path: str) -> list[list[list[float]]]:
    """Load meteor data from data file
    
    Args:
        path (str): data.txt file path

    Returns:
        list[lsit[list[float]]]: List of meteor paths
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

        meteory.append(pixels)
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

    job_id = None
    timeout = ConfigLoader().get_value_from_data("timeout")
    for i in range(10):
        status = client.is_job_done(submission_id)
        if status != False:
            job_id = status[0][0]
            break
        sleep(timeout)

        if i == 9:
            logging.error(f"Job status not successful after {10*timeout} seconds. Aborting...")
            raise Exception(f"Job status not successful after {timeout*10} seconds. Aborting...")

    # Get wcs file and convert pixel coordinates to world coordinates
    wcs_path = 'calibration.wcs'
    client.get_wcs_file(job_id, wcs_path)

    meteors = load_meteors(data_path)
    
    world = pixels_to_world(wcs_path, meteors[0])
    return world

if __name__ == '__main__':
    client = AstrometryClient()
    client.authenticate()

    print(get_meteor_coordinates(client, './data/2024-01-08-21-35-44.jpg', './data/data.txt'))
