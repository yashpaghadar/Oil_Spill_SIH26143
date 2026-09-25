"""Generate deterministic offline reproducible Case-001 package.

Simulates an incident off Mumbai/Gujarat coast in the Arabian Sea:
1. Detected slick polygon and geometry
2. Backward drift ensemble calculating origin envelope
3. AIS tracks with culprit and distractor vessels
4. Transparent candidate assessments
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pandas as pd

from oiled.ais.correlation import VesselCorrelator
from oiled.ais.parser import AISParser
from oiled.drift.environment import SyntheticEnvironmentalProvider
from oiled.drift.simulation import DriftSimulator
from oiled.utils.geometry import (
    compute_centroid,
    compute_orientation_degrees,
    compute_polygon_area_perimeter_km,
    to_geojson_polygon,
)

CASE_DIR = Path(__file__).resolve().parent / "case-001"


def generate_case_001():
    CASE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating reproducible Case-001 in {CASE_DIR} …")

    # 1. Spill Event (Observation at 12:00 UTC off Mumbai coast)
    obs_time = datetime(2026, 9, 25, 12, 0, 0, tzinfo=timezone.utc)
    base_lon, base_lat = 72.35, 18.80

    # Elongated slick oriented along shipping channel
    slick_coords = [
        (base_lon - 0.03, base_lat - 0.02),
        (base_lon + 0.04, base_lat + 0.03),
        (base_lon + 0.045, base_lat + 0.028),
        (base_lon - 0.025, base_lat - 0.022),
        (base_lon - 0.03, base_lat - 0.02),
    ]

    area_km2, perim_km = compute_polygon_area_perimeter_km(slick_coords)
    orientation_deg = compute_orientation_degrees(slick_coords)
    centroid = compute_centroid(slick_coords)

    spill_geojson = {
        "type": "Feature",
        "geometry": to_geojson_polygon(slick_coords),
        "properties": {
            "detection_id": "DET_20260925_SAR_001",
            "observation_utc": obs_time.isoformat(),
            "area_km2": round(area_km2, 2),
            "perimeter_km": round(perim_km, 2),
            "centroid": centroid,
            "orientation_deg": orientation_deg,
            "confidence": 0.94,
        },
    }

    with open(CASE_DIR / "spill_event.geojson", "w") as f:
        json.dump(spill_geojson, f, indent=2)

    # 2. Environmental Forcing & Backward Drift Simulation (12h hindcast)
    env = SyntheticEnvironmentalProvider(
        base_wind_speed=6.5,
        base_wind_dir_deg=45.0,  # blowing towards NE
        base_current_speed=0.28,
        base_current_dir_deg=35.0,
    )

    sim = DriftSimulator(
        environment=env,
        mean_windage=0.030,
        windage_std=0.005,
        diffusion_coeff=1.0,
        seed=101,  # Fixed seed for determinism
    )

    ensemble = sim.run_simulation(
        spill_event_id="DET_20260925_SAR_001",
        seed_coords=slick_coords,
        observation_utc=obs_time,
        duration_hours=12.0,
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
                ensemble.time_window_utc[0].isoformat(),
                ensemble.time_window_utc[1].isoformat(),
            ],
            "parameters": ensemble.parameters,
        },
    }

    with open(CASE_DIR / "trajectory_ensemble.geojson", "w") as f:
        json.dump(origin_geojson, f, indent=2)

    # 3. Generate AIS tracks
    # Hindcast origin release time was approx 00:00 - 02:00 UTC
    ais_records = []

    # Culprit: Tanker "AL-MARJAN" (MMSI 419000101)
    # Passes directly through origin envelope centroid around 01:00 UTC
    for step in range(10):
        t = obs_time - timedelta(hours=13) + timedelta(minutes=step * 30)
        frac = step / 9.0
        # Path crossing the backtracked origin
        lon = env_centroid[0] - 0.08 + frac * 0.16
        lat = env_centroid[1] - 0.08 + frac * 0.16
        ais_records.append({
            "mmsi": "419000101",
            "vessel_name": "MT_AL_MARJAN",
            "timestamp_utc": t.isoformat(),
            "longitude": round(lon, 4),
            "latitude": round(lat, 4),
            "sog": 13.2,
            "cog": 44.0,
        })

    # Distractor 1: Cargo "PACIFIC_VOYAGER" (MMSI 419000202)
    # Spatial mismatch: passes 55 km west
    for step in range(10):
        t = obs_time - timedelta(hours=13) + timedelta(minutes=step * 30)
        frac = step / 9.0
        lon = env_centroid[0] - 0.55 + frac * 0.10
        lat = env_centroid[1] - 0.10 + frac * 0.20
        ais_records.append({
            "mmsi": "419000202",
            "vessel_name": "MV_PACIFIC_VOYAGER",
            "timestamp_utc": t.isoformat(),
            "longitude": round(lon, 4),
            "latitude": round(lat, 4),
            "sog": 15.0,
            "cog": 30.0,
        })

    # Distractor 2: Bulker "OCEAN_PRIDE" (MMSI 419000303)
    # Temporal mismatch: crosses exact coordinates, but 14 hours after release window
    for step in range(10):
        t = obs_time + timedelta(hours=2) + timedelta(minutes=step * 30)
        frac = step / 9.0
        lon = env_centroid[0] - 0.08 + frac * 0.16
        lat = env_centroid[1] - 0.08 + frac * 0.16
        ais_records.append({
            "mmsi": "419000303",
            "vessel_name": "MV_OCEAN_PRIDE",
            "timestamp_utc": t.isoformat(),
            "longitude": round(lon, 4),
            "latitude": round(lat, 4),
            "sog": 11.5,
            "cog": 45.0,
        })

    ais_df = pd.DataFrame(ais_records)
    ais_df.to_csv(CASE_DIR / "synthetic_ais_tracks.csv", index=False)

    # 4. Run AIS Parser & Correlation Engine
    parser = AISParser()
    tracks = parser.parse_records(ais_records, source_name="Synthetic AIS Generator")

    correlator = VesselCorrelator(max_search_distance_km=40.0)
    assessments = correlator.correlate(
        ensemble=ensemble,
        tracks=tracks,
        spill_orientation_deg=orientation_deg,
    )

    assessments_dict = [
        {
            "vessel_id": a.vessel_id,
            "rank": a.rank,
            "total_score": a.total_score,
            "evidence_components": a.evidence_components,
            "exclusions": a.exclusions,
            "disclaimer": a.disclaimer,
        }
        for a in assessments
    ]

    with open(CASE_DIR / "candidate_assessments.json", "w") as f:
        json.dump(assessments_dict, f, indent=2)

    # 5. Case Manifest
    manifest = {
        "case_id": "case-001",
        "description": "Synthetic Arabian Sea oil spill incident with origin backtracking and AIS correlation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "geographic_region": "Arabian Sea (off Mumbai / Maharashtra coast)",
        "coordinates": {"longitude": base_lon, "latitude": base_lat},
        "observation_utc": obs_time.isoformat(),
        "artifacts": {
            "spill_event": "spill_event.geojson",
            "trajectory_ensemble": "trajectory_ensemble.geojson",
            "ais_tracks": "synthetic_ais_tracks.csv",
            "candidate_assessments": "candidate_assessments.json",
        },
        "assessment_summary": {
            "total_vessels_evaluated": len(assessments),
            "ranked_candidates": len([a for a in assessments if a.rank > 0]),
            "excluded_vessels": len([a for a in assessments if a.exclusions]),
            "top_candidate": assessments[0].vessel_id if assessments else None,
            "top_score": assessments[0].total_score if assessments else None,
        },
    }

    with open(CASE_DIR / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print("✓ Successfully generated case-001 package!")
    print(f"  Top Candidate: {manifest['assessment_summary']['top_candidate']} (Score: {manifest['assessment_summary']['top_score']})")


if __name__ == "__main__":
    generate_case_001()
