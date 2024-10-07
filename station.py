from astropy.time import Time
import astropy.units as u
from astropy.coordinates import EarthLocation

class Station:
    label: str

    # Geodetic position information
    lat: float
    lon: float
    height: float

    # Geocentric position information
    X: float
    Y: float
    Z: float

    # Time information
    time: Time
    time_zone: float

    # Camera alignment
    wcs_path: str
    wcs_time: Time

    def __init__(self,
                 lat: float, lon: float, height: float,
                 time_zone: float, time: str = None,
                 label: str = '',
                 wcs_path: str = None, wcs_time: str = None):
        """Args:
            lat (float): Latitude of station in decimal degrees
            lon (float): Longitude of station in decimal degrees
            height (float): Height above see in metres
            time_zone (float): Offset in hours from UTC
            time (str): Time at the station at the time of observation
            label (str): Label describing the station, optional, an empty
            string is used if not set
            wcs_path (str): Path to wcs file to be used in fixed alignment
            astrometry
            wcs_time (str): A string representing the date and time of wcs
            file measurement

        Returns:
            None
        """

        self.lat = lat
        self.lon = lon
        self.height = height

        self.earth_location = EarthLocation(lat=self.lat * u.deg,
                                            lon=self.lon * u.deg,
                                            height=self.height * u.m)

        self.geodetic = {
            'lat': self.lat,
            'lon': self.lon,
            'height': self.height
        }

        self.time_zone = time_zone
        self.label = label

        self.wcs_path = wcs_path
        if wcs_time != None:
            self.wcs_time = Time(wcs_time)

        # Calculate geocentric coordinates
        from coordinates import geodetic_to_geocentric

        self.geocentric = geodetic_to_geocentric(self.geodetic)

        # Calculate local sidereal time if time is set
        if time == None:
            return
        
        self.time = Time(time, location=self.earth_location) + self.time_zone * u.hour
        self.lst = self.time.sidereal_time('mean').value / 24 * 360

        self.geodetic_lst = {
            'lat': self.lat,
            'lon': self.lst,
            'height': self.height
        }
        self.geocentric_lst = geodetic_to_geocentric(self.geodetic_lst)

    def set_wcs(self, wcs_path: str, wcs_time: str) -> None:
        """Updates the WCS file path and calculation time
        
        Args:
            wcs_path (str): Path to wcs file to be used in fixed alignment
            astrometry
            wcs_time (str): A string representing the date and time of wcs
            file measurement

        Returns:
            None
        """

        self.wcs_path = wcs_path
        self.wcs_time = Time(wcs_time)

    def set_time(self, time: str, time_zone: float = None) -> None:
        """Updates the station time
        
        Args:
            time (str): A string representing the date and time
            time_zone (float): Offset in hours from GMT, optional

        Returns:
            None
        """

        if time_zone != None:
            self.time_zone = time_zone

        self.time = Time(time, location=self.earth_location) + self.time_zone * u.hour
        self.lst = self.time.sidereal_time('mean').value / 24 * 360
