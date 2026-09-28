# 📊 Balanced SIH 2026 Presentation Blueprint & AI Prompts

NOTE

**Design & Depth Balance:** Clean, professional white theme (light mode) that strikes the perfect balance—**technically thorough and complete** so judges get all required details, yet **structured with clear visual hierarchy** so it remains easy to read.

---

## 📽️ Complete 6-Slide Presentation Blueprint

text

SLIDE 1: Title & Metadata Page (Complete SIH26143 Identification)

SLIDE 2: Proposed Solution (System Architecture & Innovation Overview)

SLIDE 3: Technical Approach (5-Stage End-to-End Pipeline & Tech Stack)

SLIDE 4: Feasibility & Viability (Validation Benchmarks & Risk Mitigation Matrix)

SLIDE 5: Impact & Benefits (Environmental, Operational & Economic Value)

SLIDE 6: Research & References (Data Registers, Scientific Standards & React GUI)

---

### Slide 1: Title Page

#### Layout & Content

- **Header:** Smart India Hackathon 2026
- **Problem Statement ID:** `SIH26143`
- **Problem Title:** _Leveraging satellite imagery to determine Oil spills at sea along with AIS data correlations to identify vessel responsible for spill_
- **Organization:** National Technical Research Organisation (NTRO)
- **Theme:** Disaster Management | **Category:** Software
- **Team ID & Name:** `[Your Team ID]` | `[Your Registered Team Name]`

---

### Slide 2: Proposed Solution

#### Layout & Content (3 Feature Columns + System Concept Image)

- **Problem Context:** Oil spills cause severe marine damage; traditional manual analysis and bounding-box detection lack boundary precision and vessel correlation capabilities.
- **Core Solution — Oiled Platform:**
    1. 🛰️ **Dual-Pol SAR Semantic Segmentation:** Uses Sentinel-1 (VV/VH) radar to extract precise slick boundaries, surface area (km2km2), perimeter, and orientation (avoiding bounding-box limitations).
    2. 🌊 **Physics-Based Drift Engine:** Simulates backward origin windows using ECMWF ERA5 10m wind and Copernicus Marine surface current vectors.
    3. 🚢 **Explainable AIS Vessel Attribution:** Correlates historical AIS vessel trajectories within the origin envelope to rank candidate ships transparently based on spatio-temporal evidence.
- **Visual Asset:** **[IMAGE 1: Complete System Concept Overview]**

---

### Slide 3: Technical Approach

#### Layout & Content (5 Pipeline Stages + Tech Stack Table)

- **5-Stage Execution Flow:**
    - `Stage 1 (Ingestion & Calibration)`: Sentinel-1 IW GRD →→ Radiometric σ0σ0 dB Calibration →→ Valid Ocean Masking.
    - `Stage 2 (Tile Triage Classifier)`: Lightweight ResNet CNN filters clean ocean & radar lookalikes (low wind, natural films).
    - `Stage 3 (Dense Slick Segmentation)`: Dual-channel PyTorch U-Net (ResNet-34 backbone) generates oil probability masks.
    - `Stage 4 (Drift & Origin Backtracking)`: Vectorized NumPy Lagrangian particle ensemble computes probabilistic origin envelopes.
    - `Stage 5 (AIS Correlation & React GUI)`: PostGIS/SQLite spatial query →→ Multi-criteria evidence ranker →→ React Web GUI.
- **Technology Stack:**

|Layer|Choice|Function|
|---|---|---|
|**Frontend GUI**|React + MapLibre GL|Interactive map visualizer, temporal slider, candidate cards|
|**Backend API**|Python / FastAPI|Microservice serving GeoJSON layers, metrics, and AIS tracks|
|**Deep Learning**|PyTorch (U-Net + ResNet)|2-channel SAR segmentation (IoU=0.7899IoU=0.7899, Dice=0.8513Dice=0.8513)|
|**Geospatial & Physics**|Rasterio + GeoPandas + NumPy|COG processing, spatial CRS transforms, particle drift simulation|

- **Visual Asset:** **[IMAGE 2: Technical Architecture & Pipeline Infographic]**

---

### Slide 4: Feasibility, Viability & Risk Strategy

#### Layout & Content (Validation Metrics Card + Detailed Risk Matrix)

