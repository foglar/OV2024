from math import sin, cos, radians, sqrt, asin, atan

from coordinates import *

def calculate_radiant(pointsA: list[list[float]], stationA: list[float], pointsB: list[list[float]], stationB: list[float]) -> list[float]:
    """Calculates the radiant of the meteor according to Ceplecha (1987)

    Arguments:
        pointsA (list[list[float]]): meteor coordinates in ra and dec in decimal degrees from station A
        stationA (list[float]): latitude, height and local siderial time of station B
        pointsB (list[list[float]]): meteor coordinates in ra and dec in decimal degrees from station A
        stationB (list[float]): latitude, height and local siderial time of station B

    Returns:
        list[float]: right ascension and declination of meteor radiant
    """

    aa, ba, ca, xa, ya, za = calculate_station(pointsA, stationA[0], stationA[1], stationA[2])
    ab, bb, cb, xb, yb, zb = calculate_station(pointsB, stationB[0], stationB[1], stationB[2])
    
    d = sqrt((ba * cb - bb * ca) ** 2 + (ab * ca - aa * cb) ** 2 + (aa * bb - ab * ba) ** 2)

    Xi = (ba * cb - bb * ca) / d
    Eta = (ab * ca - aa * cb) / d
    Zeta = (aa * bb - ab * ba) / d

    ra = atan(Eta/Xi)
    dec = asin(Zeta)

    return [ra, dec]

def calculate_station(points: float, latitude: float, height: float, localSiderialTime: float) -> list[float]:
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
    R = sqrt(40680669 * 86 * (1 - 0.0133439554 * pow(sin(radians(latitude)), 2)) / (1 - 0.006694385096))

    # Calculate equation 8
    X = (R + height) * cos(radians(geocentricLatitude))*cos(radians(localSiderialTime))
    Y = (R + height) * cos(radians(geocentricLatitude))*sin(radians(localSiderialTime))
    Z = (R + height) * sin(radians(geocentricLatitude))

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
    cdash = XiXi
    ddash = sqrt(adash ** 2 + bdash ** 2 + cdash ** 2)

    a = adash / ddash
    b = bdash / ddash
    c = cdash / ddash
    
    return [a, b, c, X, Y, Z]

def calculate_meteor_point(ra: float, dec: float):
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

def preprocess(img_path: str, data_path: str, tmp_path: str) -> None:
    """Image preprocessing for astrometry. Masks out space around sky view and meteor
    
    Args:
        img_path (str): The path to the image to mask.
        data_path (str): The path to data.txt file describing meteor.
        tmp_path (str): Path, where the masked image should be saved.

    Retruns:
        None
    """

    import cv2, numpy

    image = cv2.imread(img_path)

    mask = numpy.zeros(image.shape, dtype=numpy.uint8)
    mask = cv2.circle(mask, (image.shape[1] // 2, image.shape[0] // 2), image.shape[0] // 2, (255, 255, 255), -1)

    meteor = load_meteors(data_path)
    for point in meteor[0].pixels:
        mask = cv2.circle(mask, (int(point[0]), int(point[1])), 3, (0, 0, 0), -1)

    cv2.imwrite(tmp_path, cv2.bitwise_and(mask, image))

if __name__ == '__main__':
    # Test calculation
    client = AstrometryClient()
    client.authenticate()

    # preprocess('./meteory/18a08183/2018-10-08-23-03-53m.jpg', './meteory/18a08183/2018-10-08-23-03-53m.txt', 'tmp1.jpg')
    # meteorOndrejov = get_meteor_coordinates(client, 'tmp1.jpg', './meteory/18a08183/2018-10-08-23-03-53m.txt')
    meteorOndrejov = [[358.5777139871662, 5.971324665640321], [358.6504312221906, 5.831861098827377], [358.77842383123294, 5.6696315174979155], [358.8326082420238, 5.5380380312590445], [358.88678277639434, 5.406525428964242], [358.9787925814164, 5.36857506053104], [359.07884752135516, 5.218294147006351], [359.17881536505325, 5.068182632520112], [359.23284384174826, 4.9370780602415705], [359.3515090246942, 4.833937911378646], [359.42342710878967, 4.659481650665034], [359.5051456255217, 4.5535312170984925], [359.57780382971504, 4.469497558023422], [359.64993561844295, 4.331466943493592], [359.7311527103091, 4.18984945510145], [359.8305438335934, 4.040966253633225], [359.90297404444254, 3.9573387337643506], [0.029050797866034372, 3.7437882320182143]]

    # preprocess('./meteory/18a08183/2018-10-08-23-03-53n.jpg', './meteory/18a08183/2018-10-08-23-03-53n.txt', 'tmp1.jpg')
    # meteorKunzak = get_meteor_coordinates(client, 'tmp1.jpg', './meteory/18a08183/2018-10-08-23-03-53n.txt')
    meteorKunzak = [[328.1597069832155, 37.053787325732166], [328.3402383901155, 36.90708235404924], [328.4617709161041, 36.74411186962826], [328.55103654515426, 36.67097761814034], [328.6975465924236, 36.61427570399938], [328.72863854978453, 36.52486571142832], [328.9050094249381, 36.378967973255754], [328.9355636507618, 36.28985657919], [329.08015858838144, 36.23329074576101], [329.19720589814045, 36.07171650554443], [329.283816819975, 35.999118028951216], [329.3995362487815, 35.838064408089295], [329.48534557167426, 35.765683429444415], [329.65032484537335, 35.638738174672206], [329.6847729317717, 35.533000887804505], [329.8256319495132, 35.47677332577176], [329.9940206042571, 35.332696530535664], [330.0219257591962, 35.245000183573445], [330.1887676420967, 35.101389083590796], [330.21618432460895, 35.0140119748251], [330.3679939909516, 34.91444608478159], [330.5190273750478, 34.81497228029015], [330.55897237616466, 34.684576998880715], [330.7218458147565, 34.54209923937315], [330.77271457857, 34.483324369189155], [330.8965036556135, 34.356711060376256], [331.0569801128769, 34.21491470918202], [331.2288747917939, 34.03046332726654]]

    # Latitude, height above sea level, sidereal time
    ondrejov = [14.784264, 467, 349.153338135]
    kunzak = [15.190299, 575, 349.558611371]

    print(calculate_radiant(meteorOndrejov, ondrejov, meteorKunzak, kunzak))
