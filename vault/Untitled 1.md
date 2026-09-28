# 📑 SIH 2026 Complete PPT Copy-Paste Content & ASCII Visual Wireframes

> [!IMPORTANT]
> **Strict 6-Slide Rule:** This document contains the exact slide-by-slide text to copy directly into your presentation template (`NMIET_SIH_2026_PPT_Template.pptx`), followed by ASCII visual wireframes for every image you generate.

---

# 📋 PART 1: COPY-PASTE SLIDE CONTENT

---

## 🔹 SLIDE 1: TITLE PAGE

### Header / Title Text
**SMART INDIA HACKATHON 2026**

### Problem Statement Details Box
- **Problem Statement ID:** `SIH26143`
- **Problem Statement Title:** Leveraging satellite imagery to determine Oil spills at sea along with AIS data correlations to identify vessel responsible for spill
- **Theme:** Disaster Management
- **PS Category:** Software
- **Nodal Organisation:** National Technical Research Organisation (NTRO)

### Team Metadata Box
- **Team ID:** `[Insert Your Team ID]`
- **Team Name:** `[Insert Your Registered Team Name]`
- **Institute Name:** `NMIET`

---

## 🔹 SLIDE 2: PROPOSED SOLUTION

### Slide Title
**PROPOSED SOLUTION — OILED PLATFORM**

### Left Column: Key Features & Innovation
- **Automated Dual-Pol SAR Detection:**
  Processes Sentinel-1 (VV/VH) radar rasters using U-Net semantic segmentation to extract exact slick boundaries, surface area ($\text{km}^2$), perimeter, and orientation (avoiding bounding-box limitations).
- **Physics-Driven Drift Backtracking:**
  Simulates backward origin search windows using Lagrangian particle ensembles driven by ECMWF ERA5 10m wind and Copernicus Marine ocean surface current vectors.
- **Explainable AIS Vessel Attribution:**
  Filters historical AIS tracks within the origin window to rank candidate vessels transparently based on spatial-temporal proximity, course alignment, and speed anomalies.

### Right Box: Visual Graphic Placeholder
`[INSERT IMAGE 1: 5-Stage System Overview Diagram]`

---

## 🔹 SLIDE 3: TECHNICAL APPROACH

### Slide Title
**TECHNICAL APPROACH & PIPELINE ARCHITECTURE**

### Top Tech Stack Badges
`Frontend: React + MapLibre GL` | `Backend: Python / FastAPI` | `ML: PyTorch U-Net` | `Geospatial: Rasterio & GeoPandas` | `Drift: NumPy Ensemble`

### Main Execution Pipeline
- **Stage 1 (SAR Ingestion & Calibration):** Sentinel-1 IW GRD $\rightarrow$ Radiometric $\sigma^0$ dB Calibration $\rightarrow$ Ocean Bitmasking.
- **Stage 2 (Tile Triage Classifier):** ResNet CNN filters clean sea tiles and radar lookalikes (low wind areas, biogenic films).
- **Stage 3 (Dense Slick Segmentation):** Dual-channel U-Net with ResNet-34 encoder ($\text{BCE} + \text{Dice Loss}$) generates slick probability masks.
- **Stage 4 (Drift & Origin Envelope):** Vectorized Lagrangian particle simulation propagates windage/current vectors for backward origin windows.
- **Stage 5 (AIS Correlation & React GUI):** PostGIS/SQLite spatial query $\rightarrow$ Spatio-temporal candidate ranker $\rightarrow$ React Web GUI dashboard.

### Bottom Box: Visual Graphic Placeholder
`[INSERT IMAGE 2: Technical Solution Pipeline Diagram]`

---

## 🔹 SLIDE 4: FEASIBILITY AND VIABILITY

### Slide Title
**FEASIBILITY, VALIDATION BENCHMARKS & RISK STRATEGY**

### Top Left: Key Performance Benchmark Cards
- **Validation IoU:** `0.7899`
- **Validation Dice / F1:** `0.8513`
- **Validation Loss:** `0.3619`
- **Inference Latency:** `< 2.0 sec` per $512 \times 512$ tile

### Main Table: Challenge & Mitigation Matrix

