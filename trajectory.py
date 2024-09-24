from math import sin, cos, radians, sqrt, asin, acos, degrees, pi
import astropy.units as u
from astropy.time import Time
import numpy
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plot

from coordinates import *
from station import Station
    
class Meteor:
    label: str

    # Station and observation information
    station_a: Station
    station_b: Station

    time: Time

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

    distance_from_beginning_a: list[float]
    distance_from_beginning_b: list[float]

    def __init__(self, label: str,
                 station_a: Station, station_b: Station,
                 observation_a: list[list[float]], observation_b:list[list[float]],
                 time: str) -> None:
        """Args:
            label (str): Meteor label
            station_a (Station): Station instance describing station A
            station_b (Station): Station instance describing station B
            observation_a (list[list[float]]): Measured coordinates of meteor points in decimal ra and dec with time values form station A
            observation_b (list[list[float]]): Measured coordinates of meteor points in decimal ra and dec with time values form station B
            time: (str): Time and date from which the measurements are related
        """

        self.label = label

        # Station and observation information
        self.station_a = station_a
        self.station_b = station_b

        self.time = Time(time)

        # Separate coordinate and time values
        self.observation_a = [(i[0], i[1]) for i in observation_a]
        self.times_a = [i[2] for i in observation_a]

        self.observation_b = [(i[0], i[1]) for i in observation_b]
        self.times_b = [i[2] for i in observation_b]

        # Define yet uncalculated values
        self.radiant = None
        self.Q_angle = None

        self.geocentric_trajectory_a = None
        self.geocentric_trajectory_b = None

        self.geodetic_trajectory_a = None
        self.geodetic_trajectory_b = None

        self.distance_from_beginning_a = None
        self.distance_from_beginning_b = None

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

        ra, dec = solve_goniometry((Xi, Eta, Zeta))
        # If the radiant is under the horizon, change sign of Xi, Eta, Zeta
        if world_to_altaz(ra, dec, self.station_a, self.time)[0] < 0 or world_to_altaz(ra, dec, self.station_b, self.time)[0] < 0:
            ra, dec = solve_goniometry((-Xi, -Eta, -Zeta))

        self.radiant = [ra, dec]
        self.Q_angle = angle

    def get_radiant(self) -> list[float]:
        """Returns radiant coordinates in decimal degrees
        
        Returns:
            list[float]: Radiant RA and Dec coordinates
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
    
    def plot_radiant(self) -> None:
        """Plots calculated meteor radiant and meteor tracks

        Returns:
            None
        """

        # If radiant isn't calculated yet, calculate
        if self.radiant == None:
            self.calculate_radiant()

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

    def calculate_trajectories(self) -> None:
        """Calculates meteor trajectories from both stations
        
        Returns:
            None
        """

        # Solve the station planes
        vector_a = calculate_meteor_plane(self.observation_a) + self.station_a.geocentric_lst
        vector_b = calculate_meteor_plane(self.observation_b) + self.station_b.geocentric_lst

        # Calculate GST
        GST = self.time.sidereal_time('mean', 'greenwich').value / 24 * 360

        # Solve the intersection with the meteor plane
        self.geocentric_trajectory_a = []
        self.geodetic_trajectory_a = []
        for point in self.observation_a:
            raw = calculate_meteor_point_vector(point, vector_a, vector_b)

            lon, lat, height = geocentric_to_geodetic(raw)
            cor = {'lat': lat, 'lon': lon - GST, 'height': height}

            self.geodetic_trajectory_a.append(cor)
            self.geocentric_trajectory_a.append(geodetic_to_geocentric(cor))

        self.geocentric_trajectory_b = []
        self.geodetic_trajectory_b = []
        for point in self.observation_b:
            raw = calculate_meteor_point_vector(point, vector_b, vector_a)

            lon, lat, height = geocentric_to_geodetic(raw)
            cor = {'lat': lat, 'lon': lon - GST, 'height': height}

            self.geodetic_trajectory_b.append(cor)
            self.geocentric_trajectory_b.append(geodetic_to_geocentric(cor))

        # Mesh trajectories together according to the height
        self.times = []
        self.geocentric_trajectory = []
        self.geodetic_trajectory = []

        # Append the data point with higher height value
        i, j = 0, 0
        while i < len(self.times_a) and j < len(self.times_b):
            if self.geodetic_trajectory_a[i]['height'] > self.geodetic_trajectory_b[j]['height']:
                self.times.append(self.times_a[i])
                self.geocentric_trajectory.append(self.geocentric_trajectory_a[i])
                self.geodetic_trajectory.append(self.geodetic_trajectory_a[i])
                i += 1
            else:
                self.times.append(self.times_b[j])
                self.geocentric_trajectory.append(self.geocentric_trajectory_b[j])
                self.geodetic_trajectory.append(self.geodetic_trajectory_b[j])
                j += 1

        # Append the rest
        while i < len(self.times_a):
            self.times.append(self.times_a[i])
            self.geocentric_trajectory.append(self.geocentric_trajectory_a[i])
            self.geodetic_trajectory.append(self.geodetic_trajectory_a[i])
            i += 1

        while j < len(self.times_b):
            self.times.append(self.times_b[j])
            self.geocentric_trajectory.append(self.geocentric_trajectory_b[j])
            self.geodetic_trajectory.append(self.geodetic_trajectory_b[j])
            j += 1

    def get_trajectories_geocentric(self) -> list[list[list[float]]]:
        """Returns the separate trajectories from both stations in geocentric coordinates
        
        Returns:
            list[list[list[float]]]
        """

        # If the geocentric trajectory isn't calculated yet, calculate
        if self.geocentric_trajectory_a == None or self.geocentric_trajectory_b == None:
            self.calculate_trajectories()

        return self.geocentric_trajectory_a, self.geocentric_trajectory_b

    def get_trajectories_geodetic(self) -> list[list[list[float]]]:
        """Returns the separate trajectories from both stations in geodetic coordinates
        
        Returns:
            list[list[list[float]]]
        """

        # If the geodetic trajectories aren't calculated yet, calculate
        if self.geodetic_trajectory_a == None or self.geodetic_trajectory_b == None:
            self.calculate_trajectories()

        return self.geodetic_trajectory_a, self.geodetic_trajectory_b
    
    def save_trajectory_gpx(self, correct_start, correct_end) -> None:
        """Returns the trajectory in a GPX format"""

        # If the geodetic trajectories aren't calculated yet, calculate
        if self.geodetic_trajectory_a == None or self.geodetic_trajectory_b == None:
            self.calculate_trajectories()

        gpx = '<?xml version="1.0" encoding="UTF-8"?><gpx xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.topografix.com/GPX/gpx_style/0/2 http://www.topografix.com/GPX/gpx_style/0/2/gpx_style.xsd" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpx_style="http://www.topografix.com/GPX/gpx_style/0/2" version="1.1" creator="https://gpx.studio"><metadata>    <name>Meteory</name>    <author>        <name>gpx.studio</name>        <link href="https://gpx.studio"></link>    </author></metadata>'

        # Add stations
        gpx += f'<wpt lat="{self.station_a.geodetic["lat"]}" lon="{self.station_a.geodetic["lon"]}"><ele>{self.station_a.geodetic["height"]}</ele><name>{self.station_a.label}</name></wpt>'
        gpx += f'<wpt lat="{self.station_b.geodetic["lat"]}" lon="{self.station_b.geodetic["lon"]}"><ele>{self.station_b.geodetic["height"]}</ele><name>{self.station_b.label}</name></wpt>'

        # Add trajectories
        gpx += f'<trk><name>Trajectory {self.label}</name><trkseg>'
        for point in self.geodetic_trajectory:
            gpx += f'<trkpt lat="{point["lat"]}" lon="{point["lon"]}"><ele>{point["height"]}</ele></trkpt>'
        gpx += '</trkseg></trk>'

        #Write the correct trajectory
        gpx += '<trk><name>Correct solution</name><trkseg>'
        gpx += f'<trkpt lat="{correct_start[1]}" lon="{correct_start[0]}"><ele>{correct_start[2]}</ele></trkpt>'
        gpx += f'<trkpt lat="{correct_end[1]}" lon="{correct_end[0]}"><ele>{correct_end[2]}</ele></trkpt>'
        gpx += '</trkseg></trk>'

        # Terminate the gpx file
        gpx += '</gpx>'

        # Write the gpx to a file
        open(f'{self.label}.gpx', 'w').write(gpx)

    def plot_trajectory_geodetic(self) -> None:
        """Plots the geodetic trajectory with matplotlib
        
        Returns:
            None
        """

        fig = plot.figure(figsize=(8,8))
        ax = fig.add_axes([0.1,0.1,0.8,0.8])

        # Set up the background map
        m = Basemap(projection = 'stere', rsphere = 6371200.,
                    resolution = 'i', area_thresh = 10000,
                    lat_0 = 50, lon_0 = 15,
                    width=1200000, height=800000)
    
        m.drawcoastlines()
        m.drawcountries()

        # Draw stations
        m.scatter(latlon = True, x = self.station_a.lon, y = self.station_a.lat,
                  color='red')

        m.scatter(latlon = True, x = self.station_b.lon, y = self.station_b.lat,
                  color='red')
        
        # Draw meteor trajectories
        x, y, heights = [], [], []
        for point in self.geodetic_trajectory:
            x.append(point['lon'])
            y.append(point['lat'])

            heights.append(point['height'])

        x, y = m(x, y)
        m.plot(x, y, linewidth=1.5, color='blue')

        # Add height marks
        for i in range(len(x)):
            plot.annotate(f'{self.times[i]} - {round(heights[i] / 1000, 3)} km', (x[i], y[i]))

        # Draw the first and last points with special markers
        m.scatter(x[0], y[0], marker='^', color='blue')
        m.scatter(x[-1], y[-1], marker='x', color='blue')
            
        plot.title(f'Meteor {self.label}')
        plot.show()

    def calculate_distances_along_trajectories(self) -> None:
        """Calculates the distance of each point on both trajectories from
        the first points.

        Returns:
            None
        """

        # If the geocentric trajectories aren't calculated yet, calculate
        if self.geocentric_trajectory_a == None or self.geocentric_trajectory_b == None:
            self.calculate_trajectories()

        self.distance_from_beginning_a = []
        beginning = self.geocentric_trajectory_a[0]
        for point in self.geocentric_trajectory_a:
            self.distance_from_beginning_a.append(sqrt((beginning[0] - point[0]) ** 2 + (beginning[1] - point[1]) ** 2 + (beginning[2] - point[2]) ** 2))

        self.distance_from_beginning_b = []
        beginning = self.geocentric_trajectory_b[0]
        for point in self.geocentric_trajectory_b:
            self.distance_from_beginning_b.append(sqrt((beginning[0] - point[0]) ** 2 + (beginning[1] - point[1]) ** 2 + (beginning[2] - point[2]) ** 2))

    def get_distances_along_trajectories(self) -> list[list[float]]:
        """Returns the distances of points on both trajectories from
        the first point
        
        Returns:
            list[list[float]]
        """

        # If the distances aren't calculated yet, calculate
        if self.distance_from_beginning_a == None or self.distance_from_beginning_b == None:
            self.calculate_distances_along_trajectories()

        return self.distance_from_beginning_a, self.distance_from_beginning_b
    
    def calculate_velocities_along_trajectories(self) -> None:
        """Calculates the velocity of meteor at each point in both trajectories"""

        # If the geocentric trajectories aren't calculated yet, calculate
        if self.geocentric_trajectory_a == None or self.geocentric_trajectory_b == None:
            self.calculate_trajectories()

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
    
    def plot_velocities_along_trajectories(self) -> None:
        """Plots a velocity vs time graph
        
        Returns:
            None
        """

        # If the velocities aren't calculated yet, calculate
        if self.velocities_a == None or self.velocities_b == None:
            self.calculate_velocities_along_trajectories()

        fig, ax = plot.subplots()

        x, y = [], []
        for i in range(len(self.velocities_a)):
            x.append(self.times_a[i + 1])
            y.append(self.velocities_a[i])
        ax.plot(x, y)

        x, y = [], []
        for i in range(len(self.velocities_b)):
            x.append(self.times_b[i + 1])
            y.append(self.velocities_b[i])
        ax.plot(x, y)

        plot.show()

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
        Xi, Eta, Zeta = calculate_meteor_point(point)

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

def calculate_meteor_point(point: list[float]) -> list[float]:
    """Calculates Xi, Eta and Zeta values from ra and dec values of meteor point

    Args:
        point (list[float]): ra and dec coordinates in decimal degrees

    Returns:
        list[float]: Geocentric vector Xi, Eta, Zeta
    """

    # Calculate equation 9
    xi = cos(radians(point[1])) * cos(radians(point[0]))
    eta = cos(radians(point[1])) * sin(radians(point[0]))
    zeta = sin(radians(point[1]))

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
    xi, eta, zeta = calculate_meteor_point(point)

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
        float: distance between points A and B
    """

    xa, ya, za = point_a
    xb, yb, zb = point_b

    return sqrt((xb - xa) ** 2 + (yb - ya) ** 2 + (zb - za) ** 2)

