from math import sin, cos, radians, sqrt, asin, acos, degrees, pi, atan2
import astropy.units as u
from astropy.time import Time
import numpy

from coordinates import *

class Meteor:
    # Station and observation information
    station_a: dict
    station_b: dict

    observation_a: list[list[float]]
    observation_b: list[list[float]]

    times_a: (list[float])
    times_b: (list[float])

    Q_angle: float
    
    # Radiant information
    radiant: list[float]

    # Trajectory information
    geocentric_trajectory_a: list[list[float]]
    geocentric_trajectory_b: list[list[float]]

    geodetic_trajectory_a: list[list[float]]
    geodetic_trajectory_b: list[list[float]]

    distance_from_begining_a: list[float]
    distance_from_begining_b: list[float]

    def __init__(self, station_a: dict, station_b: dict,
                 observation_a: list[list[float]], observation_b:list[list[float]],
                 times_a: (list[float]), times_b: (list[float])) -> None:
        """Args:
            station_a dict: latitude, height and time of station A
            station_b dict: latitude, height and time of station B
            observation_b (list[list[float]]): meteor coordinates in ra and dec in decimal degrees from station A
            observation_a (list[list[float]]): meteor coordinates in ra and dec in decimal degrees from station B
            times_a (list[float]): Times in seconds of each point observation
            times_b (list[float]): Times in seconds of each point observation
        """
        # Station and observation information
        self.station_a = station_a
        self.station_b = station_b

        self.observation_a = observation_a
        self.observation_b = observation_b

        self.times_a = times_a
        self.times_b = times_b

        # Define yet uncalculated values
        self.radiant = None
        self.Q_angle = None

        self.geocentric_trajectory_a = None
        self.geocentric_trajectory_b = None

        self.geodetic_trajectory_a = None
        self.geodetic_trajectory_b = None

        self.distance_from_begining_a = None
        self.distance_from_begining_b = None

        self.velocities_a = None
        self.velocities_b = None

    def calculate_radiant(self) -> None:
        """Calculates the radiant of the meteor according to Ceplecha (1987)

        Returns:
            None
        """

        aa, ba, ca = calculate_meteor_plane(self.observation_a)
        ab, bb, cb = calculate_meteor_plane(self.observation_b)
        
        d = sqrt((ba * cb - bb * ca) ** 2 + (ab * ca - aa * cb) ** 2 + (aa * bb - ab * ba) ** 2)

        Xi = (ba * cb - bb * ca) / d
        Eta = (ab * ca - aa * cb) / d
        Zeta = (aa * bb - ab * ba) / d

        angle = degrees(acos(abs(aa*ab + ba*bb + ca*cb)) / sqrt((aa**2+ba**2+ca**2)*(ab**2+bb**2+cb**2)))

        ra, dec = solve_goniometry(Xi, Eta, Zeta)
        # If the radiant is under the horizon, change sign of Xi, Eta, Zeta
        if world_to_altaz(ra, dec, self.station_a)[0] < 0 or world_to_altaz(ra, dec, self.station_b)[0] < 0:
            ra, dec = solve_goniometry(-Xi, -Eta, -Zeta)

        self.radiant = [ra, dec]
        self.Q_angle = angle

    def get_radiant(self) -> list[float]:
        """Returns radiant coordinates in decimal degrees
        
        Returns:
            list[float]: Radiant RA and Dec coordiantes
        """

        # If radiant isn't calculated yet, calculate
        if self.radiant == None:
            self.calculate_radiant()

        return self.radiant
    
    def get_Q_angle(self) -> float:
        """Returns the angle between planes containing the meteor and observation stations
        
        Returns:
            float: the Q angle in decimal degrees
        """

        # If the angle isn't calculated yet, calculate
        if self.Q_angle == None:
            self.calculate_radiant()

        return self.Q_angle
    
    def plot__radiant(self) -> None:
        """Plots calculated meteor radiant and meteor tracks

        Returns:
            None
        """

        # If radiant isn't calculated yet, calculate
        if self.radiant == None:
            self.calculate_radiant()

        import matplotlib.pyplot as plot
        fig, ax = plot.subplots()

        # Plot the path from station A
        x, y = [], []
        for point in self.observation_a:
            ax.scatter(point[0], point[1], color = 'b')
            x.append(point[0])
            y.append(point[1])
        ax.plot(x, y)
        
        # Plot the path from station B
        x, y = [], []
        for point in self.observation_b:
            ax.scatter(point[0], point[1], color = 'y')
            x.append(point[0])
            y.append(point[1])
        ax.plot(x, y)

        # Plot the radiant
        ax.scatter(self.radiant[0], self.radiant[1], color = 'r')

        plot.show()

    def calculate_trajectories_geocentric(self) -> None:
        """Calculates meteor trajectories from both stations in geocentric coordinates
        
        Returns:
            None
        """

        # Solve the station planes
        vector_a = calculate_meteor_plane(self.observation_a) + geodetic_to_geocentric(self.station_a)
        vector_b = calculate_meteor_plane(self.observation_b) + geodetic_to_geocentric(self.station_b)

        # Solve the intersection with the meteor plane
        self.geocentric_trajectory_a = []
        for point in self.observation_a:
            self.geocentric_trajectory_a.append(calculate_meteor_point_vector(point, vector_a, vector_b))

        self.geocentric_trajectory_b = []
        for point in self.observation_b:
            self.geocentric_trajectory_b.append(calculate_meteor_point_vector(point, vector_b, vector_a))
    
    def get_trajectories_geocentric(self) -> list[list[list[float]]]:
        """Returns the separate trajectories from both stations in geocentric coordinates
        
        Returns:
            list[list[list[float]]]
        """

        # If the geocentric trajectory isn't calculated yet, calculate
        if self.geocentric_trajectory_a == None or self.geocentric_trajectory_b == None:
            self.calculate_trajectories_geocentric()

        return self.geocentric_trajectory_a, self.geocentric_trajectory_b

    def calculate_trajectories_geodetic(self) -> None:
        """Calculates meteor trajectories from both stations in geodetic coordinates
        
        Returns:
            None
        """

        # If the geocentric trajectories aren't calculated yet, calculate
        if self.geocentric_trajectory_a == None or self.geocentric_trajectory_b == None:
            self.calculate_trajectories_geocentric()

        # Convert the geocentric coordinates to geodetic
        self.geodetic_trajectory_a = []
        for point in self.geocentric_trajectory_a:
            self.geodetic_trajectory_a.append(geocentric_to_geodetic(point))

        self.geodetic_trajectory_b = []
        for point in self.geocentric_trajectory_b:
            self.geodetic_trajectory_b.append(geocentric_to_geodetic(point))

    def get_trajectories_geodetic(self) -> list[list[list[float]]]:
        """Returns the separate trajectories from both stations in geodetic coordinates
        
        Returns:
            list[list[list[float]]]
        """

        # If the geodetic trajectories aren't calculated yet, calcualte
        if self.geodetic_trajectory_a == None or self.geodetic_trajectory_b == None:
            self.calculate_trajectories_geodetic()

        return self.geodetic_trajectory_a, self.geodetic_trajectory_b

    def calculate_distances_along_trajectories(self) -> None:
        """Calculates the distance of each point on both trajectories from
        the first points.

        Returns:
            None
        """

        # If the geocentric trajectories aren't calculated yet, calculate
        if self.geocentric_trajectory_a == None or self.geocentric_trajectory_b == None:
            self.calculate_trajectories_geocentric()

        self.distance_from_begining_a = []
        beginning = self.geocentric_trajectory_a[0]
        for point in self.geocentric_trajectory_a:
            self.distance_from_begining_a.append(sqrt((beginning[0] - point[0]) ** 2 + (beginning[1] - point[1]) ** 2 + (beginning[2] - point[2]) ** 2))

        self.distance_from_begining_b = []
        beginning = self.geocentric_trajectory_b[0]
        for point in self.geocentric_trajectory_b:
            self.distance_from_begining_b.append(sqrt((beginning[0] - point[0]) ** 2 + (beginning[1] - point[1]) ** 2 + (beginning[2] - point[2]) ** 2))

    def get_distances_along_trajectories(self) -> list[list[float]]:
        """Returns the distances of points on both trajectories from
        the first point
        
        Returns:
            list[list[float]]
        """

        # If the distances aren't calculated yet, calculate
        if self.distance_from_begining_a == None or self.distance_from_begining_b == None:
            self.calculate_distances_along_trajectories()

        return self.distance_from_begining_a, self.distance_from_begining_b
    
    def calculate_velocities_along_trajectories(self) -> None:
        """Calculates the velocity of meteor at each point in both trajectories"""

        # If the geocentric trajectories aren't calculated yet, calculate
        if self.geocentric_trajectory_a == None or self.geocentric_trajectory_b == None:
            self.calculate_trajectories_geocentric()

        self.velocities_a = []
        for i in range(1, len(self.geocentric_trajectory_a)):
            distance_from_last = calculate_distance(self.geocentric_trajectory_a[i], self.geocentric_trajectory_a[i - 1])
            time_from_last = self.times_a[i] - self.times_a[i - 1]

            self.velocities_a.append(distance_from_last/time_from_last)

        self.velocities_b = []
        for i in range(1, len(self.geocentric_trajectory_b)):
            distance_from_last = calculate_distance(self.geocentric_trajectory_b[i], self.geocentric_trajectory_b[i - 1])
            time_from_last = self.times_b[i] - self.times_b[i - 1]

            self.velocities_b.append(distance_from_last/time_from_last)

    def get_velocities_along_trajectories(self) -> list[list[float]]:
        """Returns the velocities at all but the first points from both trajectories
        
        Returns:
            list[list[float]]
        """

        # If the velocities aren't calculated yet, calculate
        if self.velocities_a == None or self.velocities_b == None:
            self.calculate_velocities_along_trajectories()

        return self.velocities_a, self.velocities_b

