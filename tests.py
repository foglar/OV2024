from trajectory import *
import numpy

def test_fixed_wcs_astrometry():
    """Tests the fixed WCS astrometry calculation"""

    from astrometry import AstrometryClient
    from station import Station
    from coordinates import download_wcs_file

    client = AstrometryClient()
    client.authenticate()

    time = Time('2024-01-08 21:35:44')
    kunzak = Station(lat=49.107290, lon=15.200930, height=656,
                     time_zone=0, time='2024-01-08 21:35:44', label='Kunžak',
                     wcs_path='calibration.wcs', wcs_time=Time('2024-01-08 23:24:54'))

    # Calculate meteor coordinates from WCS from the same image
    world_a = get_meteor_coordinates(client, './data/meteory/Kunzak/2024-01-08-21-35-44/2024-01-08-21-35-44.jpg', './data/meteory/Kunzak/2024-01-08-21-35-44/data.txt', kunzak, time)

    # Calculate meteor coordinates from a different image
    download_wcs_file(client, './data/meteory/Kunzak/2024-01-08-23-24-54/2024-01-08-23-24-54.jpg')
    world_b = get_meteor_coordinates_fixed('./data/meteory/Kunzak/2024-01-08-21-35-44/data.txt', kunzak, time)

    # Check the results
    for i in range(len(world_a)):
        assert numpy.allclose(world_a[i], world_b[i]), \
               f'{world_a[i]} is not {world_b[i]}'

def test_solve_plane_intersection():
    """Tests the plane intersection calculation function"""

    from random import random

    # Choose random plane slopes
    plane_a = [random() - 0.5, random() - 0.5, random() - 0.5]
    plane_b = [random() - 0.5, random() - 0.5, random() - 0.5]
    plane_c = [random() - 0.5, random() - 0.5, random() - 0.5]

    # Choose random point for planes to intersect in
    point = [random() - 0.5, random() - 0.5, random() - 0.5]

    # Calculate d values for planes
    plane_a.append(-(plane_a[0]*point[0] + plane_a[1]*point[1] + plane_a[2]*point[2]))
    plane_b.append(-(plane_b[0]*point[0] + plane_b[1]*point[1] + plane_b[2]*point[2]))
    plane_c.append(-(plane_c[0]*point[0] + plane_c[1]*point[1] + plane_c[2]*point[2]))

    # Calculate the intersection
    calculated_point = solve_plane_intersection(plane_a, plane_b, plane_c)

    assert numpy.allclose(point, calculated_point), \
           f'Should be {point}, not {calculated_point}'

