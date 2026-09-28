---
title: Core System Modules & Objectives
---

# Core System Modules & Objectives

The **Oiled** platform is structured into 9 modular core components:

1. [[Objectives/01 - Detect Oil Spill]] — Dual-channel SAR triage and U-Net semantic slick segmentation
2. [[Objectives/02 - Characterize Spill]] — Geometry extraction, area ($\text{km}^2$), perimeter, and centroid metrics
3. [[Objectives/03 - Validate Detection]] — Leakage-safe evaluation, probability thresholding, and confidence scoring
4. [[Objectives/04 - Model Spill Drift]] — Physics-based Lagrangian forward and backward particle drift modeling
5. [[Objectives/05 - Backtrack Origin]] — Probabilistic origin envelope determination (spatial region & temporal window)
6. [[Objectives/06 - Analyze AIS]] — Quality-aware AIS track parsing, interpolation, and trajectory storage
7. [[Objectives/07 - Correlate Vessel With Spill]] — Spatio-temporal exclusion filtering and evidence feature calculation
8. [[Objectives/08 - Source Assessment]] — Multi-criteria explainable candidate vessel ranking
9. [[Objectives/09 - Visualize Incident]] — Interactive geospatial incident map, temporal playback, and intelligence export

---

## Pipeline Execution Order

```text
[01 - Detect Oil Spill] ──> [02 - Characterize Spill] ──> [04 - Model Spill Drift] ──> [05 - Backtrack Origin]
          │                                                                                    │
          ▼                                                                                    ▼
[03 - Validate Detection]                                                          [07 - Correlate Vessel With Spill] <── [06 - Analyze AIS]
                                                                                               │
                                                                                               ▼
                                                                                   [08 - Source Assessment]
                                                                                               │
                                                                                               ▼
                                                                                   [09 - Visualize Incident]
```
