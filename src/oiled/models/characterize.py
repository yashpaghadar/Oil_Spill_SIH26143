"""Slick morphology, Bragg wind gate, and Fay spreading age interval.

SAR sees oil because a film damps centimetre-scale Bragg waves. Below ~2 m/s the
sea is already dark; above ~13 m/s wind mixes oil down. The gate is a continuous
multiplier in [0, 1], not a hard cut.

Age is never a scalar: Fay's surface-tension law yields {low, best, high} hours
from observed width. Real oil spreads faster, so this is a loose ceiling used
to check the hindcast window — not a claimed slick age.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from oiled.utils.geometry import (
    axis_endpoints,
    compute_centroid,
    compute_orientation_degrees,
    compute_polygon_area_perimeter_km,
    pca_length_width_km,
)

GATE_RISE_MS = (2.0, 3.6)
GATE_FALL_MS = (9.5, 13.0)
WIND_GATE_REFUSE = 0.15

FAY_K3 = 1.33
SEAWATER_DENSITY = 1025.0
SEAWATER_VISCOSITY = 1.05e-6
SPREADING_COEFFICIENT = (0.03, 0.02, 0.01)  # N/m: fast, best, slow


def _ramp(value: float, low: float, high: float) -> float:
    if high <= low:
        return 1.0 if value >= high else 0.0
    return max(0.0, min(1.0, (value - low) / (high - low)))


def wind_gate(speed_ms: float) -> float:
    """Bragg-scattering confidence at a 10 m wind speed."""
    if not math.isfinite(speed_ms):
        raise ValueError(f"wind speed must be finite, got {speed_ms}")
    return _ramp(speed_ms, *GATE_RISE_MS) * (1.0 - _ramp(speed_ms, *GATE_FALL_MS))


def wind_direction_from_uv(u_ms: float, v_ms: float) -> Tuple[float, float]:
    """Return (speed_ms, meteorological from-direction degrees)."""
    speed = math.hypot(u_ms, v_ms)
    from_deg = (math.degrees(math.atan2(-u_ms, -v_ms)) + 360.0) % 360.0
    return speed, from_deg


def fay_surface_tension_hours(width_m: float, sigma: float) -> float:
    """Hours for a line-source slick to reach width_m in Fay's surface-tension regime."""
    if not (width_m > 0 and sigma > 0):
        raise ValueError("width and spreading coefficient must be positive")
    half_width = width_m / 2.0
    seconds = (
        (half_width / FAY_K3) ** 4 * SEAWATER_DENSITY**2 * SEAWATER_VISCOSITY / sigma**2
    ) ** (1.0 / 3.0)
    return float(seconds) / 3600.0


@dataclass
class AgeInterval:
    """Morphology prior on age. Never store a bare scalar."""
    low_hours: float
    best_hours: float
    high_hours: float
    width_m: float
    method: str = "fay_surface_tension"
    confidence: str = "very_low"
    explanation: str = ""


def morphology_age_prior(width_m: float) -> AgeInterval:
    if width_m <= 0:
        raise ValueError("width must be positive")
    fast, best, slow = (fay_surface_tension_hours(width_m, s) for s in SPREADING_COEFFICIENT)
    return AgeInterval(
        low_hours=round(fast, 2),
        best_hours=round(best, 2),
        high_hours=round(slow, 2),
        width_m=round(width_m, 1),
        explanation=(
            f"Fay surface-tension spreading to {width_m:.0f} m takes {fast:.1f}–{slow:.1f} h "
            "for σ = 0.03–0.01 N/m. Real oil spreads faster, so this is a ceiling, not an age."
        ),
    )


@dataclass
class SlickCharacterization:
    area_km2: float
    perimeter_km: float
    length_km: float
    width_km: float
    orientation_deg: float
    elongation: float
    compactness: float
    fragmentation: int
    centroid: Tuple[float, float]
    head: Tuple[float, float]
    tail: Tuple[float, float]
    head_tail_resolved_by: str
    wind_speed_ms: float
    wind_from_deg: float
    wind_gate_multiplier: float
    age: AgeInterval
    confidence: float
    provenance: str = "SIM"
    notes: List[str] = field(default_factory=list)


def characterize_slick(
    coords: List[Tuple[float, float]],
    wind_u: float,
    wind_v: float,
    confidence: float = 0.9,
    fragmentation: int = 1,
    provenance: str = "SIM",
) -> SlickCharacterization:
    """Measure geometry from a lon/lat ring and attach wind-gate / age prior."""
    area_km2, perimeter_km = compute_polygon_area_perimeter_km(coords)
    length_km, width_km = pca_length_width_km(coords)
    orientation = compute_orientation_degrees(coords)
    centroid = compute_centroid(coords)
    head, tail = axis_endpoints(coords)
    elongation = length_km / max(width_km, 1e-6)
    compactness = 0.0
    if perimeter_km > 0:
        compactness = (4.0 * math.pi * area_km2) / (perimeter_km**2)
    speed, from_deg = wind_direction_from_uv(wind_u, wind_v)
    gate = wind_gate(speed)
    age = morphology_age_prior(max(width_km * 1000.0, 1.0))

    notes: List[str] = []
    if gate < WIND_GATE_REFUSE:
        notes.append(
            f"Wind {speed:.1f} m/s is outside the Bragg window; detection confidence is refused."
        )
    elif gate < 0.75:
        notes.append(f"Wind {speed:.1f} m/s: reduced Bragg contrast (gate {gate:.2f}).")
    notes.append("Damping contrast is not thickness; no volume is inferred from SAR.")

    return SlickCharacterization(
        area_km2=round(area_km2, 2),
        perimeter_km=round(perimeter_km, 2),
        length_km=round(length_km, 2),
        width_km=round(width_km, 2),
        orientation_deg=round(orientation, 1),
        elongation=round(elongation, 2),
        compactness=round(compactness, 3),
        fragmentation=fragmentation,
        centroid=(round(centroid[0], 5), round(centroid[1], 5)),
        head=(round(head[0], 5), round(head[1], 5)),
        tail=(round(tail[0], 5), round(tail[1], 5)),
        head_tail_resolved_by="geometry_narrower_end_convention",
        wind_speed_ms=round(speed, 2),
        wind_from_deg=round(from_deg, 1),
        wind_gate_multiplier=round(gate, 3),
        age=age,
        confidence=confidence,
        provenance=provenance,
        notes=notes,
    )


def characterization_to_dict(c: SlickCharacterization) -> dict:
    return {
        "area_km2": c.area_km2,
        "perimeter_km": c.perimeter_km,
        "length_km": c.length_km,
        "width_km": c.width_km,
        "orientation_deg": c.orientation_deg,
        "elongation": c.elongation,
        "compactness": c.compactness,
        "fragmentation": c.fragmentation,
        "centroid": list(c.centroid),
        "head": list(c.head),
        "tail": list(c.tail),
        "head_tail_resolved_by": c.head_tail_resolved_by,
        "wind_speed_ms": c.wind_speed_ms,
        "wind_from_deg": c.wind_from_deg,
        "wind_gate_multiplier": c.wind_gate_multiplier,
        "age": {
            "low_hours": c.age.low_hours,
            "best_hours": c.age.best_hours,
            "high_hours": c.age.high_hours,
            "width_m": c.age.width_m,
            "method": c.age.method,
            "confidence": c.age.confidence,
            "explanation": c.age.explanation,
        },
        "confidence": c.confidence,
        "provenance": c.provenance,
        "notes": c.notes,
    }