| Potential Technical Challenge | System Solution & Risk Mitigation Strategy |
|---|---|
| **Radar Lookalikes** (Low wind zones, natural slicks) | ResNet triage classifier trained on false negatives rejects clean sea spots prior to dense segmentation. |
| **Drift Physics Uncertainty** | Multi-particle Lagrangian ensemble propagates windage and current variations to output spatial origin envelopes. |
| **AIS Transmission Gaps / Spoofing** | Hermite spline trajectory reconstruction coupled with explicit transmission quality flag weighting. |

### Bottom Box: Visual Graphic Placeholder
`[INSERT IMAGE 3: Model Validation Benchmark Report Card]`

---

## 🔹 SLIDE 5: IMPACT AND BENEFITS

### Slide Title
**IMPACT AND BENEFITS**

### 3 Core Value Pillars

#### 1. 🌿 Environmental Impact
- Enables early slick boundary extraction and precise area metrics for rapid deployment of emergency containment barriers.
- Minimizes coastal ecological contamination and protects marine biodiversity.

#### 2. ⚡ NTRO Operational Readiness
- Automates satellite data processing to deliver actionable intelligence reports within minutes of a satellite pass.
- Provides transparent candidate vessel ranking with complete audit provenance logging.

#### 3. 💰 Economic & System Efficiency
- Utilizes open-access Sentinel-1 SAR and Copernicus ERA5/CMEMS data streams without expensive proprietary software locks.
- Modular, lightweight Python architecture designed for low-cost cloud deployment.

### Bottom Box: Visual Graphic Placeholder
`[INSERT IMAGE 4: 3-Pillar Impact Infographic]`

---

## 🔹 SLIDE 6: RESEARCH AND REFERENCES

### Slide Title
**RESEARCH AND REFERENCES**

### Left Column: Data Registers & Scientific Frameworks
- **Satellite SAR Benchmark Corpus:** Zenodo Records `8346860` (Part I Training) & `13761290` (Part III Validation).
- **MetOcean Forcing Data:** ECMWF ERA5 10m Atmospheric Wind Reanalysis & CMEMS Global Ocean Surface Currents.
- **AIS Data Standards:** MarineCadastre / NOAA AccessAIS Format & IMO AIS Carriage Regulations.
- **Operational Guidelines:** EMSA CleanSeaNet Operational Monitoring Framework & NOAA PyGNOME Drift Physics.

### Right Box: Visual Graphic Placeholder
`[INSERT IMAGE 5: React Web Dashboard UI Screenshot]`

---

# 🎨 PART 2: ASCII VISUAL IMAGE REFERENCES

Use these ASCII wireframes as a visual guide for what each generated image should look like before inserting it into your PPT slides.

---

### 🖼️ IMAGE 1 (For Slide 2): System Overview Diagram

```text
+---------------------------------------------------------------------------------------------------+
|                                 OILED SYSTEM OVERVIEW DIAGRAM                                     |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   +-------------------+      +-------------------+      +-------------------+                     |
|   | 1. SAR SATELLITE  | ---> | 2. DUAL-STAGE AI  | ---> | 3. SLICK POLYGON  |                     |
|   | Sentinel-1 VV/VH  |      | Triage + U-Net    |      | Area (km²), Cent. |                     |
|   +-------------------+      +-------------------+      +-------------------+                     |
|                                                                   |                               |
|                                                                   v                               |
|   +-------------------+      +-------------------+      +-------------------+                     |
|   | 5. REACT GUI MAP  | <--- | 4. AIS RANKING    | <--- | 4. DRIFT PHYSICS  |                     |
|   | Analyst Dashboard |      | Candidate Match   |      | Wind + Currents   |                     |
|   +-------------------+      +-------------------+      +-------------------+                     |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

### 🖼️ IMAGE 2 (For Slide 3): Technical Solution Pipeline Diagram

```text
+---------------------------------------------------------------------------------------------------+
|                             TECHNICAL SOLUTION PIPELINE FLOWCHART                                 |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  [ Sentinel-1 SAR COG Tile ]                                                                      |
|             |                                                                                     |
|             v                                                                                     |
|  [ Preprocessing & Calibration (Rasterio) ]                                                       |
|             |                                                                                     |
|             v                                                                                     |
|  [ ResNet Triage Classifier ] ---> (Clean Sea / Lookalike) ---> [ Log Rejection & Exit ]          |
|             | (Candidate Oil)                                                                     |
|             v                                                                                     |
|  [ PyTorch U-Net Segmentation ]                                                                    |
|             |                                                                                     |
|             v                                                                                     |
|  [ GeoPandas Polygon Extraction ]                                                                 |
|             |                                                                                     |
|             v                                                                                     |
|  [ NumPy Lagrangian Particle Drift Simulation ]                                                   |
|             |                                                                                     |
|             v                                                                                     |
|  [ AIS Track Normalizer & Spatial Search Window ]                                                 |
|             |                                                                                     |
|             v                                                                                     |
|  [ Multi-Criteria Vessel Evidence Ranker ]                                                        |
|             |                                                                                     |
|             v                                                                                     |
|  [ React Web GUI Dashboard (MapLibre GL) ]                                                        |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

