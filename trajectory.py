from math import sin, cos, radians, sqrt, asin, acos, degrees, pi
import astropy.units as u
from astropy.time import Time
import numpy

from coordinates import *

def calculate_radiant(pointsA: list[list[float]], stationA: dict, pointsB: list[list[float]], stationB: dict) -> list[float]:
    """Calculates the radiant of the meteor according to Ceplecha (1987)

    Args:
        pointsA (list[list[float]]): meteor coordinates in ra and dec in decimal degrees from station A
        stationA dict: latitude, height and time of station B
        pointsB (list[list[float]]): meteor coordinates in ra and dec in decimal degrees from station A
        stationB dict: latitude, height and time of station B

    Returns:
        list[float]: right ascension and declination of meteor radiant
    """

    aa, ba, ca, xa, ya, za = calculate_station(pointsA, stationA)
    ab, bb, cb, xb, yb, zb = calculate_station(pointsB, stationB)
    
    d = sqrt((ba * cb - bb * ca) ** 2 + (ab * ca - aa * cb) ** 2 + (aa * bb - ab * ba) ** 2)

    Xi = (ba * cb - bb * ca) / d
    Eta = (ab * ca - aa * cb) / d
    Zeta = (aa * bb - ab * ba) / d

    angle = degrees(acos(abs(aa*ab + ba*bb + ca*cb)) / sqrt((aa**2+ba**2+ca**2)*(ab**2+bb**2+cb**2)))

    ra, dec = solve_goniometry(Xi, Eta, Zeta)
    # If the radiant is under the horizon, change sign of Xi, Eta, Zeta
    if world_to_altaz(ra, dec, stationA['lat'], stationA['lon'], stationA['height'], stationA['time'], stationA['time_zone'])[0] < 0:
        ra, dec = solve_goniometry(-Xi, -Eta, -Zeta)

    return ra, dec, angle

def calculate_station(points: float, station) -> list[float]:
    """Calculates station related variables according to Ceplecha (1987)

    Args:
        points (list[list[float]]): points of the given meteor
        station (list[float]): lat, lon, height and time at station

    Returns:
        list[float]: vectors (a, b, c) and (X, Y, Z)
    """

    localSiderealTime = calculate_sidereal_time(station['lat'], station['lon'], station['time'], station['time_zone'])

    # Calculate equation 7
    geocentricLatitude = station['lat'] - 0.1924240867 * sin(radians(2 * station['lat'])) + 0.000323122 * sin(radians(4 * station['lat'])) - 0.0000007235 * sin(radians(6 * station['lat']))
    R = sqrt(40680669.86 * (1 - 0.0133439554 * pow(sin(radians(station['lat'])), 2)) / (1 - 0.006694385096 * pow(sin(radians(station['lat'])), 2)))

    # Calculate equation 8
    X = (R + station['height']) * cos(radians(geocentricLatitude)) * cos(radians(localSiderealTime))
    Y = (R + station['height']) * cos(radians(geocentricLatitude)) * sin(radians(localSiderealTime))
    Z = (R + station['height']) * sin(radians(geocentricLatitude))

    # Calculate equation 9 for all meteor points
    XiEta, EtaZeta, EtaEta, XiZeta, XiXi = 0, 0, 0, 0, 0
    for point in points:
        Xi, Eta, Zeta = calculate_meteor_point(point[0], point[1])

        XiEta += Xi * Eta
        EtaZeta += Eta * Zeta
        EtaEta += Eta ** 2
        XiZeta += Xi * Zeta
        XiXi += Xi ** 2

    # Calculate equation 11
    adash = XiEta * EtaZeta - EtaEta * XiZeta
    bdash = XiEta * XiZeta - XiXi * EtaZeta
    cdash = XiXi * EtaEta - XiEta ** 2
    ddash = sqrt(adash ** 2 + bdash ** 2 + cdash ** 2)

    a = adash / ddash
    b = bdash / ddash
    c = cdash / ddash

    return [a, b, c, X, Y, Z]

