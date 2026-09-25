"""Spatio-temporal correlation and transparent candidate vessel evidence scoring."""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from oiled.data.contracts import CandidateAssessment, TrajectoryEnsemble, VesselTrack
from oiled.utils.geometry import compute_centroid, haversine_distance_km


class VesselCorrelator:
    """Correlates vessel trajectories with backtracked origin envelopes to produce transparent rankings."""

    def __init__(
        self,
        max_search_distance_km: float = 40.0,
        proximity_scale_km: float = 10.0,
        timing_scale_hours: float = 3.0,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.max_search_distance_km = max_search_distance_km
        self.proximity_scale_km = proximity_scale_km
        self.timing_scale_hours = timing_scale_hours

        # Transparent default scoring weights
        self.weights = weights or {
            "proximity": 0.40,
            "timing": 0.30,
            "route_fit": 0.15,
            "speed_behavior": 0.10,
            "data_quality": 0.05,
        }

    def correlate(
        self,
        ensemble: TrajectoryEnsemble,
        tracks: Dict[str, VesselTrack],
        spill_orientation_deg: Optional[float] = None,
    ) -> List[CandidateAssessment]:
        """Assess and rank candidate vessels against the backtracked origin envelope.

        Args:
            ensemble: TrajectoryEnsemble containing origin envelope and time window.
            tracks: Dictionary of parsed VesselTrack objects.
            spill_orientation_deg: Principal slick axis (degrees clockwise from North).
        """
        # Origin envelope polygon & centroid
        env_geojson = ensemble.origin_envelope_geojson or {}
        coords = env_geojson.get("coordinates", [[]])[0]
        env_centroid = compute_centroid(coords) if coords else (0.0, 0.0)

        window_start, window_end = ensemble.time_window_utc or (datetime.min, datetime.max)
        target_release_utc = window_start  # Hindcast horizon time

        assessments: List[CandidateAssessment] = []

        for mmsi, track in tracks.items():
            exclusions = []

            if not track.positions or len(track.positions) < 2:
                exclusions.append("insufficient_valid_points")
                assessments.append(
                    CandidateAssessment(
                        vessel_id=mmsi,
                        rank=-1,
                        total_score=0.0,
                        evidence_components={},
                        exclusions=exclusions,
                    )
                )
                continue

            track_start = track.timestamps_utc[0]
            track_end = track.timestamps_utc[-1]

            # 1. Temporal Check: Did vessel report within reasonable window?
            if track_end < window_start or track_start > window_end:
                exclusions.append("temporal_mismatch")

            # 2. Spatial Check: Closest Point of Approach (CPA) to origin centroid
            min_dist_km = float("inf")
            cpa_idx = 0
            for idx, (lon, lat) in enumerate(track.positions):
                d = haversine_distance_km(lon, lat, env_centroid[0], env_centroid[1])
                if d < min_dist_km:
                    min_dist_km = d
                    cpa_idx = idx

            if min_dist_km > self.max_search_distance_km:
                exclusions.append(f"spatial_mismatch_cpa_{min_dist_km:.1f}km")

            if exclusions:
                assessments.append(
                    CandidateAssessment(
                        vessel_id=mmsi,
                        rank=-1,
                        total_score=0.0,
                        evidence_components={"cpa_distance_km": round(min_dist_km, 2)},
                        exclusions=exclusions,
                    )
                )
                continue

            # Surviving candidate: Compute explainable evidence components
            # Proximity score: exp(-d / scale)
            proximity_score = math.exp(-min_dist_km / self.proximity_scale_km)

            # Timing score: temporal proximity of CPA to release horizon
            cpa_time = track.timestamps_utc[cpa_idx]
            dt_hours = abs((cpa_time - target_release_utc).total_seconds()) / 3600.0
            timing_score = math.exp(-dt_hours / self.timing_scale_hours)

            # Route / course fit
            cpa_cog = track.cog_degrees[cpa_idx]
            if spill_orientation_deg is not None:
                # Difference between vessel course and spill axis (0-90 deg)
                diff = abs((cpa_cog - spill_orientation_deg + 180) % 360 - 180)
                folded_diff = min(diff, 180.0 - diff)
                route_fit_score = max(0.0, 1.0 - (folded_diff / 90.0))
            else:
                route_fit_score = 0.8  # neutral fallback

            # Speed behavior: Typical tanker discharge happens at cruising speed (8-18 knots)
            cpa_sog = track.sog_knots[cpa_idx]
            if 8.0 <= cpa_sog <= 18.0:
                speed_score = 1.0
            elif 4.0 <= cpa_sog < 8.0 or 18.0 < cpa_sog <= 25.0:
                speed_score = 0.6
            else:
                speed_score = 0.2

            # Data quality factor
            quality_penalty = len(track.quality_flags) * 0.15
            quality_score = max(0.2, 1.0 - quality_penalty)

            # Weighted combination
            components = {
                "proximity": round(proximity_score, 4),
                "timing": round(timing_score, 4),
                "route_fit": round(route_fit_score, 4),
                "speed_behavior": round(speed_score, 4),
                "data_quality": round(quality_score, 4),
                "cpa_distance_km": round(min_dist_km, 2),
                "cpa_time_diff_hours": round(dt_hours, 2),
            }

            total_score = (
                self.weights["proximity"] * proximity_score
                + self.weights["timing"] * timing_score
                + self.weights["route_fit"] * route_fit_score
                + self.weights["speed_behavior"] * speed_score
                + self.weights["data_quality"] * quality_score
            )

            assessments.append(
                CandidateAssessment(
                    vessel_id=mmsi,
                    rank=0,  # will be assigned after sorting
                    total_score=round(float(total_score), 4),
                    evidence_components=components,
                    exclusions=[],
                )
            )

        # Sort surviving candidates by total score descending
        valid_candidates = [a for a in assessments if not a.exclusions]
        valid_candidates.sort(key=lambda x: x.total_score, reverse=True)

        for rank, cand in enumerate(valid_candidates, start=1):
            cand.rank = rank

        # Re-attach excluded candidates at the bottom
        excluded_candidates = [a for a in assessments if a.exclusions]
        return valid_candidates + excluded_candidates
