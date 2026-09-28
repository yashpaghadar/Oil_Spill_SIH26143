---
title: Incident Verification Dataset Architecture
---

# Incident Verification Dataset Architecture

## Overview

The system maintains versioned **Incident Verification Packages** to validate end-to-end processing across the pipeline modules (SAR Segmentation, Drift Modeling, AIS Correlation, and Incident Dashboard).

---

## Verification Package Layout

```text
verification_case_001/
├── manifest.json                 # Version control, source metadata, hashes, license
├── scene/
│   ├── vv_vh_cog.tif             # Calibrated 2-band SAR GeoTIFF/COG raster
│   ├── valid_ocean_mask.tif      # Binary valid marine spatial mask
│   └── scene_metadata.json       # Sentinel-1 acquisition metadata
├── model/
│   ├── triage.onnx               # Exported ONNX triage classifier
│   └── segmentation.onnx         # Exported ONNX U-Net segmentation checkpoint
├── expected/
│   ├── oil_probability_mask.tif  # Standardized output probability raster
│   ├── spill_event.geojson       # Extracted GeoJSON polygon with area & centroid
│   ├── trajectory_ensemble.geojson # Computed forward/backward particle trajectories
│   └── candidate_assessments.json  # Ranked vessel candidate assessment record
├── forcing/
│   └── environment.nc            # ERA5 wind & CMEMS current NetCDF forcing grid
└── ais/
    └── vessel_tracks.csv         # Normalized historical AIS vessel track dataset
```

---

## Quality Assurance & Verification Policy

- **Held-Out Validation:** Verification scenes are strictly excluded from model training and tuning splits.
- **Deterministic Pipeline Execution:** Expected results are produced by the frozen pipeline release and validated against regression metrics.
- **Audit Lineage:** Every verification artifact includes explicit model commit hashes, data schema revisions, and execution parameter records.
- **Automated Regression Testing:** CI/CD runners execute test packages to ensure raster outputs, extracted geometries, particle trajectories, and candidate rankings remain within defined statistical tolerances.