def calculate_meteor_point(ra: float, dec: float) -> list[float]:
    """Calculates Xi, Eta and Zeta values from ra and dec values of meteor point

    Args:
        ra (float): right ascension in decimal degrees
        dec (float): declination in decimal degrees

    Returns:
        list[float]:  Geocentric vector Xi, Eta, Zeta
    """

    # Calculate equation 9
    Xi = cos(radians(dec)) * cos(radians(ra))
    Eta = cos(radians(dec)) * sin(radians(ra))
    Zeta = sin(radians(dec))

    return [Xi, Eta, Zeta]

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

    t = Time(time, location=(lat, lon)) - u.hour * time_zone
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

def solve_goniometry(Xi: float, Eta: float, Zeta: float) -> list[float]:
    """Solves equation 9
    
    Args:
        Vector (Xi, Eta, Zeta)
        
    Returns:
        list[float]: RA and Dec in decimal degrees
    """

    # Calculate dec
    declinations = [asin(Zeta), pi - asin(Zeta) if Zeta >= 0 else 2 * pi - asin(-Zeta)]
    for dec in declinations:
        # Skip if Dec is outside of it's domain
        if dec > 90 and dec < -90:
            break

        # Check for quadrants
        # quad 1 2 3 4
        # sin  + + - -
        # cos  + - - +

        # Float math can result in values slightly outside domains, round
        sinRA = round(Eta / cos(dec), 12)
        cosRA = round(Xi / cos(dec), 12)

        ra = None
        if sinRA >= 0 and cosRA >= 0:
            ra = asin(sinRA)
        if sinRA >= 0 and cosRA < 0:
            ra = pi - asin(sinRA)
        if sinRA < 0 and cosRA < 0:
            ra = pi - asin(sinRA)
        if sinRA < 0 and cosRA >= 0:
            ra = 2 * pi + asin(sinRA)

        if numpy.allclose((Xi, Eta, Zeta), (cos(dec)*cos(ra), cos(dec)*sin(ra), sin(dec))):
            print()
            return degrees(ra), degrees(dec)

