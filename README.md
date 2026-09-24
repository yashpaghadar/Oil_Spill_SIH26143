# Oiled — Codebase

Software implementation for Smart India Hackathon problem statement **SIH26143** (NTRO):
*Leveraging satellite imagery to determine Oil spills at sea along with AIS data correlations to identify vessel responsible for spill.*

All conceptual, architectural, and operational notes are stored in the separate Obsidian vault (`../sih-2026-vault`).

## Architecture & Pipeline

$$\text{Sentinel-1 SAR (VV/VH)} \xrightarrow{\text{CNN Triage}} \text{U-Net Segmentation} \xrightarrow{\text{Drift Physics}} \text{Origin Envelope} \xrightarrow{\text{AIS Filtering}} \text{Candidate Ranking}$$

## Directory Layout

- `src/oiled/`: Core library package
  - `data/`: Preprocessing, loaders, and stable data contracts (`contracts.py`)
  - `models/`: CNN triage classifier & U-Net (ResNet-34) segmentation
  - `drift/`: Physics-based forward/backward particle ensemble simulation
  - `ais/`: AIS normalization, filtering, and candidate evidence scoring
  - `utils/`: Geospatial transformations, GeoPandas/Shapely helpers
- `notebooks/`: Kaggle training and evaluation workflows
- `cases/`: Offline reproducible demo packages (e.g. `case-001`)
- `tests/`: Unit and integration test suites