- **Benchmark Performance Metrics:**
    - **Val IoU:** `0.7899` | **Val Dice / F1:** `0.8513` | **Val Loss:** `0.3619`
    - **Inference Speed:** `< 2.0 sec` per 512×512512×512 tile | **Model Parameters:** `24.4 M`
- **Comprehensive Challenge vs. Mitigation Matrix:**

|Technical Challenge|System Solution & Mitigation|
|---|---|
|**Radar Lookalikes** (Low wind areas, biogenic films)|ResNet triage classifier trained on false negatives rejects non-oil dark spots before dense segmentation|
|**Metocean & Drift Uncertainty**|Multi-particle Lagrangian ensemble propagates windage/current variations to output spatial origin envelopes|
|**AIS Signal Gaps & Spoofing**|Hermite spline trajectory reconstruction with explicit AIS transmission quality weighting|

- **Visual Asset:** **[IMAGE 3: Benchmark Performance & Model Metrics Report Card]**

---

### Slide 5: Impact and Benefits

#### Layout & Content (3 Visual Impact Sections)

- 🌿 **Environmental Impact:** Enables early slick boundary extraction and perimeter calculation for targeted emergency containment, protecting coastal marine ecosystems.
- ⚡ **NTRO Operational Readiness:** Automates satellite imagery ingestion and generates actionable candidate vessel intelligence within minutes of satellite pass.
- 💰 **Economic & Resource Efficiency:** Built on open-access Sentinel-1 SAR imagery and Copernicus ERA5/CMEMS environmental data feeds without heavy proprietary software locks.
- 📜 **Scientific Accountability:** Transparent, multi-criteria evidence scoring with complete data provenance and execution logging.
- **Visual Asset:** **[IMAGE 4: Environmental, Operational & Economic Impact Infographic]**

---

### Slide 6: Research & References

#### Layout & Content (Data Registers + React UI Screenshot Preview)

- **Data Registers & Scientific References:**
    - **Sentinel-1 SAR Oil Spill Corpus:** Zenodo Records `8346860` (Part I) & `13761290` (Part III).
    - **Environmental Forcing Data:** ECMWF ERA5 10m Wind & Copernicus Marine Ocean Surface Currents (CMEMS).
    - **Vessel Tracking Standards:** MarineCadastre / NOAA AIS Schema & IMO AIS Specifications.
    - **Operational Standards:** EMSA CleanSeaNet Framework & NOAA PyGNOME Drift Physics.
- **Visual Asset:** **[IMAGE 5: React Incident Management Dashboard UI Mockup]**

---

# 🎨 White-Theme AI Image Generation Prompts (Rich & Technical)

TIP

Zip your vault folder (`sih-2026-vault/Oiled-SIH/`), attach it to ChatGPT or Gemini, and copy-paste these prompts.

---

### 🎨 Image Prompt 1 (Slide 2): Complete System Overview Graphic

text

