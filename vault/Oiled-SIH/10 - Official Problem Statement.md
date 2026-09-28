---
title: SIH26143 Requirements Traceability
---

# SIH26143 Requirements Traceability Map

## Problem Challenge Brief

- **Title:** Leveraging satellite imagery to determine Oil spills at sea along with AIS data correlations to identify vessel responsible for spill.
- **Organisation:** National Technical Research Organisation (NTRO)
- **Theme:** Disaster Management
- **Category:** Software Infrastructure
- **Source:** https://sih.gov.in/sih2026PS

---

## Requirement-to-Design Map

| SIH Requirement | Planned System Architecture | Evidence of Completion |
|---|---|---|
| **Detect oil from satellite imagery** | Dual-pol Sentinel-1 SAR tile triage & U-Net semantic segmentation | Held-out scene segmentation metrics ($\text{IoU} \ge 0.78$, $\text{Dice} \ge 0.85$) |
| **Characterise slick geometry** | Vector geometry conversion service | Extracted GeoJSON polygon, surface area ($\text{km}^2$), perimeter, spatial centroid |
| **Use SAR and EO imagery** | SAR as primary detector; EO interface for optical corroboration | Decoupled `EOProvider` interface supporting Sentinel-2 / PlanetScope overlays |
| **Trace backward and forecast forward** | Physics-based Lagrangian particle drift simulation | Generated `TrajectoryEnsemble` and spatial-temporal origin envelopes |
| **Estimate slick age if feasible** | Multi-temporal trajectory alignment & weathering mechanics | Documented age estimation service driven by temporal slick tracking |
| **Reconstruct historic vessel traffic** | AIS track parser, normalizer, and PostGIS trajectory store | Standardized `VesselTrack` records with quality & interpolation flags |
| **Filter irrelevant vessels** | Origin envelope & time window spatial filtering engine | Automated vessel exclusion filters with logged rejection reasons |
| **Score proximity, trajectory & behavior** | Explainable multi-criteria evidence scoring ranker | Weighted composite candidate scores and ordered vessel assessments |
| **Provide an interactive visual interface** | Web geospatial incident management dashboard | Map interface featuring raster overlays, drift timelines, and candidate vessel cards |

---

## Technical Interpretation Guidelines

- **Candidate Ranking vs Legal Attribution:** "Identify vessel responsible" is engineered as **explainable spatio-temporal evidence ranking**. The system ranks candidate vessels based on physical compatibility without automated legal conclusions.
- **Confidence & Uncertainty:** Detection outputs carry calibrated probability maps and confidence flags to distinguish high-confidence oil slicks from radar lookalikes.
- **Origin Envelope:** "Origin" represents a probabilistic spatial-temporal envelope derived from particle trajectory ensembles, acknowledging hydrodynamic uncertainty.

---

## System Component Mapping

- [[Objectives/01 - Detect Oil Spill]]
- [[Objectives/02 - Characterize Spill]]
- [[Objectives/03 - Validate Detection]]
- [[Objectives/04 - Model Spill Drift]]
- [[Objectives/05 - Backtrack Origin]]
- [[Objectives/06 - Analyze AIS]]
- [[Objectives/07 - Correlate Vessel With Spill]]
- [[Objectives/08 - Source Assessment]]
- [[Objectives/09 - Visualize Incident]]