if __name__ == '__main__':
    # Test calculation
    # client = AstrometryClient()
    # client.authenticate()

    # Latitude, longitude, height above sea level, time of observation
    ondrejov = {'lat': 14.784264, 'lon': 49.904682, 'height': 467, 'time': '2018-10-8 22:03:54', 'time_zone': 1}
    kunzak = {'lat': 15.190299, 'lon': 49.121249, 'height': 575, 'time': '2018-10-8 22:03:54', 'time_zone': 1}

    meteoryDir = './meteory/'

    meteorPathsOndrejov = [
        ['18a08183/2018-10-08-23-03-53m.jpg', '18a08183/2018-10-08-23-03-53m.txt'],
        ['18a08223/2018-10-08-23-29-55m.jpg', '18a08223/2018-10-08-23-29-55m.txt'],
        ['18A08052/2018-10-08-20-56-01m.jpg', '18A08052/2018-10-08-20-56-01m.txt'],
        ['18A08085/2018-10-08-21-38-32m.jpg', '18A08085/2018-10-08-21-38-32m.txt'],
        ['18A08215/2018-10-08-23-21-02m.jpg', '18A08215/2018-10-08-23-21-02m.txt'],
    ]
    meteorPathsKunzak = [
        ['18a08183/2018-10-08-23-03-53n.jpg', '18a08183/2018-10-08-23-03-53n.txt'],
        ['18a08223/2018-10-08-23-29-55n.jpg', '18a08223/2018-10-08-23-29-55n.txt'],
        ['18A08052/2018-10-08-20-56-00n.jpg', '18A08052/2018-10-08-20-56-00n.txt'],
        ['18A08085/2018-10-08-21-38-32n.jpg', '18A08085/2018-10-08-21-38-32n.txt'],
        ['18A08215/2018-10-08-23-21-02n.jpg', '18A08215/2018-10-08-23-21-02n.txt'],
    ]

    radiants = [
        [262.1776, 56.0219],
        [260.8404, 55.8957],
        [320.8006, 58.7769],
        [271.9055, 53.8931],
        [262.7624, 56.0977],
    ]

    # for i in range(len(meteorPathsOndrejov)):
    #     preprocess(meteoryDir + meteorPathsOndrejov[i][0], meteoryDir + meteorPathsOndrejov[i][1], 'tmp1.jpg')
    #     meteorOndrejov = get_meteor_coordinates(client, 'tmp1.jpg', meteoryDir + meteorPathsOndrejov[i][1])

    #     preprocess(meteoryDir + meteorPathsKunzak[i][0], meteoryDir + meteorPathsKunzak[i][1], 'tmp1.jpg')
    #     meteorKunzak = get_meteor_coordinates(client, 'tmp1.jpg', meteoryDir + meteorPathsKunzak[i][1])

    meteorOndrejov = [[358.647, 8.286], [358.711, 8.142], [358.776, 8.031], [358.838, 7.912], [358.892, 7.772], [359.003, 7.642], [359.094, 7.543], [359.162, 7.386], [359.220, 7.233], [359.304, 7.092], [359.396, 6.971], [359.456, 6.852], [359.559, 6.680], [359.612, 6.599], [359.693, 6.482], [359.777, 6.318], [359.863, 6.188], [359.945, 6.049], [0.027, 5.910], [0.085, 5.792], [0.161, 5.667], [0.243, 5.505], [0.342, 5.359], [0.408, 5.239], [0.471, 5.085], [0.564, 4.954], [0.642, 4.840], [0.707, 4.720], [0.798, 4.612], [0.886, 4.449], [0.948, 4.298], [1.038, 4.168], [1.105, 4.082], [1.169, 3.964], [1.285, 3.824], [1.344, 3.697], [1.360, 3.588], [1.482, 3.468], [1.550, 3.315], [1.654, 3.226], [1.709, 3.068], [1.750, 2.950], [1.793, 2.887], [1.935, 2.749], [1.992, 2.624], [2.048, 2.545], [2.131, 2.343], [2.208, 2.199], [2.285, 2.101], [2.323, 2.029], [2.441, 1.847], [2.542, 1.695], [2.579, 1.669], [2.609, 1.557], [2.676, 1.438], [2.745, 1.380]]
    meteorKunzak = [[327.429, 37.968],[327.552, 37.916],[327.615, 37.886],[327.693, 37.811],[327.750, 37.720],[327.846, 37.631],[327.996, 37.529],[328.078, 37.437],[328.177, 37.370],[328.218, 37.286],[328.359, 37.126],[328.477, 37.075],[328.522, 36.974],[328.696, 36.903],[328.745, 36.785],[328.877, 36.721],[328.963, 36.643],[329.058, 36.494],[329.177, 36.427],[329.255, 36.330],[329.355, 36.239],[329.500, 36.117],[329.608, 35.994],[329.625, 35.935],[329.754, 35.820],[329.862, 35.735],[329.980, 35.608],[330.075, 35.520],[330.147, 35.426],[330.316, 35.327],[330.411, 35.232],[330.501, 35.154],[330.626, 35.025],[330.723, 34.916],[330.790, 34.832],[330.878, 34.704],[330.961, 34.643],[331.055, 34.536],[331.152, 34.412],[331.223, 34.299],[331.350, 34.187],[331.414, 34.098],[331.532, 34.018],[331.619, 33.921],[331.651, 33.824],[331.788, 33.695],[331.926, 33.552],[331.983, 33.489],[332.072, 33.420],[332.164, 33.281],[332.254, 33.143],[332.390, 33.100],[332.484, 32.934],[332.523, 32.892],[332.641, 32.760]]

    ra, dec, angle = calculate_radiant(meteorOndrejov, ondrejov, meteorKunzak, kunzak)
    print([ra, dec], radiants[0])
    print(angle)

    # Plot the meteor trajectory and radiant
    import matplotlib.pyplot as plot
    fig, ax = plot.subplots()

    x, y = [], []
    for i in meteorOndrejov:
        ax.scatter(i[0], i[1], color = 'b')
        x.append(i[0])
        y.append(i[1])
    ax.plot(x, y)
    
    x, y = [], []
    for i in meteorKunzak:
        ax.scatter(i[0], i[1], color = 'y')
        x.append(i[0])
        y.append(i[1])
    ax.plot(x, y)

    ax.scatter(ra, dec, color = 'r')
    ax.scatter(radiants[0][0], radiants[0][1], color = 'm')

    plot.show()
