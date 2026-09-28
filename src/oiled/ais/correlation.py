"""Spatio-temporal correlation and transparent candidate vessel evidence scoring.

Six named terms, hand-set weights, never fitted on three demo cases:

  drift        agreement with the hindcast origin field (the physics term)
  proximity    closest approach to the origin centroid
  temporality  CPA time vs release window
  parity       course vs slick axis
  behaviour    speed typical of a underway discharge
  prior        AIS quality / class prior

A wind gate below the refuse threshold, a diffuse origin field, or two
candidates the weights cannot separate returns insufficient_evidence instead
of a forced suspect.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from oiled.data.contracts import CandidateAssessment, TrajectoryEnsemble, VesselTrack
from oiled.drift.origin_field import OriginField, SEPARABILITY_FLOOR, estimate_origin_field
from oiled.models.characterize import WIND_GATE_REFUSE
from oiled.utils.geometry import compute_centroid, haversine_distance_km, point_in_polygon

WEIGHTS: Dict[str, float] = {
    "drift": 0.30,
    "proximity": 0.20,
    "temporality": 0.15,
    "parity": 0.15,
    "behaviour": 0.12,
    "prior": 0.08,
}
WEIGHTS_VERSION = "w1-handset"
PROXIMITY_SCALE_KM = 10.0
TIMING_SCALE_HOURS = 3.0
DRIFT_SCALE_KM = 6.0


class VesselCorrelator:
    """Correlates vessel trajectories with backtracked origin envelopes to produce transparent rankings."""

    def __init__(
        self,
        max_search_distance_km: float = 40.0,
        proximity_scale_km: float = PROXIMITY_SCALE_KM,
        timing_scale_hours: float = TIMING_SCALE_HOURS,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.max_search_distance_km = max_search_distance_km
        self.proximity_scale_km = proximity_scale_km
        self.timing_scale_hours = timing_scale_hours
        self.weights = weights or dict(WEIGHTS)

    def correlate(
        self,
        ensemble: TrajectoryEnsemble,
        tracks: Dict[str, VesselTrack],
        spill_orientation_deg: Optional[float] = None,
        wind_gate_multiplier: float = 1.0,
        vessel_meta: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> List[CandidateAssessment]:
        """Assess and rank candidate vessels against the backtracked origin field."""
        meta = vessel_meta or {}
        env_geojson = ensemble.origin_envelope_geojson or {}
        coords = env_geojson.get("coordinates", [[]])[0]
        ring = [(float(p[0]), float(p[1])) for p in coords] if coords else []
        env_centroid = compute_centroid(ring) if ring else (0.0, 0.0)

        final_points: List[Tuple[float, float]] = []
        if ensemble.particle_paths:
            for path in ensemble.particle_paths:
                if path:
                    _t, lon, lat = path[-1]
                    final_points.append((lon, lat))
        origin_field = (
            estimate_origin_field(final_points)
            if final_points
            else OriginField(
                centroid=env_centroid,
                sigma_km=float(ensemble.parameters.get("origin_sigma_km", 8.0)),
                area90_km2=float(ensemble.parameters.get("origin_area90_km2", 50.0)),
                particle_count=ensemble.particle_count,
                insufficient_evidence=bool(ensemble.parameters.get("origin_insufficient", False)),
                reason=str(ensemble.parameters.get("origin_insufficient_reason", "")),
            )
        )

        window_start, window_end = ensemble.time_window_utc or (datetime.min, datetime.max)
        target_release_utc = window_start

        refuse_reasons: List[str] = []
        if wind_gate_multiplier < WIND_GATE_REFUSE:
            refuse_reasons.append("wind_gate_insufficient_evidence")
        if origin_field.insufficient_evidence:
            refuse_reasons.append(origin_field.reason or "origin_field_too_diffuse")

        assessments: List[CandidateAssessment] = []

        for mmsi, track in tracks.items():
            info = meta.get(mmsi, {})
            label = info.get("name") or track.vessel_name or mmsi
            exclusions = []

            if not track.positions or len(track.positions) < 2:
                exclusions.append("insufficient_valid_points")
                assessments.append(
                    self._excluded(mmsi, label, exclusions, {"cpa_distance_km": None})
                )
                continue

            track_start = track.timestamps_utc[0]
            track_end = track.timestamps_utc[-1]

            if track_end < window_start or track_start > window_end:
                exclusions.append("temporal_mismatch")

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
                    self._excluded(
                        mmsi,
                        label,
                        exclusions,
                        {"cpa_distance_km": round(min_dist_km, 2)},
                    )
                )
                continue

            if refuse_reasons:
                assessments.append(
                    CandidateAssessment(
                        vessel_id=mmsi,
                        rank=-1,
                        total_score=0.0,
                        evidence_components={"cpa_distance_km": round(min_dist_km, 2)},
                        exclusions=list(refuse_reasons),
                        label=label,
                        verdict="insufficient_evidence",
                    )
                )
                continue

            proximity_score = math.exp(-min_dist_km / self.proximity_scale_km)

            cpa_time = track.timestamps_utc[cpa_idx]
            dt_hours = abs((cpa_time - target_release_utc).total_seconds()) / 3600.0
            timing_score = math.exp(-dt_hours / self.timing_scale_hours)

            cpa_cog = track.cog_degrees[cpa_idx]
            if spill_orientation_deg is not None:
                diff = abs((cpa_cog - spill_orientation_deg + 180) % 360 - 180)
                folded_diff = min(diff, 180.0 - diff)
                route_fit_score = max(0.0, 1.0 - (folded_diff / 90.0))
            else:
                route_fit_score = 0.8

            cpa_sog = track.sog_knots[cpa_idx]
            if 8.0 <= cpa_sog <= 18.0:
                speed_score = 1.0
            elif 4.0 <= cpa_sog < 8.0 or 18.0 < cpa_sog <= 25.0:
                speed_score = 0.6
            else:
                speed_score = 0.2

            quality_penalty = len(track.quality_flags) * 0.15
            quality_score = max(0.2, 1.0 - quality_penalty)
            vessel_type = (info.get("type") or track.vessel_type or "").lower()
            if "tanker" in vessel_type:
                quality_score = min(1.0, quality_score + 0.05)

            drift_score = self._drift_score(track, origin_field, ring, env_centroid)

            terms = {
                "drift": round(drift_score, 4),
                "proximity": round(proximity_score, 4),
                "temporality": round(timing_score, 4),
                "parity": round(route_fit_score, 4),
                "behaviour": round(speed_score, 4),
                "prior": round(quality_score, 4),
            }
            total = sum(self.weights[k] * terms[k] for k in self.weights) * wind_gate_multiplier
            without_keys = [k for k in self.weights if k != "drift"]
            wsum = sum(self.weights[k] for k in without_keys)
            total_without = (
                sum(self.weights[k] * terms[k] for k in without_keys) / wsum
            ) * wind_gate_multiplier

            assessments.append(
                CandidateAssessment(
                    vessel_id=mmsi,
                    rank=0,
                    total_score=round(float(total), 4),
                    evidence_components={
                        **terms,
                        "cpa_distance_km": round(min_dist_km, 2),
                        "cpa_time_diff_hours": round(dt_hours, 2),
                        "inside_origin_envelope": point_in_polygon(
                            track.positions[cpa_idx][0],
                            track.positions[cpa_idx][1],
                            ring,
                        )
                        if ring
                        else False,
                        "weights_version": WEIGHTS_VERSION,
                    },
                    exclusions=[],
                    label=label,
                    total_without_drift=round(float(total_without), 4),
                    verdict="ranked",
                )
            )

        valid_candidates = [a for a in assessments if a.verdict == "ranked"]
        valid_candidates.sort(key=lambda x: x.total_score, reverse=True)

        if len(valid_candidates) >= 2:
            margin = valid_candidates[0].total_score - valid_candidates[1].total_score
            if margin < SEPARABILITY_FLOOR:
                for cand in valid_candidates:
                    cand.rank = -1
                    cand.verdict = "insufficient_evidence"
                    cand.exclusions = ["candidates_not_separable"]
                    cand.total_score = 0.0

        ranked = [a for a in valid_candidates if a.verdict == "ranked"]
        for rank, cand in enumerate(ranked, start=1):
            cand.rank = rank

        others = [a for a in assessments if a not in ranked]
        return ranked + others

    def _drift_score(
        self,
        track: VesselTrack,
        origin_field: OriginField,
        ring: List[Tuple[float, float]],
        env_centroid: Tuple[float, float],
    ) -> float:
        """S_drift: how well the track sits in the origin density."""
        scores = []
        for lon, lat in track.positions:
            d = haversine_distance_km(lon, lat, origin_field.centroid[0], origin_field.centroid[1])
            scores.append(math.exp(-d / DRIFT_SCALE_KM))
        if not scores:
            return 0.0
        peak = max(scores)
        mean = sum(scores) / len(scores)
        inside = 0.0
        if ring:
            inside = max(
                1.0 if point_in_polygon(lon, lat, ring) else 0.0
                for lon, lat in track.positions
            )
        return max(0.0, min(1.0, 0.5 * peak + 0.3 * mean + 0.2 * inside))

    def _excluded(
        self,
        mmsi: str,
        label: str,
        exclusions: List[str],
        components: Dict[str, Any],
    ) -> CandidateAssessment:
        return CandidateAssessment(
            vessel_id=mmsi,
            rank=-1,
            total_score=0.0,
            evidence_components=components,
            exclusions=exclusions,
            label=label,
            verdict="excluded",
        )
