from math import sin, cos, radians, sqrt, asin, atan

from coordinates import *

def calculateRadiant(pointsA: list[list[float]], stationA: list[float], pointsB: list[list[float]], stationB: list[float]) -> list[float]:
    """Calculates the radiant of the meteor according to Ceplecha (1987)

    Arguments:
        pointsA (list[list[float]]): meteor coordinates in ra and dec in decimal degrees from station A
        stationA (list[float]): latitude, height and local siderial time of station B
        pointsB (list[list[float]]): meteor coordinates in ra and dec in decimal degrees from station A
        stationB (list[float]): latitude, height and local siderial time of station B

    Returns:
        list[float]: right ascension and declination of meteor radiant
    """

    aa, ba, ca, xa, ya, za = calculateStation(pointsA, stationA[0], stationA[1], stationA[2])
    ab, bb, cb, xb, yb, zb = calculateStation(pointsB, stationB[0], stationB[1], stationB[2])
    
    d = sqrt((ba * cb - bb * ca) ** 2 + (ab * ca - aa * cb) ** 2 + (aa * bb - ab * ba) ** 2)

    Xi = (ba * cb - bb * ca) / d
    Eta = (ab * ca - aa * cb) / d
    Zeta = (aa * bb - ab * ba) / d

    ra = atan(Eta/Xi)
    dec = asin(Zeta)

    return [ra, dec]

def calculateStation(points: float, latitude: float, height: float, localSiderialTime: float) -> list[float]:
    """Calculates station related variables according to Ceplecha (1987)

    Arguments:
        points (list[list[float]]): points of the given meteor
        latitude (float): latitude of the observatory in decimal degrees
        height (float): height of the observatory above sea level
        localSiderialTime (float): local siderial time in decimal degrees

    Returns:
        list[float]: values a, b and c
    """

    # Calculate equation 7
    geocentricLatitude = latitude - 0.1924240867 * sin(radians(2 * latitude)) + 0.000323122 * sin(radians(4 * latitude)) - 0.0000007235 * sin(radians(6 * latitude))
    R = sqrt(40680669 * 86 * (1 - 0.0133439554 * pow(sin(radians(latitude), 2))) / (1 - 0.006694385096))

    # Calculate equation 8
    X = (R + height) * cos(radians(geocentricLatitude))*cos(radians(localSiderialTime))
    Y = (R + height) * cos(radians(geocentricLatitude))*sin(radians(localSiderialTime))
    Z = (R + height) * sin(radians(geocentricLatitude))

    # Calculate equation 9 for all meteor points
    XiEta, EtaZeta, EtaEta, XiZeta, XiXi = 0, 0, 0, 0, 0
    for point in points:
        Xi, Eta, Zeta = calculateMeteorPoint(point[0], point[1])

        XiEta += Xi * Eta
        EtaZeta += Eta * Zeta
        EtaEta += Eta ** 2
        XiZeta += Xi * Zeta
        XiXi += Xi ** 2

    # Calculate equation 11
    adash = XiEta * EtaZeta - EtaEta * XiZeta
    bdash = XiEta * XiZeta - XiXi * EtaZeta
    cdash = XiXi
    ddash = sqrt(adash ** 2 + bdash ** 2 + cdash ** 2)

    a = adash / ddash
    b = bdash / ddash
    c = cdash / ddash
    
    return [a, b, c, X, Y, Z]

def calculateMeteorPoint(ra: float, dec: float):
    """Calculates Xi, Eta and Zeta values from ra and dec values of meteor point

    Attributes:
        ra (float): right ascension in decimal degrees
        dec (float): declination in decimal degrees
    """

    # Calculate equation 9
    Xi = cos(radians(dec))*cos(radians(ra))
    Eta = cos(radians(dec))*cos(radians(ra))
    Zeta = sin(radians(dec))

    return [Xi, Eta, Zeta]

if __name__ == '__main__':
    # Test calculation
    client = AstrometryClient()
    client.authenticate()

    meteorOndrejov = get_meteor_coordinates(client, './meteory/18a08183/2018-10-08-23-03-53m.jpg', './meteory/18a08183/2018-10-08-23-03-53m.txt')
    meteorKunzak = get_meteor_coordinates(client, './meteory/18a08183/2018-10-08-23-03-53n.jpg', './meteory/18a08183/2018-10-08-23-03-53n.txt')

    # Latitude, height above sea level, sidereal time
    ondrejov = [14.784264, 467, 349.153338135]
    kunzak = [15.190299, 575, 349.558611371]

    print(calculateRadiant(meteorOndrejov, ondrejov, meteorKunzak, kunzak))
