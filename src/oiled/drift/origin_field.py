"""Origin probability from a backward particle ensemble.

A convex hull is a bound, not a probability. Attribution should score AIS
against a density field P(lon, lat) estimated from final particle positions.
If that field is too diffuse to discriminate, ranking is refused.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

from oiled.utils.geometry import compute_centroid, haversine_distance_km

# Origin field too wide to name a vessel (km² of the 90% mass region).
DIFFUSE_AREA_KM2 = 400.0
SEPARABILITY_FLOOR = 0.015


@dataclass
class OriginField:
    centroid: Tuple[float, float]
    sigma_km: float
    area90_km2: float
    particle_count: int
    insufficient_evidence: bool
    reason: str

    def density(self, lon: float, lat: float) -> float:
        """Unnormalized isotropic Gaussian density at a point, scaled to ~[0, 1] at the mode."""
        d = haversine_distance_km(lon, lat, self.centroid[0], self.centroid[1])
        s = max(self.sigma_km, 0.5)
        return float(np.exp(-0.5 * (d / s) ** 2))


def estimate_origin_field(final_coords: List[Tuple[float, float]]) -> OriginField:
    if not final_coords:
        return OriginField(
            centroid=(0.0, 0.0),
            sigma_km=1e6,
            area90_km2=1e12,
            particle_count=0,
            insufficient_evidence=True,
            reason="no_particles",
        )

    centroid = compute_centroid(final_coords)
    distances = [
        haversine_distance_km(lon, lat, centroid[0], centroid[1])
        for lon, lat in final_coords
    ]
    sigma_km = float(np.std(distances)) if len(distances) > 1 else float(distances[0])
    sigma_km = max(sigma_km, 0.5)
    # 90% mass of a 2D Gaussian lives inside ~2.15 σ
    radius_90 = 2.15 * sigma_km
    area90 = math.pi * radius_90**2
    diffuse = area90 > DIFFUSE_AREA_KM2
    return OriginField(
        centroid=(float(centroid[0]), float(centroid[1])),
        sigma_km=round(sigma_km, 3),
        area90_km2=round(area90, 2),
        particle_count=len(final_coords),
        insufficient_evidence=diffuse,
        reason="origin_field_too_diffuse" if diffuse else "",
    )
