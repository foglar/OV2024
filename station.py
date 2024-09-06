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
    time_zone: float

    def __init__(self, lat: float, lon: float, height: float, time_zone: float, time: str = None, label: str = ''):
        """Args:
            lat (float): Latitude of station in decimal degrees
            lon (float): Longitude of station in decimal degrees
            height (float): Height above see in metres
            time_zone (float): Offset in hours from UTC
            time (str): time at the station at the time of observation
            label (str): Label describing the station
        """

        self.lat = lat
        self.lon = lon
        self.height = height

        self.earth_location = EarthLocation(lat=self.lat * u.deg,
                                            lon=self.lon * u.deg,
                                            height=self.height * u.m)

        self.geodetic = {'lat': self.lat,'lon': self.lon, 'height': self.height}

        self.time_zone = time_zone
        self.label = label

        # Calculate geocentric coordinates
        from coordinates import geodetic_to_geocentric

        self.geocentric = geodetic_to_geocentric(self.geodetic)

        # Calculate local sidereal time if time is set
        if time == None:
            return
        
        t = Time(time, location=self.earth_location) + self.time_zone * u.hour
        self.lst = t.sidereal_time('mean')

        self.geodetic_lst = {'lat': self.lat, 'lon': self.lst, 'height': self.height}
        self.geocentric_lst = geodetic_to_geocentric(self.geodetic_lst)