Analyze the attached vault zip for project 'Oiled'. Generate a clean, detailed presentation infographic on a crisp white background (#FFFFFF) illustrating an end-to-end satellite oil spill detection, drift physics, and vessel attribution system.

Design Style: Modern light-mode graphic, pure white background, subtle ocean blue (#0A2540), navy, and slate grey accents, clean structured layout, high legibility, zero text errors.

Visual Flow (5 connected steps across white background):

1. SATELLITE INGESTION: Sentinel-1 SAR satellite scanning ocean surface (dual-pol VV/VH).

2. DUAL-STAGE AI: CNN triage classifier filtering lookalikes + U-Net semantic segmentation drawing slick outline.

3. SLICK METRICS: Polygon displaying Surface Area (km²), Perimeter (km), and Spatial Centroid.

4. DRIFT PHYSICS: Forward/backward Lagrangian particle trajectories driven by 10m wind and ocean current vectors forming an origin search window.

5. AIS VESSEL RANKING: Historical ship tracks intersecting the origin window with ranked candidate score cards (e.g. #1 Vessel Alpha - 89% Match).

Rich technical details, clean light aesthetic, visually structured for hackathon presentation slides.

---

### 🎨 Image Prompt 2 (Slide 3): Technical Solution Pipeline Diagram

text

Generate a clean, detailed technical software architecture flowchart on a white background (#FFFFFF) for the 'Oiled' platform (context attached in zip).

Design Style: Light-mode software architecture diagram, structured rounded card nodes, white background, slate grey lines, crisp cyan and navy callout accents, clear typography.

Detailed Nodes to Display:

- Input: Sentinel-1 Dual-Pol (VV/VH) SAR COG Tiles (512x512)

- Preprocessing: Radiometric Sigma0 dB Calibration & Valid Ocean Masking (Rasterio)

- Module 1: ResNet Triage Classifier (Filters clean sea & radar lookalikes)

- Module 2: PyTorch U-Net Segmentation (ResNet-34 Backbone, BCE+Dice Loss)

- Module 3: GeoPandas Geometry Service (Outputs GeoJSON Polygon, Area km², Centroid)

- Module 4: NumPy Drift Engine (Lagrangian Particle Ensemble with ERA5 wind & CMEMS currents)

- Module 5: PostGIS/SQLite AIS Engine (Spatial Bounding Box Query & Trajectory Normalizer)

- Module 6: Multi-Criteria Ranker (Scores proximity, heading alignment, and SOG anomalies)

- Output: React Web Dashboard (MapLibre GL Map, Temporal Slider, Candidate Cards)

Technically rich, clear horizontal structure, highly legible on white presentation slides.

---

### 🎨 Image Prompt 3 (Slide 4): Model Validation & Benchmark Report Card

text

Create a clean white-theme performance report card graphic showcasing deep learning model validation metrics and SAR segmentation outputs (U-Net + ResNet-34).

Design Style: Light mode analytics report card, crisp white background (#FFFFFF), light grey card borders, navy typography, soft green status indicators, clean data presentation.

Content Layout:

- Top Title: Model Performance & Validation Benchmark

- Stat Card 1: Validation IoU: "0.7899" (Blue progress ring)

- Stat Card 2: Validation Dice / F1: "0.8513" (Green status badge)

- Stat Card 3: Validation Loss: "0.3619"

- Stat Card 4: Processing Speed: "< 2.0 sec / Scene" (24.4M Parameters)

- Bottom Section: Dual image comparison showing:

  (Left) Raw Sentinel-1 SAR Radar Image tile

  (Right) Precise U-Net Binarized Slick Mask Overlay with extracted GeoJSON boundary.

Clean white theme, rich metric details, executive technical presentation quality.

---

### 🎨 Image Prompt 4 (Slide 5): Impact & Benefits Infographic

text

Generate a clean, structured visual infographic on a pure white background (#FFFFFF) depicting the 3 core impact pillars of the 'Oiled' platform:

1. Environmental Protection: Minimal icon of marine ecosystem protected by an ocean shield, labeled "Coastal Ecosystem Protection (Slick Boundary Extraction)".

2. Operational Readiness: Icon of a radar dish and alert dashboard, labeled "NTRO Operational Readiness (Rapid Alert Within Minutes)".

3. Economic Efficiency: Icon of open satellite nodes and data feeds, labeled "Cost Efficiency (Open Sentinel-1 & ERA5/CMEMS Data)".

Design Style: Clean vector illustrations, white background, soft sky-blue, navy, and slate color scheme, structured cards, highly legible.

---

### 🎨 Image Prompt 5 (Slide 6): React Incident Dashboard UI Screenshot

text

Generate a detailed, clean white-theme desktop web application UI mockup of a React & MapLibre GL maritime incident management interface named 'Oiled'.

Design Style: Light-mode web SaaS interface, white navigation header bar, soft light-grey map styling, slate text, clean modern SaaS aesthetic (Stripe / Mapbox Light style).

UI Components to Render:

- Top Header: "Oiled — Marine Incident Platform" with nav tabs (Incident Map, Analytics, Data Logs).

- Main Map View: Soft grey ocean map displaying a dark blue oil slick polygon, blue particle drift trajectories, and numbered vessel markers.

- Right Intelligence Panel (White card):

  - Incident Details: Area: 14.2 km² | Perimeter: 18.6 km | Confidence: 94.2%

  - Ranked Candidate Vessels:

    #1 Vessel Alpha (MMSI: 235012345) — 89.4% Match (High Proximity, Heading Aligned)

    #2 Vessel Beta (MMSI: 412098765) — 64.1% Match (Temporal Gap Flagged)

- Bottom Control: Time scrubber timeline with play/pause buttons.

Rich UI details, realistic white-theme SaaS web app screenshot.