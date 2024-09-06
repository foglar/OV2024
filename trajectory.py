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
        gpx += f'<wpt lat="{self.station_a.geodetic["lat"]}" lon="{self.station_a.geodetic["lon"]}"><ele>{self.station_a.geodetic["height"]}</ele><name>Station A</name></wpt>'
        gpx += f'<wpt lat="{self.station_b.geodetic["lat"]}" lon="{self.station_b.geodetic["lon"]}"><ele>{self.station_b.geodetic["height"]}</ele><name>Station B</name></wpt>'

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
                    width=12000000, height=8000000)
    
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
            self.calculate_trajectories_geocentric()

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

if __name__ == '__main__':
    # Precomputed ra, dec and time values
    meteory = [
        ['18A08085', '2018-10-8 21:38:32', [[337.420, 5.816, 1.0164], [337.526, 5.678, 1.0328], [337.598, 5.589, 1.0492], [337.676, 5.463, 1.0656], [337.718, 5.353, 1.0820], [337.821, 5.263, 1.0984], [337.862, 5.153, 1.1148], [337.925, 5.046, 1.1311], [337.984, 4.928, 1.1475], [338.075, 4.786, 1.1639], [338.125, 4.650, 1.1803], [338.198, 4.516, 1.1967], [338.301, 4.380, 1.2131], [338.357, 4.311, 1.2295], [338.417, 4.228, 1.2459], [338.499, 4.068, 1.2623], [338.556, 3.952, 1.2787], [338.631, 3.829, 1.2951], [338.702, 3.697, 1.3115], [338.750, 3.586, 1.3279], [338.823, 3.487, 1.3443], [338.919, 3.344, 1.3607], [338.976, 3.207, 1.3770], [339.048, 3.131, 1.3934], [339.114, 2.968, 1.4098], [339.199, 2.876, 1.4262], [339.273, 2.733, 1.4426], [339.340, 2.626, 1.4590], [339.407, 2.542, 1.4754], [339.479, 2.422, 1.4918], [339.530, 2.278, 1.5082], [339.622, 2.184, 1.5246], [339.689, 2.056, 1.5410], [339.725, 1.974, 1.5574], [339.813, 1.849, 1.5738], [339.913, 1.730, 1.5902], [339.991, 1.631, 1.6066], [340.023, 1.496, 1.6230], [340.109, 1.417, 1.6393], [340.186, 1.297, 1.6557], [340.242, 1.197, 1.6721], [340.299, 1.075, 1.6885], [340.367, 0.959, 1.7049], [340.460, 0.878, 1.7213], [340.507, 0.782, 1.7377], [340.609, 0.544, 1.7541], [340.667, 0.477, 1.7705], [340.730, 0.354, 1.7869], [340.805, 0.281, 1.8033]], [[308.540, 34.335, 0.9959], [308.632, 34.295, 1.0122], [308.661, 34.227, 1.0286], [308.682, 34.147, 1.0450], [308.766, 34.089, 1.0614], [308.841, 34.019, 1.0778], [308.838, 33.941, 1.0942], [308.898, 33.884, 1.1106], [308.993, 33.821, 1.1270], [309.000, 33.747, 1.1434], [309.121, 33.669, 1.1598], [309.171, 33.601, 1.1762], [309.179, 33.521, 1.1926], [309.307, 33.454, 1.2090], [309.329, 33.362, 1.2254], [309.387, 33.306, 1.2418], [309.459, 33.231, 1.2581], [309.540, 33.168, 1.2745], [309.590, 33.094, 1.2909], [309.653, 33.010, 1.3073], [309.714, 32.933, 1.3237], [309.754, 32.850, 1.3401], [309.834, 32.780, 1.3565], [309.884, 32.701, 1.3729], [309.975, 32.628, 1.3893], [310.022, 32.556, 1.4057], [310.113, 32.477, 1.4221], [310.157, 32.421, 1.4385], [310.207, 32.329, 1.4549], [310.277, 32.243, 1.4713], [310.333, 32.177, 1.4877], [310.388, 32.111, 1.5040], [310.457, 32.020, 1.5204], [310.493, 31.941, 1.5368], [310.526, 31.877, 1.5532], [310.624, 31.797, 1.5696], [310.660, 31.712, 1.5860], [310.737, 31.626, 1.6024], [310.798, 31.573, 1.6188], [310.851, 31.502, 1.6352], [310.907, 31.412, 1.6516], [310.962, 31.329, 1.6680], [311.032, 31.208, 1.6844], [311.079, 31.167, 1.7008], [311.111, 31.092, 1.7172], [311.192, 31.020, 1.7336], [311.254, 30.943, 1.7499], [311.331, 30.822, 1.7663], [311.403, 30.805, 1.7827], [311.457, 30.699, 1.7991], [311.542, 30.646, 1.8155]], [14.11767, 49.05369, 102606.8], [14.24757, 48.98114, 90325.8]],
        ['18A08052', '2018-10-8 20:56:00', [[308.607, 15.553, 1.0164], [308.547, 15.460, 1.0328], [308.541, 15.327, 1.0492], [308.493, 15.207, 1.0656], [308.470, 15.034, 1.0820], [308.480, 14.941, 1.0984], [308.432, 14.821, 1.1148], [308.421, 14.734, 1.1311], [308.378, 14.567, 1.1475], [308.343, 14.419, 1.1639], [308.304, 14.319, 1.1803], [308.262, 14.151, 1.1967], [308.235, 14.023, 1.2131], [308.224, 13.936, 1.2295], [308.181, 13.767, 1.2459], [308.163, 13.659, 1.2623], [308.144, 13.551, 1.2787], [308.105, 13.450, 1.2951], [308.119, 13.308, 1.3115], [308.141, 13.186, 1.3279], [308.074, 13.071, 1.3443], [308.088, 12.928, 1.3607], [308.006, 12.772, 1.3770]], [[270.158, 40.947, 0.9632], [270.062, 40.870, 0.9796], [269.927, 40.798, 0.9960], [269.859, 40.762, 1.0124], [269.759, 40.655, 1.0288], [269.709, 40.602, 1.0452], [269.615, 40.525, 1.0616], [269.543, 40.459, 1.0780], [269.432, 40.399, 1.0944], [269.400, 40.329, 1.1108], [269.345, 40.247, 1.1272], [269.175, 40.180, 1.1435], [269.034, 40.050, 1.1599], [268.985, 39.997, 1.1763], [268.812, 39.902, 1.1927], [268.738, 39.808, 1.2091], [268.604, 39.707, 1.2255], [268.501, 39.676, 1.2419], [268.412, 39.600, 1.2583], [268.365, 39.547, 1.2747], [268.377, 39.502, 1.2911], [268.292, 39.454, 1.3075], [268.225, 39.390, 1.3239], [268.170, 39.280, 1.3403], [268.061, 39.192, 1.3567], [267.977, 39.145, 1.3731], [267.927, 39.064, 1.3894], [267.885, 39.040, 1.4058]], [13.80263, 49.46655, 87566.8], [13.82907, 49.44937, 77595.2]],
        ['18A08215', '2018-10-8 23:21:02', [[355.546, 20.860, 0.0664], [355.606, 20.775, 0.0828], [355.701, 20.636, 0.0992], [355.806, 20.461, 0.1156], [355.897, 20.328, 0.1320], [355.989, 20.195, 0.1484], [356.079, 20.062, 0.1648], [356.170, 19.927, 0.1811], [356.234, 19.837, 0.1975], [356.308, 19.703, 0.2139], [356.427, 19.530, 0.2303], [356.507, 19.382, 0.2467], [356.606, 19.247, 0.2631], [356.656, 19.110, 0.2795], [356.802, 19.000, 0.2959], [356.885, 18.828, 0.3123], [356.959, 18.691, 0.3287], [357.089, 18.488, 0.3451], [357.161, 18.373, 0.3615], [357.281, 18.174, 0.3779], [357.346, 18.072, 0.3943], [357.462, 17.949, 0.4107], [357.527, 17.760, 0.4270], [357.678, 17.578, 0.4434], [357.737, 17.488, 0.4598], [357.838, 17.359, 0.4762], [357.905, 17.146, 0.4926], [358.012, 17.058, 0.5090], [358.081, 16.908, 0.5254], [358.195, 16.750, 0.5418], [358.298, 16.597, 0.5582], [358.361, 16.460, 0.5746], [358.483, 16.265, 0.5910], [358.582, 16.101, 0.6074], [358.671, 15.959, 0.6238], [358.760, 15.817, 0.6402], [358.847, 15.675, 0.6566], [358.943, 15.592, 0.6730], [359.031, 15.431, 0.6893], [359.113, 15.284, 0.7057], [359.193, 15.160, 0.7221], [359.301, 14.991, 0.7385], [359.400, 14.858, 0.7549], [359.480, 14.677, 0.7713], [359.593, 14.549, 0.7877], [359.677, 14.411, 0.8041], [359.729, 14.219, 0.8205], [359.835, 14.105, 0.8369], [359.987, 13.960, 0.8533], [0.032, 13.838, 0.8697], [0.094, 13.675, 0.8861], [0.198, 13.584, 0.9025], [0.252, 13.458, 0.9189], [0.353, 13.334, 0.9352], [0.447, 13.190, 0.9516], [0.476, 13.120, 0.9680], [0.627, 12.917, 0.9844], [0.686, 12.776, 1.0008], [0.763, 12.594, 1.0172], [0.863, 12.469, 1.0336], [0.954, 12.349, 1.0500], [0.940, 12.344, 1.0664]], [[317.227, 47.473, 0.2762], [317.325, 47.444, 0.2926], [317.401, 47.371, 0.3090], [317.460, 47.367, 0.3254], [317.639, 47.305, 0.3417], [317.700, 47.226, 0.3581], [317.819, 47.168, 0.3745], [317.939, 47.085, 0.3909], [318.043, 47.022, 0.4073], [318.137, 47.043, 0.4237], [318.190, 46.949, 0.4401], [318.344, 46.891, 0.4565], [318.440, 46.837, 0.4729], [318.484, 46.778, 0.4893], [318.638, 46.695, 0.5057], [318.747, 46.621, 0.5221], [318.848, 46.582, 0.5385], [318.928, 46.498, 0.5549], [319.051, 46.479, 0.5713], [319.109, 46.400, 0.5876], [319.202, 46.345, 0.6040], [319.381, 46.272, 0.6204], [319.438, 46.168, 0.6368], [319.509, 46.143, 0.6532], [319.659, 46.084, 0.6696], [319.722, 45.995, 0.6860], [319.892, 45.905, 0.7024], [319.905, 45.836, 0.7188], [320.018, 45.801, 0.7352], [320.158, 45.727, 0.7516], [320.270, 45.692, 0.7680], [320.338, 45.593, 0.7844], [320.408, 45.568, 0.8008], [320.547, 45.493, 0.8172], [320.615, 45.418, 0.8335], [320.683, 45.344, 0.8499], [320.890, 45.269, 0.8663], [320.902, 45.199, 0.8827], [320.928, 45.160, 0.8991], [321.059, 45.119, 0.9155], [321.209, 45.049, 0.9319], [321.275, 44.950, 0.9483], [321.383, 44.890, 0.9647], [321.442, 44.825, 0.9811], [321.544, 44.799, 0.9975], [321.575, 44.725, 1.0139], [321.648, 44.666, 1.0303], [321.742, 44.625, 1.0467], [321.841, 44.550, 1.0631], [321.926, 44.470, 1.0795], [322.123, 44.345, 1.0958], [322.215, 44.280, 1.1122], [322.325, 44.185, 1.1286], [322.441, 44.105, 1.1450], [322.569, 44.088, 1.1614]], [14.02974, 49.48029, 104526.0], [14.25031, 49.25344, 86218.6]],
        ['18A08223', '2018-10-8 23:59:55', [[353.196, 8.492, 1.1618], [353.231, 8.335, 1.1782], [353.275, 8.355, 1.1946], [353.360, 8.202, 1.2110], [353.467, 8.042, 1.2274], [353.516, 7.891, 1.2438], [353.559, 7.815, 1.2602], [353.657, 7.574, 1.2766], [353.733, 7.520, 1.2929], [353.849, 7.356, 1.3093], [353.900, 7.301, 1.3257], [353.965, 7.096, 1.3421], [354.073, 7.066, 1.3585], [354.164, 6.900, 1.3749], [354.194, 6.792, 1.3913], [354.258, 6.648, 1.4077], [354.332, 6.500, 1.4241], [354.404, 6.377, 1.4405], [354.494, 6.270, 1.4569], [354.555, 6.151, 1.4733], [354.624, 5.993, 1.4897], [354.675, 5.878, 1.5061], [354.746, 5.755, 1.5225], [354.842, 5.635, 1.5388], [354.913, 5.512, 1.5552], [354.978, 5.403, 1.5716], [355.064, 5.227, 1.5880], [355.122, 5.134, 1.6044], [355.189, 5.001, 1.6208], [355.260, 4.878, 1.6372], [355.328, 4.721, 1.6536], [355.440, 4.642, 1.6700], [355.474, 4.487, 1.6864], [355.552, 4.386, 1.7028], [355.622, 4.264, 1.7192], [355.701, 4.163, 1.7356], [355.771, 4.041, 1.7520], [355.861, 3.912, 1.7684], [355.927, 3.780, 1.7847], [355.966, 3.611, 1.8011], [356.073, 3.523, 1.8175], [356.169, 3.380, 1.8339], [356.235, 3.249, 1.8503], [356.251, 3.172, 1.8667], [356.377, 3.018, 1.8831], [356.406, 2.913, 1.8995], [356.501, 2.830, 1.9159], [356.556, 2.703, 1.9323], [356.645, 2.575, 1.9487], [356.722, 2.476, 1.9651], [356.791, 2.356, 1.9815], [356.847, 2.206, 1.9979], [356.920, 2.097, 2.0143], [356.960, 2.081, 2.0306], [357.039, 1.900, 2.0470], [357.105, 1.747, 2.0634], [357.181, 1.707, 2.0798], [357.219, 1.599, 2.0962], [357.277, 1.542, 2.1126], [357.362, 1.325, 2.1290], [357.526, 1.159, 2.1454], [357.492, 1.103, 2.1618], [357.610, 1.024, 2.1782], [357.615, 0.952, 2.1946], [357.701, 0.851, 2.2110], [357.700, 0.794, 2.2274], [357.748, 0.603, 2.2438], [357.814, 0.567, 2.2602], [357.920, 0.378, 2.2766]], [[323.010, 33.235, 1.0375], [323.068, 33.186, 1.0539], [323.143, 33.155, 1.0703], [323.199, 33.086, 1.0867], [323.348, 33.023, 1.1031], [323.400, 32.893, 1.1195], [323.431, 32.775, 1.1359], [323.453, 32.695, 1.1523], [323.601, 32.652, 1.1687], [323.686, 32.557, 1.1851], [323.741, 32.421, 1.2015], [323.785, 32.349, 1.2179], [323.875, 32.267, 1.2343], [323.955, 32.200, 1.2506], [324.038, 32.106, 1.2670], [324.126, 32.004, 1.2834], [324.182, 31.910, 1.2998], [324.241, 31.855, 1.3162], [324.315, 31.731, 1.3326], [324.437, 31.635, 1.3490], [324.477, 31.545, 1.3654], [324.589, 31.465, 1.3818], [324.648, 31.365, 1.3982], [324.712, 31.277, 1.4146], [324.801, 31.171, 1.4310], [324.922, 31.096, 1.4474], [325.009, 30.990, 1.4638], [325.057, 30.907, 1.4802], [325.107, 30.843, 1.4965], [325.209, 30.753, 1.5129], [325.284, 30.645, 1.5293], [325.346, 30.559, 1.5457], [325.436, 30.422, 1.5621], [325.472, 30.337, 1.5785], [325.591, 30.283, 1.5949], [325.670, 30.188, 1.6113], [325.738, 30.089, 1.6277], [325.868, 29.970, 1.6441], [325.916, 29.883, 1.6605], [325.971, 29.807, 1.6769], [326.046, 29.739, 1.6933], [326.171, 29.604, 1.7097], [326.206, 29.540, 1.7261], [326.289, 29.433, 1.7424], [326.355, 29.313, 1.7588], [326.445, 29.261, 1.7752], [326.525, 29.114, 1.7916], [326.563, 29.044, 1.8080], [326.653, 28.902, 1.8244], [326.741, 28.851, 1.8408], [326.809, 28.769, 1.8572], [326.892, 28.660, 1.8736], [326.967, 28.565, 1.8900], [327.021, 28.463, 1.9064], [327.051, 28.386, 1.9228], [327.163, 28.242, 1.9392], [327.230, 28.139, 1.9556], [327.288, 28.097, 1.9720], [327.393, 28.009, 1.9883], [327.459, 27.907, 2.0047], [327.520, 27.836, 2.0211], [327.561, 27.711, 2.0375], [327.665, 27.603, 2.0539], [327.708, 27.542, 2.0703], [327.788, 27.411, 2.0867], [327.873, 27.314, 2.1031], [327.906, 27.251, 2.1195], [328.112, 27.117, 2.1359], [328.132, 27.057, 2.1523], [328.188, 26.923, 2.1687], [328.217, 26.890, 2.1851], [328.242, 26.841, 2.2015], [328.308, 26.734, 2.2179], [328.401, 26.617, 2.2343], [328.440, 26.474, 2.2506], [328.530, 26.429, 2.2670]], [13.57204, 49.32171, 112891.2], [13.86229, 49.00099, 88932.6]],
        ['18A08183', '2018-10-8 22:03:54', [[358.647, 8.286, 1.0046], [358.711, 8.142, 1.0210], [358.776, 8.031, 1.0374], [358.838, 7.912, 1.0538], [358.892, 7.772, 1.0702], [359.003, 7.642, 1.0866], [359.094, 7.543, 1.1030], [359.162, 7.386, 1.1194], [359.220, 7.233, 1.1358], [359.304, 7.092, 1.1522], [359.396, 6.971, 1.1686], [359.456, 6.852, 1.1850], [359.559, 6.680, 1.2014], [359.612, 6.599, 1.2178], [359.693, 6.482, 1.2342], [359.777, 6.318, 1.2505], [359.863, 6.188, 1.2669], [359.945, 6.049, 1.2833], [0.027, 5.910, 1.2997], [0.085, 5.792, 1.3161], [0.161, 5.667, 1.3325], [0.243, 5.505, 1.3489], [0.342, 5.359, 1.3653], [0.408, 5.239, 1.3817], [0.471, 5.085, 1.3981], [0.564, 4.954, 1.4145], [0.642, 4.840, 1.4309], [0.707, 4.720, 1.4473], [0.798, 4.612, 1.4637], [0.886, 4.449, 1.4801], [0.948, 4.298, 1.4964], [1.038, 4.168, 1.5128], [1.105, 4.082, 1.5292], [1.169, 3.964, 1.5456], [1.285, 3.824, 1.5620], [1.344, 3.697, 1.5784], [1.360, 3.588, 1.5948], [1.482, 3.468, 1.6112], [1.550, 3.315, 1.6276], [1.654, 3.226, 1.6440], [1.709, 3.068, 1.6604], [1.750, 2.950, 1.6768], [1.793, 2.887, 1.6932], [1.935, 2.749, 1.7096], [1.992, 2.624, 1.7260], [2.048, 2.545, 1.7423], [2.131, 2.343, 1.7587], [2.208, 2.199, 1.7751], [2.285, 2.101, 1.7915], [2.323, 2.029, 1.8079], [2.441, 1.847, 1.8243], [2.542, 1.695, 1.8407], [2.579, 1.669, 1.8571], [2.609, 1.557, 1.8735], [2.676, 1.438, 1.8899], [2.745, 1.380, 1.9063]], [[327.429, 37.968, 0.9655], [327.552, 37.916, 0.9819], [327.615, 37.886, 0.9982], [327.693, 37.811, 1.0146], [327.750, 37.720, 1.0310], [327.846, 37.631, 1.0474], [327.996, 37.529, 1.0638], [328.078, 37.437, 1.0802], [328.177, 37.370, 1.0966], [328.218, 37.286, 1.1130], [328.359, 37.126, 1.1294], [328.477, 37.075, 1.1458], [328.522, 36.974, 1.1622], [328.696, 36.903, 1.1786], [328.745, 36.785, 1.1950], [328.877, 36.721, 1.2114], [328.963, 36.643, 1.2278], [329.058, 36.494, 1.2441], [329.177, 36.427, 1.2605], [329.255, 36.330, 1.2769], [329.355, 36.239, 1.2933], [329.500, 36.117, 1.3097], [329.608, 35.994, 1.3261], [329.625, 35.935, 1.3425], [329.754, 35.820, 1.3589], [329.862, 35.735, 1.3753], [329.980, 35.608, 1.3917], [330.075, 35.520, 1.4081], [330.147, 35.426, 1.4245], [330.316, 35.327, 1.4409], [330.411, 35.232, 1.4573], [330.501, 35.154, 1.4737], [330.626, 35.025, 1.4900], [330.723, 34.916, 1.5064], [330.790, 34.832, 1.5228], [330.878, 34.704, 1.5392], [330.961, 34.643, 1.5556], [331.055, 34.536, 1.5720], [331.152, 34.412, 1.5884], [331.223, 34.299, 1.6048], [331.350, 34.187, 1.6212], [331.414, 34.098, 1.6376], [331.532, 34.018, 1.6540], [331.619, 33.921, 1.6704], [331.651, 33.824, 1.6868], [331.788, 33.695, 1.7032], [331.926, 33.552, 1.7196], [331.983, 33.489, 1.7360], [332.072, 33.420, 1.7523], [332.164, 33.281, 1.7687], [332.254, 33.143, 1.7851], [332.390, 33.100, 1.8015], [332.484, 32.934, 1.8179], [332.523, 32.892, 1.8343], [332.641, 32.760, 1.8507]], [14.06785, 49.20714, 108162.4], [14.27193, 49.00960, 91210.7]]
    ]
    
    for meteor in meteory:
        # Latitude, longitude, height above sea level, time of observation
        ondrejov = Station(lat=49.970222, lon=14.780208, height=524, time_zone=0, time=meteor[1], label='Ondřejov')
        kunzak = Station(lat=49.107290, lon=15.200930, height=656, time_zone=0, time=meteor[1], label='Kunžak')

        calculation = Meteor(meteor[0], ondrejov, kunzak, meteor[2], meteor[3], meteor[1])
        calculation.calculate_trajectories()
        calculation.plot_trajectory_geodetic()
        calculation.save_trajectory_gpx(meteor[4], meteor[5])
