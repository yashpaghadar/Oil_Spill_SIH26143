"""Stable data contracts defining module boundaries across the Oiled pipeline.

See: sih-2026-vault/Oiled-SIH/03 - Solution Pipeline.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Scene:
    """Canonical Sentinel-1 SAR input scene metadata and raster references."""
    scene_id: str
    acquisition_utc: datetime
    crs: str
    vv_asset_uri: str
    vh_asset_uri: str
    preprocessing_version: str
    source: str
    licence: str
    bounds: Optional[Tuple[float, float, float, float]] = None  # (minx, miny, maxx, maxy)


@dataclass
class LabelSet:
    """Ground truth segmentation or triage annotations for a scene."""
    scene_id: str
    mask_uri: str
    label_taxonomy: str  # e.g., 'oil', 'lookalike', 'clean_sea'
    annotator: str
    label_revision: str
    confidence_level: float = 1.0


@dataclass
class Detection:
    """Raw model output from semantic segmentation / triage."""
    scene_id: str
    model_version: str
    probability_mask_uri: str
    threshold: float
    is_candidate_oil: bool
    calibration_flags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpillEvent:
    """Georeferenced detected oil spill polygon and extracted geometry."""
    detection_id: str
    observation_utc: datetime
    geometry_geojson: Dict[str, Any]
    area_km2: float
    perimeter_km: float
    centroid: Tuple[float, float]  # (longitude, latitude)
    confidence: float
    uncertainty_flags: List[str] = field(default_factory=list)


@dataclass
class EnvironmentalField:
    """Wind (ERA5) and current (Copernicus Marine) forcing data."""
    provider: str
    variables: List[str]  # e.g., ['u10', 'v10', 'uo', 'vo']
    time_bounds_utc: Tuple[datetime, datetime]
    spatial_bounds: Tuple[float, float, float, float]
    resolution_deg: float
    source_revision: str


@dataclass
class TrajectoryEnsemble:
    """Physics-based forward/backward particle ensemble simulation."""
    spill_event_id: str
    direction: str  # 'backward' (origin hindcast) or 'forward' (forecast)
    particle_count: int
    simulation_duration_hours: float
    parameters: Dict[str, Any]  # e.g., windage coefficient, diffusion rate
    origin_envelope_geojson: Optional[Dict[str, Any]] = None
    time_window_utc: Optional[Tuple[datetime, datetime]] = None


@dataclass
class VesselTrack:
    """Normalized historic AIS track for a single vessel."""
    mmsi: str
    timestamps_utc: List[datetime]
    positions: List[Tuple[float, float]]  # List of (longitude, latitude)
    sog_knots: List[float]
    cog_degrees: List[float]
    source: str
    quality_flags: List[str] = field(default_factory=list)


@dataclass
class CandidateAssessment:
    """Transparent evidence evaluation ranking a candidate vessel."""
    vessel_id: str  # MMSI
    rank: int
    total_score: float
    evidence_components: Dict[str, float]  # e.g., {'proximity': 0.8, 'timing': 0.7, 'route_fit': 0.9}
    exclusions: List[str] = field(default_factory=list)
    disclaimer: str = (
        "Candidate vessel assessment based on spatio-temporal correlation. "
        "Does not constitute confirmation of causation or legal liability."
    )