def calculate_meteor_plane(points: list[float]) -> list[float]:
    """Calculates meteor path plane according to equations 9 and 11
    
    Args:
        points (list[list[float]]): ra and dec coordinates of meteor points
        
    Returns:
        list[float]: vector (a, b, c) describing meteor path plane
    """

    # Calculate equation 9 for all meteor points
    xi_eta, eta_zeta, eta_eta, xi_zeta, xi_xi = 0, 0, 0, 0, 0
    for point in points:
        Xi, Eta, Zeta = calculate_meteor_point(point[0], point[1])

        xi_eta += Xi * Eta
        eta_zeta += Eta * Zeta
        eta_eta += Eta ** 2
        xi_zeta += Xi * Zeta
        xi_xi += Xi ** 2

    # Calculate equation 11
    a_dash = xi_eta * eta_zeta - eta_eta * xi_zeta
    b_dash = xi_eta * xi_zeta - xi_xi * eta_zeta
    c_dash = xi_xi * eta_eta - xi_eta ** 2
    d_dash = sqrt(a_dash ** 2 + b_dash ** 2 + c_dash ** 2)

    a = a_dash / d_dash
    b = b_dash / d_dash
    c = c_dash / d_dash

    return a, b, c

def calculate_meteor_point(ra: float, dec: float) -> list[float]:
    """Calculates Xi, Eta and Zeta values from ra and dec values of meteor point

    Args:
        ra (float): right ascension in decimal degrees
        dec (float): declination in decimal degrees

    Returns:
        list[float]:  Geocentric vector Xi, Eta, Zeta
    """

    # Calculate equation 9
    xi = cos(radians(dec)) * cos(radians(ra))
    eta = cos(radians(dec)) * sin(radians(ra))
    zeta = sin(radians(dec))

    return xi, eta, zeta