def preprocess(img_path: str, data_path: str, tmp_path: str) -> None:
    """Image preprocessing for astrometry. Masks out space around sky view and meteor
    
    Args:
        img_path (str): The path to the image to mask
        data_path (str): The path to data.txt file describing meteor
        tmp_path (str): Path, where the masked image should be saved

    Returns:
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

def solve_goniometry(vector: list[float]) -> list[float]:
    """Solves equation 9
    
    Args:
        vector (list[float]): Vector (Xi, Eta, Zeta)
        
    Returns:
        list[float]: RA and Dec in decimal degrees
    """

    # Calculate dec
    declinations = [asin(vector[2]), pi - asin(vector[2]) if vector[2] >= 0 else 2 * pi - asin(-vector[2])]
    for dec in declinations:
        # Skip if Dec is outside of it's domain
        if dec > 0.5 * pi or dec < -0.5 * pi:
            break

        # Check for quadrants
        # quad 1 2 3 4
        # sin  + + - -
        # cos  + - - +

        # Float math can result in values slightly outside domains, clamp
        sin_ra = min(max(vector[1] / cos(dec), -1), 1)
        cos_ra = min(max(vector[0] / cos(dec), -1), 1)

        ra = None
        if sin_ra >= 0 and cos_ra >= 0:
            ra = asin(sin_ra)
        if sin_ra >= 0 and cos_ra < 0:
            ra = pi - asin(sin_ra)
        if sin_ra < 0 and cos_ra < 0:
            ra = pi - asin(sin_ra)
        if sin_ra < 0 and cos_ra >= 0:
            ra = 2 * pi + asin(sin_ra)

        if numpy.allclose(vector, (cos(dec)*cos(ra), cos(dec)*sin(ra), sin(dec)), atol=0.001):
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