def test_radiant_calculation() -> None:
    """Tests the radiant calculation procedure"""

    radiant = [266.7788, 59.4235]
    errors = [1.1839, 0.0592]
    Q = 7.06

    # Latitude, longitude, height above sea level, time of observation
    ondrejov = Station(lat=49.970222, lon=14.780208, height=524, time_zone=1)
    kunzak = Station(lat=49.107290, lon=15.200930, height=656, time_zone=1)

    time = '2018-10-8 22:03:54'

    # Precomputed ra and dec values
    meteor_ondrejov = [[358.647, 8.286, 1.0046], [358.711, 8.142, 1.0210], [358.776, 8.031, 1.0374], [358.838, 7.912, 1.0538], [358.892, 7.772, 1.0702], [359.003, 7.642, 1.0866], [359.094, 7.543, 1.1030], [359.162, 7.386, 1.1194], [359.220, 7.233, 1.1358], [359.304, 7.092, 1.1522], [359.396, 6.971, 1.1686], [359.456, 6.852, 1.1850], [359.559, 6.680, 1.2014], [359.612, 6.599, 1.2178], [359.693, 6.482, 1.2342], [359.777, 6.318, 1.2505], [359.863, 6.188, 1.2669], [359.945, 6.049, 1.2833], [0.027, 5.910, 1.2997], [0.085, 5.792, 1.3161], [0.161, 5.667, 1.3325], [0.243, 5.505, 1.3489], [0.342, 5.359, 1.3653], [0.408, 5.239, 1.3817], [0.471, 5.085, 1.3981], [0.564, 4.954, 1.4145], [0.642, 4.840, 1.4309], [0.707, 4.720, 1.4473], [0.798, 4.612, 1.4637], [0.886, 4.449, 1.4801], [0.948, 4.298, 1.4964], [1.038, 4.168, 1.5128], [1.105, 4.082, 1.5292], [1.169, 3.964, 1.5456], [1.285, 3.824, 1.5620], [1.344, 3.697, 1.5784], [1.360, 3.588, 1.5948], [1.482, 3.468, 1.6112], [1.550, 3.315, 1.6276], [1.654, 3.226, 1.6440], [1.709, 3.068, 1.6604], [1.750, 2.950, 1.6768], [1.793, 2.887, 1.6932], [1.935, 2.749, 1.7096], [1.992, 2.624, 1.7260], [2.048, 2.545, 1.7423], [2.131, 2.343, 1.7587], [2.208, 2.199, 1.7751], [2.285, 2.101, 1.7915], [2.323, 2.029, 1.8079], [2.441, 1.847, 1.8243], [2.542, 1.695, 1.8407], [2.579, 1.669, 1.8571], [2.609, 1.557, 1.8735], [2.676, 1.438, 1.8899], [2.745, 1.380, 1.9063]]
    meteor_kunzak = [[327.429, 37.968, 0.9655], [327.552, 37.916, 0.9819], [327.615, 37.886, 0.9982], [327.693, 37.811, 1.0146], [327.750, 37.720, 1.0310], [327.846, 37.631, 1.0474], [327.996, 37.529, 1.0638], [328.078, 37.437, 1.0802], [328.177, 37.370, 1.0966], [328.218, 37.286, 1.1130], [328.359, 37.126, 1.1294], [328.477, 37.075, 1.1458], [328.522, 36.974, 1.1622], [328.696, 36.903, 1.1786], [328.745, 36.785, 1.1950], [328.877, 36.721, 1.2114], [328.963, 36.643, 1.2278], [329.058, 36.494, 1.2441], [329.177, 36.427, 1.2605], [329.255, 36.330, 1.2769], [329.355, 36.239, 1.2933], [329.500, 36.117, 1.3097], [329.608, 35.994, 1.3261], [329.625, 35.935, 1.3425], [329.754, 35.820, 1.3589], [329.862, 35.735, 1.3753], [329.980, 35.608, 1.3917], [330.075, 35.520, 1.4081], [330.147, 35.426, 1.4245], [330.316, 35.327, 1.4409], [330.411, 35.232, 1.4573], [330.501, 35.154, 1.4737], [330.626, 35.025, 1.4900], [330.723, 34.916, 1.5064], [330.790, 34.832, 1.5228], [330.878, 34.704, 1.5392], [330.961, 34.643, 1.5556], [331.055, 34.536, 1.5720], [331.152, 34.412, 1.5884], [331.223, 34.299, 1.6048], [331.350, 34.187, 1.6212], [331.414, 34.098, 1.6376], [331.532, 34.018, 1.6540], [331.619, 33.921, 1.6704], [331.651, 33.824, 1.6868], [331.788, 33.695, 1.7032], [331.926, 33.552, 1.7196], [331.983, 33.489, 1.7360], [332.072, 33.420, 1.7523], [332.164, 33.281, 1.7687], [332.254, 33.143, 1.7851], [332.390, 33.100, 1.8015], [332.484, 32.934, 1.8179], [332.523, 32.892, 1.8343], [332.641, 32.760, 1.8507]]

    # Calculate radiant and Q angle
    meteor = Meteor('test', [ondrejov, kunzak], [meteor_ondrejov, meteor_kunzak], Time(time))

    ra, dec = meteor.get_radiant()
    angle = meteor.get_Q_angle()

    # Check results
    # Right ascension
    assert numpy.isclose(ra, radiant[0], atol=errors[0]), \
           f'Should be {radiant[0]}, not {ra}'
    # Declination
    assert numpy.isclose(dec, radiant[1], atol=errors[1]), \
           f'Should be {radiant[1]}, not {dec}'
    # Q Angle
    assert numpy.isclose(angle, Q),\
           f'Should be {Q}, not {angle}'

def test_goniometry_solver():
    """Tests calculate_meteor_point and solve_goniometry functions"""

    from random import random

    # Test a couple of values
    for _ in range(1000):
        ra, dec = round(random() * 360, 4), round(random() * 180 - 90, 4)

        # Calculate xi, eta and zeta values and back
        xi, eta, zeta = calculate_meteor_point((ra, dec))
        calculated = solve_goniometry((xi, eta, zeta))

        # Test
        assert numpy.allclose((ra, dec), calculated), \
               f'Should be {(ra, dec)}, not {calculated}'

def test_meteor_calculation():
    """Tests the fixed astrometry and calculation procedures"""

    time = Time('2024-01-08 23:52:57')
    ondrejov = Station(lat=49.970222,
                       lon=14.780208,
                       height=524,
                       time_zone=0,
                       time='2024-01-08 23:52:57',
                       label='Ondřejov',
                       wcs_path='ondrejov.wcs',
                       wcs_time=Time('2024-01-08 21:35:44'))

    kunzak = Station(lat=49.107290,
                     lon=15.200930,
                     height=656,
                     time_zone=0,
                     time='2024-01-08 23:52:57',
                     label='Kunžak',
                     wcs_path='kunzak.wcs',
                     wcs_time=Time('2024-01-08 21:35:44'))

    data_paths = [
        './data/meteory/Ondrejov/2024-01-08-23-52-57/data.txt',
        './data/meteory/Kunzak/2024-01-08-23-52-57/data.txt',
    ]

    calculation: Meteor = Meteor.from_astrometry_fixed('test',
                                                       [ondrejov, kunzak],
                                                       data_paths,
                                                       time)

    calculation.calculate_trajectories()
    calculation.calculate_radiant()
    calculation.plot_trajectory_geodetic()
    calculation.plot_velocities_along_trajectories()

if __name__ == '__main__':
    test_meteor_calculation()
    test_fixed_wcs_astrometry()
    test_goniometry_solver()
    test_solve_plane_intersection()
    test_radiant_calculation()
    print('Tests passed')