def calculate_meteor_point_vector(point: list[float], station_a: list[float], station_b: list[float]) -> list[float]:
    """Calculates vector X, Y, Z for meteor point
    
    Args:
        meteor (list[float]): ra and dec of meteor
        station_a (list[float]): vectors a, b, c and X, Y, Z of station A
        station_b (list[float]): vectors a, b, c and X, Y, Z of station B

    Returns:
        list[float]: coordinates X, Y and Z of intersection
    """

    aa, ba, ca, xa, ya, za = station_a
    ab, bb, cb, xb, yb, zb = station_b
    xi, eta, zeta = calculate_meteor_point(point[0], point[1])

    # Plane definitions and equation 13
    plane_a = [aa, ba, ca, -(aa * xa + ba * ya + ca * za)]
    plane_b = [ab, bb, cb, -(ab * xb + bb * yb + cb * zb)]

    # Equation 18
    an = eta * ca - zeta * ba
    bn = zeta * aa - xi * ca
    cn = xi * ba - eta * aa
    dn = -(an * xa + bn * ya + cn * za)

    plane_n = [an, bn, cn, dn]

    return solve_plane_intersection(plane_a, plane_b, plane_n)

def calculate_distance(point_a: list[float], point_b: list[float]) -> float:
    """Calculates distance between two points defined with geocentric vectors
    
    Args:
        point_a (list[float]): Vector (X, Y, Z) A
        point_b (list[float]): Vector (X, Y, Z) B
        
    Returns:
        float: disctance between points A and B
    """

    xa, ya, za = point_a
    xb, yb, zb = point_b

    return sqrt((xb - xa) ** 2 + (yb - ya) ** 2 + (zb - za) ** 2)

