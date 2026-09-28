"""Geospatial and geometric utilities for oil spill detection, drift envelopes, and AIS tracks."""

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

EARTH_RADIUS_KM = 6371.0
METERS_PER_DEG_LAT = 111139.0


def haversine_distance_km(
    lon1: float, lat1: float, lon2: float, lat2: float
) -> float:
    """Calculate the great-circle distance between two points in kilometers."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


def meters_to_lat_lon_displacement(
    dx_meters: float, dy_meters: float, ref_lat: float
) -> Tuple[float, float]:
    """Convert eastward (dx) and northward (dy) displacements in meters to (dlon, dlat) in degrees."""
    dlat = dy_meters / METERS_PER_DEG_LAT
    cos_lat = math.cos(math.radians(ref_lat))
    if abs(cos_lat) < 1e-6:
        cos_lat = 1e-6
    dlon = dx_meters / (METERS_PER_DEG_LAT * cos_lat)
    return dlon, dlat


def compute_centroid(coords: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Compute (mean_lon, mean_lat) for a collection of (lon, lat) points."""
    if not coords:
        return 0.0, 0.0
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return float(np.mean(lons)), float(np.mean(lats))


def compute_polygon_area_perimeter_km(
    coords: List[Tuple[float, float]]
) -> Tuple[float, float]:
    """Compute approximate spherical area in km^2 and perimeter in km for a polygon of (lon, lat)."""
    if len(coords) < 3:
        return 0.0, 0.0

    # Ensure closed polygon
    pts = list(coords)
    if pts[0] != pts[-1]:
        pts.append(pts[0])

    # Centroid for local projection
    mean_lon, mean_lat = compute_centroid(pts[:-1])
    cos_lat = math.cos(math.radians(mean_lat))

    # Convert to local Cartesian coordinates (km)
    cart_pts = []
    for lon, lat in pts:
        x_km = (lon - mean_lon) * (METERS_PER_DEG_LAT * cos_lat) / 1000.0
        y_km = (lat - mean_lat) * METERS_PER_DEG_LAT / 1000.0
        cart_pts.append((x_km, y_km))

    # Shoelace formula for area
    area = 0.0
    perimeter = 0.0
    n = len(cart_pts)
    for i in range(n - 1):
        x1, y1 = cart_pts[i]
        x2, y2 = cart_pts[i + 1]
        area += x1 * y2 - x2 * y1
        perimeter += math.hypot(x2 - x1, y2 - y1)

    area = abs(area) * 0.5
    return float(area), float(perimeter)


def compute_orientation_degrees(coords: List[Tuple[float, float]]) -> float:
    """Compute the principal orientation angle (degrees clockwise from North, 0-180)."""
    if len(coords) < 3:
        return 0.0
    mean_lon, mean_lat = compute_centroid(coords)
    cos_lat = math.cos(math.radians(mean_lat))

    xs = np.array([(lon - mean_lon) * cos_lat for lon, lat in coords])
    ys = np.array([lat - mean_lat for lon, lat in coords])

    cov = np.cov(xs, ys)
    if cov.shape != (2, 2) or np.isnan(cov).any():
        return 0.0

    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    major_idx = np.argmax(eigenvalues)
    major_vec = eigenvectors[:, major_idx]  # [dx, dy]

    # Angle relative to North (y-axis)
    angle_rad = math.atan2(float(major_vec[0]), float(major_vec[1]))
    angle_deg = math.degrees(angle_rad) % 180.0
    return round(float(angle_deg), 2)


def compute_convex_hull(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Compute 2D convex hull of (lon, lat) points using Monotone Chain algorithm."""
    unique_points = sorted(set(points))
    if len(unique_points) <= 2:
        return unique_points

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in unique_points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in reversed(unique_points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    hull = lower[:-1] + upper[:-1]
    # Close hull
    if hull and hull[0] != hull[-1]:
        hull.append(hull[0])
    return hull


def point_in_polygon(lon: float, lat: float, coords: List[Tuple[float, float]]) -> bool:
    """Ray-casting test for a (lon, lat) point against a polygon ring."""
    if len(coords) < 3:
        return False
    pts = list(coords)
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        intersects = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def pca_length_width_km(coords: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Approximate major/minor axis lengths (km) from a 2-sigma PCA ellipse."""
    if len(coords) < 3:
        return 0.0, 0.0
    mean_lon, mean_lat = compute_centroid(coords)
    cos_lat = math.cos(math.radians(mean_lat))
    xs = np.array([(lon - mean_lon) * (METERS_PER_DEG_LAT * cos_lat) / 1000.0 for lon, lat in coords])
    ys = np.array([(lat - mean_lat) * METERS_PER_DEG_LAT / 1000.0 for lon, lat in coords])
    cov = np.cov(xs, ys)
    if cov.shape != (2, 2) or np.isnan(cov).any():
        return 0.0, 0.0
    eigenvalues, _ = np.linalg.eigh(cov)
    eigenvalues = np.clip(eigenvalues, 0.0, None)
    # 2-sigma extents along principal axes
    length = 4.0 * math.sqrt(float(eigenvalues.max()))
    width = 4.0 * math.sqrt(float(eigenvalues.min()))
    return float(length), float(max(width, 1e-6))


def axis_endpoints(
    coords: List[Tuple[float, float]],
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Return the two extreme vertices along the principal axis (narrower-end first)."""
    if not coords:
        return (0.0, 0.0), (0.0, 0.0)
    mean_lon, mean_lat = compute_centroid(coords)
    cos_lat = math.cos(math.radians(mean_lat))
    xs = np.array([(lon - mean_lon) * cos_lat for lon, lat in coords])
    ys = np.array([lat - mean_lat for lon, lat in coords])
    cov = np.cov(xs, ys)
    if cov.shape != (2, 2) or np.isnan(cov).any():
        return coords[0], coords[-1]
    _, eigenvectors = np.linalg.eigh(cov)
    major = eigenvectors[:, np.argmax(np.linalg.eigvalsh(cov))]
    proj = xs * major[0] + ys * major[1]
    head = coords[int(np.argmin(proj))]
    tail = coords[int(np.argmax(proj))]
    return (float(head[0]), float(head[1])), (float(tail[0]), float(tail[1]))


def to_geojson_polygon(coords: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Wrap closed coordinates [(lon, lat), ...] into GeoJSON Polygon dict."""
    pts = list(coords)
    if pts and pts[0] != pts[-1]:
        pts.append(pts[0])
    return {
        "type": "Polygon",
        "coordinates": [pts],
    }
