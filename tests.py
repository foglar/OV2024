from trajectory import *
import numpy

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

    assert numpy.allclose(point, calculated_point), f'Should be {point}'

def test_radiant_calculation() -> None:
    """Tests the radiant calculation procedure"""

    radiant = [262.1776, 56.0219]
    Q = 7.06

    # Latitude, longitude, height above sea level, time of observation
    ondrejov = {'lon': 14.784264, 'lat': 49.904682, 'height': 467, 'time': '2018-10-8 22:03:54', 'time_zone': 1}
    kunzak = {'lon': 15.190299, 'lat': 49.121249, 'height': 575, 'time': '2018-10-8 22:03:54', 'time_zone': 1}

    # Precomputed ra and dec values
    meteor_ondrejov = [[358.647, 8.286], [358.711, 8.142], [358.776, 8.031], [358.838, 7.912], [358.892, 7.772], [359.003, 7.642], [359.094, 7.543], [359.162, 7.386], [359.220, 7.233], [359.304, 7.092], [359.396, 6.971], [359.456, 6.852], [359.559, 6.680], [359.612, 6.599], [359.693, 6.482], [359.777, 6.318], [359.863, 6.188], [359.945, 6.049], [0.027, 5.910], [0.085, 5.792], [0.161, 5.667], [0.243, 5.505], [0.342, 5.359], [0.408, 5.239], [0.471, 5.085], [0.564, 4.954], [0.642, 4.840], [0.707, 4.720], [0.798, 4.612], [0.886, 4.449], [0.948, 4.298], [1.038, 4.168], [1.105, 4.082], [1.169, 3.964], [1.285, 3.824], [1.344, 3.697], [1.360, 3.588], [1.482, 3.468], [1.550, 3.315], [1.654, 3.226], [1.709, 3.068], [1.750, 2.950], [1.793, 2.887], [1.935, 2.749], [1.992, 2.624], [2.048, 2.545], [2.131, 2.343], [2.208, 2.199], [2.285, 2.101], [2.323, 2.029], [2.441, 1.847], [2.542, 1.695], [2.579, 1.669], [2.609, 1.557], [2.676, 1.438], [2.745, 1.380]]
    meteor_kunzak = [[327.429, 37.968],[327.552, 37.916],[327.615, 37.886],[327.693, 37.811],[327.750, 37.720],[327.846, 37.631],[327.996, 37.529],[328.078, 37.437],[328.177, 37.370],[328.218, 37.286],[328.359, 37.126],[328.477, 37.075],[328.522, 36.974],[328.696, 36.903],[328.745, 36.785],[328.877, 36.721],[328.963, 36.643],[329.058, 36.494],[329.177, 36.427],[329.255, 36.330],[329.355, 36.239],[329.500, 36.117],[329.608, 35.994],[329.625, 35.935],[329.754, 35.820],[329.862, 35.735],[329.980, 35.608],[330.075, 35.520],[330.147, 35.426],[330.316, 35.327],[330.411, 35.232],[330.501, 35.154],[330.626, 35.025],[330.723, 34.916],[330.790, 34.832],[330.878, 34.704],[330.961, 34.643],[331.055, 34.536],[331.152, 34.412],[331.223, 34.299],[331.350, 34.187],[331.414, 34.098],[331.532, 34.018],[331.619, 33.921],[331.651, 33.824],[331.788, 33.695],[331.926, 33.552],[331.983, 33.489],[332.072, 33.420],[332.164, 33.281],[332.254, 33.143],[332.390, 33.100],[332.484, 32.934],[332.523, 32.892],[332.641, 32.760]]

    # Calculate radiant and Q angle
    meteor = Meteor(ondrejov, kunzak, meteor_ondrejov, meteor_kunzak, [], [])

    ra, dec = meteor.get_radiant()
    angle = meteor.get_Q_angle()

    # Check result
    assert numpy.allclose([ra, dec],radiant), f'Should be {radiant}'
    assert numpy.isclose(angle, Q), f'Should be {Q}'

def test_goniometry_solver():
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

if __name__ == '__main__':
    test_goniometry_solver()
    test_solve_plane_intersection()
    test_radiant_calculation()
    print('Tests passed')