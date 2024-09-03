class Station:
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

    def __init__(self, lat: float, lon: float, height: float, time_zone: float):
        """Args:
            lat (float): Latitude of station in decimal degrees
            lon (float): Longitude of station in decimal degrees
            height (float): Height above see in metres
            time_zone (float): Offset in hours from UTC
        """

        self.lat = lat
        self.lon = lon
        self.height = height

        self.geodetic = {'lat': self.lat,'lon': self.lon, 'height': self.height}

        self.time_zone = time_zone

        # Calculate geocentric coordinates
        from coordinates import geodetic_to_geocentric
        self.geocentric = geodetic_to_geocentric(self.geodetic)
        self.X, self.Y, self.Z = self.geocentric
