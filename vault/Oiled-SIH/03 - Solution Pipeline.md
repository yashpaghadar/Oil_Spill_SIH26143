---
title: System Architecture and Data Contracts
---

# System Architecture and Data Contracts

## Pipeline Execution Flow

```text
Sentinel-1 IW GRD Acquisition
   │
   ▼
Radiometric Calibration, Ocean Masking & COG Export
   │
   ▼
Spatial Tiling & Scene Manifest Generation
   │
   ▼
CNN Scene & Tile Triage Classifier
   ├── [Candidate Oil Tile] --> U-Net Oil Mask Segmentation
   └── [Clean Sea / Lookalike] --> Reject & Log Classification Reason
   │
   ▼
Mask Binarization & Georeferenced Polygonization
   │
   ▼
SpillEvent Attribute Construction
   │
   ▼
Hydrodynamic & Wind Particle Drift Simulation
   │
   ▼
TrajectoryEnsemble Generation
   │
   ▼
Spatial-Temporal Origin Envelope Calculation
   │
   ▼
AIS Track Ingestion & Normalization Engine
   │
   ▼
Multi-Criteria Evidence Ranking Engine
   │
   ▼
Interactive Incident Dashboard & Analyst Review
```

---

## Production Data Contracts

The system enforces immutable Pydantic/dataclass data contracts between processing modules. These contracts guarantee interoperability across different data providers and compute backends.

| Data Record | Essential Schema Fields |
|---|---|
| `Scene` | `scene_id`, `acquisition_utc`, `crs`, `vv_asset_uri`, `vh_asset_uri`, `preprocessing_version`, `source_provider`, `licence` |
| `LabelSet` | `scene_id`, `mask_polygon_uri`, `label_taxonomy`, `annotator_quality`, `revision_id` |
| `Detection` | `scene_id`, `model_version`, `oil_probability_mask_uri`, `threshold`, `calibration_flags` |
| `SpillEvent` | `detection_id`, `geometry_wkt`, `area_km2`, `perimeter_km`, `centroid`, `observation_utc`, `confidence_score` |
| `EnvironmentalField` | `provider_id`, `variables` (wind_u, wind_v, current_u, current_v), `spatial_bounds`, `temporal_bounds`, `resolution` |
| `TrajectoryEnsemble` | `spill_event_id`, `particle_paths`, `drift_parameters`, `direction` (forward/backward), `uncertainty_polygon` |
| `VesselTrack` | `mmsi`, `vessel_name`, `timestamps_utc`, `positions_lat_lon`, `sog_knots`, `cog_degrees`, `quality_flags` |
| `CandidateAssessment` | `spill_event_id`, `mmsi`, `overall_rank`, `evidence_scores`, `exclusion_reasons`, `disclaimer_text` |

---

## Provider Interface Abstractions

To support production scalability and multi-cloud environments, core functions operate behind standardized abstract interfaces:

```text
SceneProvider          --> Ingests from Local COG Store, Copernicus Data Space API, or Sentinel Hub
EnvironmentalProvider  --> Fetches ERA5 Reanalysis, GFS Numerical Wind, and Copernicus Marine Ocean Currents
DriftEngine            --> Executes Lagrangian Particle Simulations (PyGNOME / OpenDrift integrations)
AISProvider            --> Interfaces with Terrestrial & Satellite AIS Feeds (Spire, MarineTraffic, AISHub)
EOProvider             --> Interfaces with Optical Satellites (Sentinel-2, PlanetScope) for Visual Corroboration
```

This modular interface design allows scaling from local batch execution to automated enterprise cloud pipelines without changing system business logic.
