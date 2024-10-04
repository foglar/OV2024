from astropy import wcs
from astropy.io import fits
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
import astropy.units as u

from main import AstrometryClient
import logging

from time import sleep
from modules import ConfigLoader

from station import Station

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

def world_to_altaz(ra: float, dec: float, station: Station, time: Time) -> list[float]:
    """Converts RA and Dec to Alt and Az.
    
    Args:
        ra (float): Right ascension
        dec (float): Declination
        station (Station): Information about the station
        
    Returns:
        list[float]: Altitude and azimuth of the object
    """

    skyCoord = SkyCoord(ra=ra, dec=dec, unit='deg', frame='fk5')
    time = time - u.hour * station.time_zone
    observatory = EarthLocation(lat=station.lat * u.deg, lon=station.lon * u.deg, height=station.height * u.m)

    altaz = skyCoord.transform_to(AltAz(obstime=time, location=observatory))
    return altaz.alt.degree, altaz.az.degree

def altaz_to_world(alt: float, az: float, station: Station, time: Time) -> list[float]:
    """Converts Alt and Az to RA and Dec
    
    Args:
        alt (float): Altitude
        az (float): Azimuth
        station (Station): Information about the station

    Returns:
        list[float]: Right ascension and declination of object
    """

    time = time - u.hour * station.time_zone
    observatory = EarthLocation(lat=station.lat * u.deg, lon=station.lon * u.deg, height=station.height * u.m)
    altaz = SkyCoord(alt=alt * u.deg, az=az * u.deg, frame='altaz', obstime=time, location=observatory)

    sky_coord = altaz.icrs
    return sky_coord.ra.degree, sky_coord.dec.degree

def geocentric_to_geodetic(location: list[float]) -> list[float]:
    """Converts the vector X, Y, Z to latitude, longitude and height
    
    Args:
        location (list[float]): Values X, Y and Z

    Returns:
        list[float]: latitude, longitude and height values
    """

    X, Y, Z = location
    return [x.value for x in EarthLocation.from_geocentric(X, Y, Z, u.m).geodetic]

def geodetic_to_geocentric(location: dict) -> list[float]:
    """Calculates geocentric vector (X, Y, Z) according to equations 7 and 8
    
    Args:
        location (dict): lat, lon, height of location

    Returns:
        list[float]: vector (X, Y, Z)
    """

    return tuple([x.value for x in EarthLocation.from_geodetic(location['lon'], location['lat'], location['height']).geocentric])

def load_meteors(path: str) -> list[list[list[float]]]:
    """Load meteor data from data file
    
    Args:
        path (str): data.txt file path

    Returns:
        list[list[list[float]]]: List of meteor paths
    """

    file = open(path, 'r').read().split('\n')

    # Cut off file and star data
    stars = int(file[8][16:])
    file = file[9+stars:]

    # Loop through meteors
    meteory = []
    casy = []
    for _ in range(int(file[0][18:])):
        # Cut off file
        file = file[1:]

        # Load meteor start and end time
        data = file[0].split(' ')

        start = float(data[-4][:-1])
        end = float(data[-2][:-1])

        duration = end - start

        # Cut off file
        file = file[1:]
        
        # Loop through meteor positions
        pixels = []
        frames = []
        j = 1
        while file[j].startswith(' frame'):
            data = file[j].split(' ')
            frames.append(int(data[3]))
            pixels.append([float(data[6]), float(data[11])])
            j += 1

        # Convert frames to time
        first = frames[0]
        count = abs(frames[-1] - frames[0])
        
        for i in range(len(frames)):
            frames[i] = (frames[i] - first) * (duration / count)

        meteory.append(pixels)
        casy.append(frames)
        file = file[j:]

    return meteory, casy

def download_wcs_file(client: AstrometryClient, img_path: str, wcs_path: str = 'calibration.wcs') -> bool:
    """Try to get astrometry from an image from nova.astrometry.net
    
    Args:
        img_path (str): Image to use for astrometry

    Returns:
        int: job_id of the astrometry, None if unsuccessful
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
            # Astrometry timed out, return False
            logging.error(f"Job status not successful after {10*timeout} seconds. Aborting...")
            return None

    # Download the resulting WCS file
    client.get_wcs_file(job_id, wcs_path)

    return job_id

def get_meteor_coordinates_fixed(data_path: str, station: Station, time: Time) -> list[list[float]]:
    meteors, times = load_meteors(data_path)
    world = pixels_to_world(station.wcs_path, meteors[0])
        
    for i in range(len(world)):
        ra, dec = world[i]
        alt, az = world_to_altaz(ra, dec, station, station.wcs_time)
        world[i] = altaz_to_world(alt, az, station, time)

    # Merge coordinate and time data
    for i in range(len(world)):
        world[i] = list(world[i]) + [times[0][i]]

    return world

def get_meteor_coordinates(client: AstrometryClient, img_path: str, data_path: str, station: Station, time: Time, job_id: int = None) -> list[list[float]]:
    """Do astrometry and return meteor path in RA and Dec with time marks
    
    Args:
        client (AstrometryClient): client to use for API communication
        img_path (str): Image to use for astrometry
        data_path (str): Observation data.txt path
        station (Station): Station to use for backup astrometry
        time (Time): Time to use for fixed camera alignment

    Returns:
        list[list[float]]: Meteor path in RA and Dec and seconds
    """
    world, times = None, None
    # Check, if images have astrometry
    if job_id == None:
        # If no, try doing astrometry on the image
        job_id = download_wcs_file(client, img_path)
    else:
        # If yes, download the WCS file
        client.get_wcs_file(job_id, 'calibration.wcs')
    
    if job_id:
        # Astrometry successful, use it to calculate meteor coordinates
        meteors, times = load_meteors(data_path)
        world = pixels_to_world('calibration.wcs', meteors[0])

        # Merge coordinate and time data
        for i in range(len(world)):
            world[i] = list(world[i]) + [times[0][i]]
    else:
        # Astrometry unsuccessful, use the saved WCS to calculate
        world = get_meteor_coordinates_fixed(data_path, station, time)

    return job_id, world
