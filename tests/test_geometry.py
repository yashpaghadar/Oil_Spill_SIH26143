"""Unit tests for geometry, distance, and polygon utilities."""

import math
import unittest
from oiled.utils.geometry import (
    haversine_distance_km,
    meters_to_lat_lon_displacement,
    compute_centroid,
    compute_polygon_area_perimeter_km,
    compute_orientation_degrees,
    compute_convex_hull,
    to_geojson_polygon,
)


class TestGeometryUtils(unittest.TestCase):
    def test_haversine_distance(self):
        # Mumbai (72.8777, 19.0760) to Goa (73.8567, 15.2993) is ~435 km
        dist = haversine_distance_km(72.8777, 19.0760, 73.8567, 15.2993)
        self.assertAlmostEqual(dist, 435.0, delta=20.0)

    def test_meters_to_lat_lon(self):
        dlon, dlat = meters_to_lat_lon_displacement(111139.0, 111139.0, ref_lat=0.0)
        self.assertAlmostEqual(dlat, 1.0, places=4)
        self.assertAlmostEqual(dlon, 1.0, places=4)

    def test_polygon_area(self):
        # 0.1 deg x 0.1 deg box near equator: approx 11.1 km x 11.1 km = ~123 km^2
        box = [(0.0, 0.0), (0.1, 0.0), (0.1, 0.1), (0.0, 0.1), (0.0, 0.0)]
        area, perim = compute_polygon_area_perimeter_km(box)
        self.assertAlmostEqual(area, 123.0, delta=10.0)
        self.assertGreater(perim, 40.0)

    def test_convex_hull(self):
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 0.5), (0.0, 1.0), (1.0, 1.0)]
        hull = compute_convex_hull(points)
        # Should enclose all points and form a closed polygon
        self.assertEqual(hull[0], hull[-1])
        self.assertEqual(len(hull), 5)  # 4 vertices + 1 closing point

    def test_orientation(self):
        # Diagonal slick from (0,0) to (1,1) oriented NE (~45 deg)
        line_pts = [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0)]
        angle = compute_orientation_degrees(line_pts)
        self.assertAlmostEqual(angle, 45.0, delta=5.0)


if __name__ == "__main__":
    unittest.main()
