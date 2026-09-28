---
title: Oiled — Oil Spill Intelligence System
status: active
---

# Oiled — Oil Spill Intelligence Architecture

Oiled is an end-to-end geospatial intelligence system designed for automated satellite oil spill detection, drift trajectory modelling, historical AIS vessel tracking, and explainable source candidate attribution.

## 🏛️ System Overview

```text
Sentinel-1 VV/VH SAR Scene
   │
   ▼
Geospatial Preprocessing & Calibration
   │
   ▼
Lookalike & Clean-Sea Triage Classifier
   │
   ▼
Dual-Pol U-Net Oil Segmentation
   │
   ▼
Spill Event: Georeferenced Polygon & Metrics
   │
   ▼
Physics-Based Drift Trajectory Ensemble
   │
   ▼
Origin Envelope: Spatial Region & Time Window
   │
   ▼
Normalized AIS Historical Track Store
   │
   ▼
Spatio-Temporal Evidence Ranker
   │
   ▼
React Web GUI Incident Map & Review System
```

---

## 💡 Core Architecture Decisions

- **Semantic Segmentation over Bounding Boxes:** Oil slicks exhibit complex, irregular, and evolving geometries. Oiled employs semantic segmentation (U-Net with ResNet backbone) on dual-polarisation SAR data to compute exact slick perimeters, surface area, and spatial centroids.
- **Dual-Polarisation Sentinel-1 SAR (VV/VH):** VV and VH backscatter channels are calibrated to Sigma0 dB and georeferenced to preserve spatial and physical ocean surface properties.
- **Two-Stage Machine Learning Pipeline:** A light CNN triage classifier filters out clean ocean and lookalike features (such as low-wind areas, natural slicks, and internal waves) before passing candidate tiles to the U-Net segmentation network.
- **Physics-Driven Drift Mechanics:** Drift forecasting and origin backtracking use metocean surface current and 10m wind particle dynamics rather than purely statistical or black-box ML predictions, outputting spatial-temporal origin envelopes.
- **Transparent & Explainable AIS Attribution:** AIS evidence correlation evaluates spatio-temporal proximity, vessel trajectories, and operational behavior to rank potential source vessels transparently with human-interpretable scoring components.

---

## 🗺️ System Modules & Documentation Index

### Core Architecture & System Boundaries
1. [[02 - System Scope]] — System boundaries, core capabilities, and operational constraints
2. [[03 - Solution Pipeline]] — End-to-end data contracts, module interfaces, and system flow
3. [[05 - Technology]] — System technology stack (React GUI + Python backend & ML)
4. [[09 - Sources]] — Data registers, operational references, and scientific literature
5. [[10 - Official Problem Statement]] — Requirements traceability map

### System Datasets & Registers
- [[Data/01 - Satellite Dataset]] — Sentinel-1 SAR imagery specs, tiling, and label taxonomy
- [[Data/02 - Environmental Data]] — ERA5 wind and Copernicus Marine ocean current forcing data
- [[Data/03 - AIS Data]] — Automatic Identification System track formats, normalization, and quality flags
- [[Data/04 - Verification Case Data]] — Incident verification datasets and end-to-end test packages

### System Capabilities & Objectives
- [[Objectives/index]] — System module index and dependency pipeline

| Component | Function | Status |
|---|---|---|
| [[Objectives/01 - Detect Oil Spill]] | Dual-pol SAR tile triage & U-Net semantic slick mask generation | ✅ Functional |
| [[Objectives/02 - Characterize Spill]] | Mask-to-polygon conversion, area calculation, centroid & perimeter metrics | ✅ Functional |
| [[Objectives/03 - Validate Detection]] | Leakage-safe model evaluation, calibration & confidence thresholding | ✅ Functional |
| [[Objectives/04 - Model Spill Drift]] | Forward/backward particle trajectory ensemble simulation | ✅ Functional |
| [[Objectives/05 - Backtrack Origin]] | Origin envelope determination (spatial region & temporal window) | ✅ Functional |
| [[Objectives/06 - Analyze AIS]] | AIS trajectory parsing, interpolation, quality assessment & track store | ✅ Functional |
| [[Objectives/07 - Correlate Vessel With Spill]] | Spatio-temporal exclusion filtering & evidence feature extraction | ✅ Functional |
| [[Objectives/08 - Source Assessment]] | Multi-criteria evidence scoring & explainable candidate ranking | ✅ Functional |
| [[Objectives/09 - Visualize Incident]] | Incident management map, track inspection & analyst report generator | ✅ Functional |
