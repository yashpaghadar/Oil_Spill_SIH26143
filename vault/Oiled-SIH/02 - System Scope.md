---
title: System Scope and Architecture Boundaries
---

# System Scope and Architecture Boundaries

## Core System Functionality

The **Oiled** system provides an automated pipeline for satellite-based ocean monitoring and incident analysis. The platform processes Sentinel-1 Synthetic Aperture Radar (SAR) observations, detects potential oil slicks, computes precise geometric attributes, models physical drift across time, and correlates vessel movement using AIS data to identify candidate source vessels.

```text
Sentinel-1 SAR Acquisition
   │
   ▼
Automated Geocoding & Calibrated VV/VH Rasters
   │
   ▼
Scene Triage Classifier
   │
   ▼
U-Net Slick Segmentation
   │
   ▼
Geospatial Polygon & Metric Extraction
   │
   ▼
Hydrodynamic & Wind Drift Modeling
   │
   ▼
Backtracked Origin Envelope
   │
   ▼
AIS Vessel Track Filtering
   │
   ▼
Explainable Evidence Scoring & Ranking
   │
   ▼
Analyst Incident Map & Intelligence Summary
```

---

## Architectural Principles & Non-Negotiables

| System Choice | Engineering Rationale |
|---|---|
| **Calibrated VV/VH SAR GeoTIFF/COG Inputs** | Standardized radiometric calibration (Sigma0 dB) ensures compatibility across public, commercial, and operational SAR sensors. |
| **Pixel-Level Semantic Segmentation** | Slick area, perimeter, shape complexity, and spatial orientation require pixel masks rather than bounding box estimates. |
| **Two-Stage Triage + Segmentation Architecture** | Dedicated triage filtering eliminates false alerts caused by low-wind zones, biogenic films, and internal waves prior to dense segmentation. |
| **Leakage-Safe Spatial Data Splitting** | Train/validation/test splits are strictly partitioned at scene/event levels to prevent spatial correlation leakage across overlapping image tiles. |
| **Physics-Based Drift Trajectories** | Drift dynamics rely on advection mechanics (surface current vector + wind leeway) rather than unconstrained black-box ML models. |
| **Decoupled Data & Compute Interfaces** | Modular interfaces for SAR ingestion, environmental forcing, and AIS streams allow underlying storage engines or APIs to swap without refactoring business logic. |
| **Defensible & Explainable Attribution** | The system produces ranked candidate assessments with explicit confidence factors and exclusions, adhering to evidentiary standards. |

---

## Operational Boundaries & Explicit Non-Goals

To maintain scientific integrity and operational focus, the system enforces the following boundaries:

- **Automated Chemical Slick Identification:** The system detects radar attenuation signatures characteristic of oil slicks; it does not replace chemical laboratory sampling for oil composition.
- **Direct Legal Causal Determination:** The platform calculates spatio-temporal compatibility scores for candidate vessels; it does not issue automated legal findings of fault.
- **Single-Image Age Determination:** Slick weathering age is inferred through multi-temporal tracking and drift alignment rather than single-image static classification.
- **Forced Multimodal Fusion Without Calibration:** Optical/EO data serves as optional corroborative evidence rather than early-stage pixel fusion without aligned ground truth.

---

## Operational Acceptance Criteria

A valid deployment of the Oiled pipeline meets the following system verification criteria:

1. **Detection:** Automated ingestion and output of calibrated oil probability rasters with lookalike rejection flags.
2. **Characterization:** Generation of georeferenced GeoJSON/WKT polygons with surface area ($\text{km}^2$), perimeter ($\text{km}$), and spatial centroid.
3. **Drift & Origin Envelope:** Simulation of forward trajectories and backward origin envelopes incorporating wind and current forcing vectors.
4. **Vessel Attribution:** Automated filtering of historical AIS tracks within the origin envelope and generation of transparently scored candidate vessel lists.
5. **Auditing:** Complete lineage preservation, attaching dataset versions, model commit hashes, and processing parameters to every incident record.