def calculate_sidereal_time(lat: float, lon: float, time, time_zone: int) -> float:
    """Calculates sidereal time in degrees.

    Args:
        time: Time at the observatory
        lat (float): Latitude of observatory
        lon (float): Longitude of observatory
        time_zone (int): Offset in hours from GMT

    Returns:
        float: Sidereal time in degrees
    """

    t = Time(time, location=(lon, lat)) - u.hour * time_zone
    return t.sidereal_time('apparent').degree

def preprocess(img_path: str, data_path: str, tmp_path: str) -> None:
    """Image preprocessing for astrometry. Masks out space around sky view and meteor
    
    Args:
        img_path (str): The path to the image to mask
        data_path (str): The path to data.txt file describing meteor
        tmp_path (str): Path, where the masked image should be saved

    Retruns:
        None
    """

    import cv2, numpy

    image = cv2.imread(img_path)

    mask = numpy.zeros(image.shape, dtype=numpy.uint8)
    mask = cv2.circle(mask, (image.shape[1] // 2, image.shape[0] // 2), image.shape[0] // 2, (255, 255, 255), -1)

    meteor = load_meteors(data_path)
    for point in meteor[0]:
        mask = cv2.circle(mask, (int(point[0]), int(point[1])), 3, (0, 0, 0), -1)

    cv2.imwrite(tmp_path, cv2.bitwise_and(mask, image))

def solve_goniometry(xi: float, eta: float, zeta: float) -> list[float]:
    """Solves equation 9
    
    Args:
        Vector (Xi, Eta, Zeta)
        
    Returns:
        list[float]: RA and Dec in decimal degrees
    """

    # Calculate dec
    declinations = [asin(zeta), pi - asin(zeta) if zeta >= 0 else 2 * pi - asin(-zeta)]
    for dec in declinations:
        # Skip if Dec is outside of it's domain
        if dec > 90 and dec < -90:
            break

        # Check for quadrants
        # quad 1 2 3 4
        # sin  + + - -
        # cos  + - - +

        # Float math can result in values slightly outside domains, round
        sin_ra = round(eta / cos(dec), 12)
        cos_ra = round(xi / cos(dec), 12)

        ra = None
        if sin_ra >= 0 and cos_ra >= 0:
            ra = asin(sin_ra)
        if sin_ra >= 0 and cos_ra < 0:
            ra = pi - asin(sin_ra)
        if sin_ra < 0 and cos_ra < 0:
            ra = pi - asin(sin_ra)
        if sin_ra < 0 and cos_ra >= 0:
            ra = 2 * pi + asin(sin_ra)

        if numpy.allclose((xi, eta, zeta), (cos(dec)*cos(ra), cos(dec)*sin(ra), sin(dec))):
            print()
            return degrees(ra), degrees(dec)

def solve_plane_intersection(plane_a: list[float], plane_b: list[float], plane_c: list[float]) -> list[float]:
    """Finds the intersection of three planes defined by (a, b, c) and d by equation 19

    Args:
        plane_a (list[float]): values a, b, c and d of plane A
        plane_b (list[float]): values a, b, c and d of plane B
        plane_c (list[float]): values a, b, c and d of plane C

    Returns:
        list[float]: coordinates X, Y and Z of intersection
    """

    a = numpy.array([plane_a[:3], plane_b[:3], plane_c[:3]])
    # Invert d since numpy assumes ax + by + cz = d
    b = numpy.array([-plane_a[3], -plane_b[3], -plane_c[3]])

    return list(numpy.linalg.solve(a, b))

if __name__ == '__main__':
    # Latitude, longitude, height above sea level, time of observation
    ondrejov = {'lon': 14.780208, 'lat': 49.910222, 'height':  524, 'time': '2018-10-8 22:03:54', 'time_zone': 1}
    kunzak = {'lon': 15.200930, 'lat': 49.107290, 'height': 656, 'time': '2018-10-8 22:03:54', 'time_zone': 1}

    # Precomputed ra, dec and time values
    ondrejov_18A08052 = [[308.607, 15.553, 1.0164], [308.547, 15.460, 1.0328], [308.541, 15.327, 1.0492], [308.493, 15.207, 1.0656], [308.470, 15.034, 1.0820], [308.480, 14.941, 1.0984], [308.432, 14.821, 1.1148], [308.421, 14.734, 1.1311], [308.378, 14.567, 1.1475], [308.343, 14.419, 1.1639], [308.304, 14.319, 1.1803], [308.262, 14.151, 1.1967], [308.235, 14.023, 1.2131], [308.224, 13.936, 1.2295], [308.181, 13.767, 1.2459], [308.163, 13.659, 1.2623], [308.144, 13.551, 1.2787], [308.105, 13.450, 1.2951], [308.119, 13.308, 1.3115], [308.141, 13.186, 1.3279], [308.074, 13.071, 1.3443], [308.088, 12.928, 1.3607], [308.006, 12.772, 1.3770]]
    kunzak_18A08052 = [[270.158, 40.947, 0.9632], [270.062, 40.870, 0.9796], [269.927, 40.798, 0.9960], [269.859, 40.762, 1.0124], [269.759, 40.655, 1.0288], [269.709, 40.602, 1.0452], [269.615, 40.525, 1.0616], [269.543, 40.459, 1.0780], [269.432, 40.399, 1.0944], [269.400, 40.329, 1.1108], [269.345, 40.247, 1.1272], [269.175, 40.180, 1.1435], [269.034, 40.050, 1.1599], [268.985, 39.997, 1.1763], [268.812, 39.902, 1.1927], [268.738, 39.808, 1.2091], [268.604, 39.707, 1.2255], [268.501, 39.676, 1.2419], [268.412, 39.600, 1.2583], [268.365, 39.547, 1.2747], [268.377, 39.502, 1.2911], [268.292, 39.454, 1.3075], [268.225, 39.390, 1.3239], [268.170, 39.280, 1.3403], [268.061, 39.192, 1.3567], [267.977, 39.145, 1.3731], [267.927, 39.064, 1.3894], [267.885, 39.040, 1.4058]]

    meteor_a = [(i[0], i[1]) for i in ondrejov_18A08052]
    time_a = [i[2] for i in ondrejov_18A08052]
    meteor_b = [(i[0], i[1]) for i in kunzak_18A08052]
    time_b = [i[2] for i in kunzak_18A08052]

    meteor = Meteor(ondrejov, kunzak, meteor_a, meteor_b, time_a, time_b)
    print(meteor.get_velocities_along_trajectories()[1])