### 🖼️ IMAGE 3 (For Slide 4): Model Validation Benchmark Report Card

```text
+---------------------------------------------------------------------------------------------------+
|                            MODEL BENCHMARK & PERFORMANCE CARD                                     |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   +-------------------------+   +-------------------------+   +-------------------------------+   |
|   |   VALIDATION IoU        |   |   VALIDATION DICE / F1  |   |   PROCESSING SPEED            |   |
|   |                         |   |                         |   |                               |   |
|   |         0.7899          |   |         0.8513          |   |      < 2.0 s / Scene           |   |
|   +-------------------------+   +-------------------------+   +-------------------------------+   |
|                                                                                                   |
|   ---------------------------------------------------------------------------------------------   |
|                                                                                                   |
|   [ SAMPLE PREVIEW ]                                                                              |
|   +---------------------------------------+   +-----------------------------------------------+   |
|   | Raw Sentinel-1 SAR Input Tile         |   | U-Net Binarized Oil Slick Mask Overlay        |   |
|   | (VV / VH Channels in dB)              |   | (Extracted Polygon Geometry)                  |   |
|   +---------------------------------------+   +-----------------------------------------------+   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

### 🖼️ IMAGE 4 (For Slide 5): 3-Pillar Impact Infographic

```text
+---------------------------------------------------------------------------------------------------+
|                              3-PILLAR SYSTEM IMPACT INFOGRAPHIC                                   |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|   +---------------------------+   +---------------------------+   +---------------------------+   |
|   |   ENVIRONMENTAL IMPACT    |   |   OPERATIONAL READINESS   |   |    ECONOMIC EFFICIENCY    |   |
|   |                           |   |                           |   |                           |   |
|   | 🌿 Marine Ecosystem       |   | ⚡ Automated Ingestion    |   | 💰 Open Data Feeds        |   |
|   |    Protection             |   |    Rapid NTRO Alerts      |   |    Zero Software Locks   |   |
|   |                           |   |                           |   |                           |   |
|   | * Precise Slick Area      |   | * Intelligence Reports    |   | * Public Sentinel-1       |   |
|   | * Containment Barriers    |   |   within Minutes          |   |   & ERA5 Datasets         |   |
|   +---------------------------+   +---------------------------+   +---------------------------+   |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

---

### 🖼️ IMAGE 5 (For Slide 6): React Web Dashboard UI Screenshot

```text
+---------------------------------------------------------------------------------------------------+
|  OILED - Incident Dashboard                       [Incidents] [Analytics] [Settings]  (React UI)  |
+-----------------------------------+---------------------------------------------------------------+
| MAP VIEW (MapLibre GL)            | INCIDENT DETAILS & CANDIDATE RANKING                          |
|                                   |                                                               |
|  [Coastal Map Layer]              | Incident ID: #INC-104                                         |
|                                   | Slick Area:  14.2 km²                                         |
|  (Oil Slick Polygon)              | Perimeter:   18.6 km                                          |
|         |                         | Confidence:  94.2%                                            |
|         v                         |                                                               |
|  (~ ~ Drift Envelope ~ ~)         | ------------------------------------------------------------- |
|         |                         | RANKED CANDIDATE VESSELS                                      |
|         v                         |                                                               |
|  [Vessel Track #1]                | #1 Vessel Alpha (MMSI: 235012345) ---> [ 89.4% Match ]        |
|  [Vessel Track #2]                |    - High Proximity, Heading Aligned                          |
|                                   |                                                               |
|                                   | #2 Vessel Beta  (MMSI: 412098765) ---> [ 64.1% Match ]        |
|                                   |    - Temporal Gap Flagged                                     |
+-----------------------------------+---------------------------------------------------------------+
| [ > Play ] Timeline Scrubber: 2026-09-25 14:00 UTC =========================[o]==================  |
+---------------------------------------------------------------------------------------------------+
```
