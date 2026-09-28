"""End-to-end offline case pipeline: characterize → drift → AIS → dashboard payload."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from oiled.ais.correlation import VesselCorrelator
from oiled.ais.parser import AISParser
from oiled.drift.environment import SyntheticEnvironmentalProvider
from oiled.drift.simulation import DriftSimulator
from oiled.models.characterize import (
    characterization_to_dict,
    characterize_slick,
)
from oiled.utils.geometry import to_geojson_polygon

VESSEL_META = {
    "419000101": {"name": "MT AL-MARJAN", "type": "Crude Oil Tanker"},
    "419000202": {"name": "MV PACIFIC VOYAGER", "type": "Container Ship"},
    "419000303": {"name": "MV OCEAN PRIDE", "type": "Bulk Carrier"},
    "419000404": {"name": "MT BHARAT SHAKTI", "type": "Product Tanker"},
    "419000505": {"name": "MV CHENNAI STAR", "type": "General Cargo"},
}


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _paths_for_dashboard(ensemble) -> List[Dict[str, Any]]:
    obs = None
    if ensemble.time_window_utc:
        obs = max(ensemble.time_window_utc)
    out = []
    for i, path in enumerate(ensemble.particle_paths or []):
        samples = []
        for ts, lon, lat in path:
            hours = 0.0
            if obs is not None:
                hours = (ts - obs).total_seconds() / 3600.0
            samples.append([round(hours, 3), round(lon, 5), round(lat, 5)])
        out.append({"id": i, "samples": samples})
    return out


def build_ais_records(
    env_centroid: Tuple[float, float],
    obs_time: datetime,
    scenario: str,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    def add_track(mmsi, name, vtype, t0, hours, lon0, lat0, dlon, dlat, sog, cog, steps=10):
        for step in range(steps):
            t = t0 + timedelta(hours=hours * step / max(steps - 1, 1))
            frac = step / max(steps - 1, 1)
            records.append(
                {
                    "mmsi": mmsi,
                    "vessel_name": name,
                    "vessel_type": vtype,
                    "timestamp_utc": _iso(t),
                    "longitude": round(lon0 + frac * dlon, 4),
                    "latitude": round(lat0 + frac * dlat, 4),
                    "sog": sog,
                    "cog": cog,
                }
            )

    if scenario == "case-002":
        # Calm-wind region: vessels exist, but the Bragg gate must refuse ranking.
        add_track(
            "419000101", "MT_AL_MARJAN", "Crude Oil Tanker",
            obs_time - timedelta(hours=13), 4.5,
            env_centroid[0] - 0.08, env_centroid[1] - 0.08, 0.16, 0.16, 13.2, 44.0,
        )
        add_track(
            "419000202", "MV_PACIFIC_VOYAGER", "Container Ship",
            obs_time - timedelta(hours=13), 4.5,
            env_centroid[0] - 0.55, env_centroid[1] - 0.10, 0.10, 0.20, 15.0, 30.0,
        )
        return records

    if scenario == "case-003":
        add_track(
            "419000404", "MT_BHARAT_SHAKTI", "Product Tanker",
            obs_time - timedelta(hours=13), 4.5,
            env_centroid[0] - 0.04, env_centroid[1] - 0.04, 0.12, 0.12, 12.4, 48.0,
        )
        add_track(
            "419000101", "MT_AL_MARJAN", "Crude Oil Tanker",
            obs_time - timedelta(hours=12), 5.0,
            env_centroid[0] - 0.12, env_centroid[1] - 0.02, 0.18, 0.08, 13.0, 55.0,
        )
        add_track(
            "419000202", "MV_PACIFIC_VOYAGER", "Container Ship",
            obs_time - timedelta(hours=13), 4.5,
            env_centroid[0] - 0.55, env_centroid[1] - 0.10, 0.10, 0.20, 15.0, 30.0,
        )
        add_track(
            "419000505", "MV_CHENNAI_STAR", "General Cargo",
            obs_time + timedelta(hours=2), 4.5,
            env_centroid[0] - 0.08, env_centroid[1] - 0.08, 0.16, 0.16, 11.0, 45.0,
        )
        return records

    # case-001: moving tanker discharge + spatial/temporal distractors
    add_track(
        "419000101", "MT_AL_MARJAN", "Crude Oil Tanker",
        obs_time - timedelta(hours=13), 4.5,
        env_centroid[0] - 0.08, env_centroid[1] - 0.08, 0.16, 0.16, 13.2, 44.0,
    )
    add_track(
        "419000202", "MV_PACIFIC_VOYAGER", "Container Ship",
        obs_time - timedelta(hours=13), 4.5,
        env_centroid[0] - 0.55, env_centroid[1] - 0.10, 0.10, 0.20, 15.0, 30.0,
    )
    add_track(
        "419000303", "MV_OCEAN_PRIDE", "Bulk Carrier",
        obs_time + timedelta(hours=2), 4.5,
        env_centroid[0] - 0.08, env_centroid[1] - 0.08, 0.16, 0.16, 11.5, 45.0,
    )
    return records


def run_scenario(
    case_id: str,
    case_dir: Path,
    *,
    title: str,
    region: str,
    base_lon: float,
    base_lat: float,
    obs_time: datetime,
    slick_coords: List[Tuple[float, float]],
    wind_speed: float,
    wind_dir_deg: float,
    current_speed: float,
    current_dir_deg: float,
    duration_hours: float = 12.0,
    provenance: str = "SIM",
) -> Dict[str, Any]:
    case_dir.mkdir(parents=True, exist_ok=True)

    env = SyntheticEnvironmentalProvider(
        base_wind_speed=wind_speed,
        base_wind_dir_deg=wind_dir_deg,
        base_current_speed=current_speed,
        base_current_dir_deg=current_dir_deg,
    )
    u10, v10 = env.get_wind(base_lon, base_lat, obs_time)
    uo, vo = env.get_current(base_lon, base_lat, obs_time)

    char = characterize_slick(
        slick_coords, u10, v10, confidence=0.94 if wind_speed >= 3 else 0.35, provenance=provenance
    )

    spill_geojson = {
        "type": "Feature",
        "geometry": to_geojson_polygon(slick_coords),
        "properties": {
            "detection_id": f"DET_{obs_time.strftime('%Y%m%d')}_{case_id.upper()}",
            "observation_utc": _iso(obs_time),
            **characterization_to_dict(char),
        },
    }
    (case_dir / "spill_event.geojson").write_text(json.dumps(spill_geojson, indent=2), encoding="utf-8")

    sim = DriftSimulator(
        environment=env,
        mean_windage=0.030,
        windage_std=0.005 if wind_speed >= 3 else 0.02,
        diffusion_coeff=1.0 if wind_speed >= 3 else 25.0,
        seed=101,
    )
    ensemble = sim.run_simulation(
        spill_event_id=spill_geojson["properties"]["detection_id"],
        seed_coords=slick_coords,
        observation_utc=obs_time,
        duration_hours=duration_hours,
        step_minutes=30.0,
        direction="backward",
        particle_count=100,
    )
    env_centroid = ensemble.parameters["envelope_centroid"]

    origin_geojson = {
        "type": "Feature",
        "geometry": ensemble.origin_envelope_geojson,
        "properties": {
            "spill_event_id": ensemble.spill_event_id,
            "direction": ensemble.direction,
            "simulation_duration_hours": ensemble.simulation_duration_hours,
            "origin_time_window_utc": [
                _iso(ensemble.time_window_utc[0]),
                _iso(ensemble.time_window_utc[1]),
            ],
            "parameters": {
                k: (list(v) if isinstance(v, tuple) else v)
                for k, v in ensemble.parameters.items()
            },
            "provenance": provenance,
        },
    }
    (case_dir / "trajectory_ensemble.geojson").write_text(json.dumps(origin_geojson, indent=2), encoding="utf-8")

    ais_records = build_ais_records(env_centroid, obs_time, case_id)
    pd.DataFrame(ais_records).to_csv(case_dir / "synthetic_ais_tracks.csv", index=False)

    parser = AISParser()
    tracks = parser.parse_records(ais_records, source_name=f"{provenance} AIS")
    correlator = VesselCorrelator(max_search_distance_km=40.0)
    assessments = correlator.correlate(
        ensemble=ensemble,
        tracks=tracks,
        spill_orientation_deg=char.orientation_deg,
        wind_gate_multiplier=char.wind_gate_multiplier,
        vessel_meta=VESSEL_META,
    )

    ranked = [a for a in assessments if a.rank > 0]
    verdict = "insufficient_evidence"
    if char.wind_gate_multiplier < 0.15:
        verdict = "insufficient_evidence"
        reason = "Wind below Bragg gate — the dark patch cannot be trusted as oil."
    elif ensemble.parameters.get("origin_insufficient"):
        verdict = "insufficient_evidence"
        reason = "Origin field too diffuse to discriminate a vessel."
    elif ranked:
        verdict = "candidate_ranked"
        reason = "Origin field and AIS gate produced a separable top candidate."
    else:
        reason = "No vessel survived spatial-temporal gating."

    assessments_dict = [
        {
            "vessel_id": a.vessel_id,
            "label": a.label or VESSEL_META.get(a.vessel_id, {}).get("name", a.vessel_id),
            "vessel_type": VESSEL_META.get(a.vessel_id, {}).get("type", ""),
            "rank": a.rank,
            "total_score": a.total_score,
            "total_without_drift": a.total_without_drift,
            "evidence_components": a.evidence_components,
            "exclusions": a.exclusions,
            "verdict": a.verdict,
            "disclaimer": a.disclaimer,
        }
        for a in assessments
    ]
    (case_dir / "candidate_assessments.json").write_text(json.dumps(assessments_dict, indent=2), encoding="utf-8")

    payload = {
        "case_id": case_id,
        "title": title,
        "description": title,
        "provenance": provenance,
        "verdict": verdict,
        "verdict_reason": reason,
        "geographic_region": region,
        "coordinates": {"longitude": base_lon, "latitude": base_lat},
        "observation_utc": _iso(obs_time),
        "metocean": {
            "wind_speed_ms": round(char.wind_speed_ms, 2),
            "wind_from_deg": char.wind_from_deg,
            "current_speed_ms": round((uo**2 + vo**2) ** 0.5, 3),
            "current_dir_deg": wind_dir_deg,  # display approx
            "wind_gate": char.wind_gate_multiplier,
            "source": f"{provenance} · Synthetic ERA5/CMEMS-like field",
        },
        "characterization": characterization_to_dict(char),
        "slick": spill_geojson,
        "origin": origin_geojson,
        "particles": _paths_for_dashboard(ensemble),
        "ais": _ais_payload(ais_records),
        "assessments": assessments_dict,
        "pipeline": [
            {"id": "sar", "label": "SAR ingest", "status": "sim"},
            {"id": "triage", "label": "Look-alike triage", "status": "pass" if char.wind_gate_multiplier >= 0.15 else "hold"},
            {"id": "seg", "label": "Slick mask", "status": "pass"},
            {"id": "geom", "label": "Characterize", "status": "pass"},
            {"id": "drift", "label": "Backward ensemble", "status": "pass"},
            {"id": "ais", "label": "AIS gate + score", "status": "pass" if verdict == "candidate_ranked" else "hold"},
        ],
    }
    (case_dir / "dashboard_payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    manifest = {
        "case_id": case_id,
        "description": title,
        "created_utc": _iso(datetime.now(timezone.utc)),
        "geographic_region": region,
        "coordinates": {"longitude": base_lon, "latitude": base_lat},
        "observation_utc": _iso(obs_time),
        "provenance": provenance,
        "verdict": verdict,
        "artifacts": {
            "spill_event": "spill_event.geojson",
            "trajectory_ensemble": "trajectory_ensemble.geojson",
            "ais_tracks": "synthetic_ais_tracks.csv",
            "candidate_assessments": "candidate_assessments.json",
            "dashboard_payload": "dashboard_payload.json",
        },
        "assessment_summary": {
            "total_vessels_evaluated": len(assessments),
            "ranked_candidates": len(ranked),
            "excluded_vessels": len([a for a in assessments if a.verdict == "excluded"]),
            "top_candidate": ranked[0].vessel_id if ranked else None,
            "top_score": ranked[0].total_score if ranked else None,
            "verdict": verdict,
        },
    }
    (case_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return payload


def _ais_payload(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by: Dict[str, Dict[str, Any]] = {}
    for r in records:
        mmsi = str(r["mmsi"])
        rec = by.setdefault(
            mmsi,
            {
                "mmsi": mmsi,
                "name": str(r.get("vessel_name", mmsi)).replace("_", " "),
                "type": r.get("vessel_type", ""),
                "points": [],
            },
        )
        rec["points"].append(
            {
                "t": r["timestamp_utc"],
                "lon": r["longitude"],
                "lat": r["latitude"],
                "sog": r["sog"],
                "cog": r["cog"],
            }
        )
    return list(by.values())


def generate_all_cases(cases_root: Path) -> List[Dict[str, Any]]:
    obs = datetime(2026, 9, 25, 12, 0, 0, tzinfo=timezone.utc)
    payloads = []

    slick_mumbai = [
        (72.32, 18.78),
        (72.39, 18.83),
        (72.395, 18.828),
        (72.325, 18.778),
        (72.32, 18.78),
    ]
    payloads.append(
        run_scenario(
            "case-001",
            cases_root / "case-001",
            title="Moving tanker discharge — Arabian Sea off Mumbai",
            region="Arabian Sea (off Mumbai / Maharashtra coast)",
            base_lon=72.35,
            base_lat=18.80,
            obs_time=obs,
            slick_coords=slick_mumbai,
            wind_speed=6.5,
            wind_dir_deg=45.0,
            current_speed=0.28,
            current_dir_deg=35.0,
        )
    )

    slick_kutch = [
        (69.72, 22.68),
        (69.76, 22.71),
        (69.765, 22.708),
        (69.725, 22.678),
        (69.72, 22.68),
    ]
    payloads.append(
        run_scenario(
            "case-002",
            cases_root / "case-002",
            title="Honest rejection — calm wind / Bragg gate closed",
            region="Gulf of Kutch (calm-wind look-alike regime)",
            base_lon=69.74,
            base_lat=22.69,
            obs_time=obs,
            slick_coords=slick_kutch,
            wind_speed=1.6,
            wind_dir_deg=20.0,
            current_speed=0.12,
            current_dir_deg=15.0,
        )
    )

    slick_lane = [
        (80.28, 13.22),
        (80.38, 13.30),
        (80.39, 13.292),
        (80.29, 13.214),
        (80.28, 13.22),
    ]
    payloads.append(
        run_scenario(
            "case-003",
            cases_root / "case-003",
            title="Traffic corridor — two tankers, one separable candidate",
            region="Bay of Bengal shipping lane (off Chennai / Ennore)",
            base_lon=80.33,
            base_lat=13.25,
            obs_time=obs,
            slick_coords=slick_lane,
            wind_speed=7.2,
            wind_dir_deg=48.0,
            current_speed=0.32,
            current_dir_deg=40.0,
        )
    )
    return payloads
