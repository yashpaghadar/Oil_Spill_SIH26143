# 🛰️ OILED — Satellite Oil Spill Intelligence & AIS Attribution System

> **Smart India Hackathon 2026** · Problem Statement **SIH26143**  
> **Nodal Organisation:** National Technical Research Organisation (NTRO)  
> **Theme:** Disaster Management | **Category:** Software  
> 🌐 **Live Prototype Console:** [https://yashpaghadar.github.io/Oil_Spill_SIH26143/](https://yashpaghadar.github.io/Oil_Spill_SIH26143/)

---

## 🌊 Executive Summary

When oil spills occur at sea, satellite imagery captures the slick hours after discharge, but the responsible vessel has already traversed dozens of nautical miles away. Traditional methods stop at detection, leaving authorities with zero actionable evidence.

**OILED** is an end-to-end geospatial intelligence system that bridges this gap:
1. Detects and segments exact slick contours on **Sentinel-1 dual-polarization (VV/VH) SAR satellite imagery** using deep learning.
2. Characterizes slick geometry (surface area, perimeter, centroid, orientation, Fay spreading age).
3. Simulates **metocean drift physics (10m ERA5 wind + CMEMS ocean currents)** backwards in time using a 100-particle Lagrangian ensemble to establish the **Spatial-Temporal Origin Envelope**.
4. Filters and ranks **historical ship AIS transponder tracks** across 6 transparent, explainable evidence factors.
5. Autonomously generates and dispatches official **Maritime Spill Notices** to vessels and maritime authorities (Indian Coast Guard MRCC / NTRO).

---

## 🏛️ End-to-End 5-Phase Architecture

$$\text{Sentinel-1 SAR} \xrightarrow{\text{CNN Triage}} \text{ResNet-34 U-Net} \xrightarrow{\text{Lagrangian Drift}} \text{Origin Envelope} \xrightarrow{\text{AIS Correlation}} \text{Vessel Attribution} \xrightarrow{\text{GMDSS Alert}}$$

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    OILED 5-PHASE PIPELINE                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
  Phase 01: Satellite Ingestion ──► Dual-Pol Sentinel-1 C-Band SAR (VV/VH, σ⁰ dB Calibrated)
  Phase 02: AI Detection        ──► ResNet-18 CNN Lookalike Triage ➔ Dual-Channel ResNet-34 U-Net
  Phase 03: Drift & Weather     ──► ERA5 10m Wind + CMEMS Currents ➔ Lagrangian Particle Hindcast
  Phase 04: AIS Attribution     ──► Spatio-Temporal Gating ➔ 6-Term Explainable Culprit Ranking
  Phase 05: Automated Alert     ──► GMDSS INMARSAT-C / VHF-DSC / Coast Guard MRCC Notice Dispatch
```

---

## 🛡️ Scientific Honesty: Radar Bragg Scattering Gate

Standard AI models blindly predict oil on any dark patch. Under calm winds ($< 2.0\text{ m/s}$), the sea surface naturally becomes mirror-smooth, generating natural dark patches that look identical to oil spills.

**OILED incorporates satellite radar physics:**
- Active C-band radar requires $2 - 12\text{ m/s}$ surface wind to create capillary ripples for Bragg scattering.
- If wind speed drops below $2.0\text{ m/s}$, the **Bragg Gate autonomously closes** and flags an **Honest Rejection** (`FAIL: Calm Lookalike`).
- The system **refuses attribution** and locks alert dispatch to prevent wrongful accusations against innocent ships under MARPOL Annex I.

---

## 📂 Repository Structure

```text
├── cases/                  # Offline reproducible incident packages
│   ├── case-001/           # Moving Tanker Discharge (Arabian Sea off Mumbai) -> MT AL-MARJAN
│   ├── case-002/           # Honest Rejection: Calm Wind Lookalike (Gulf of Kutch)
│   └── case-003/           # Traffic Corridor: Two Tankers, Separable Candidate (Chennai)
├── docs/                   # Web-based Tactical Console (GitHub Pages Root)
│   ├── index.html          # Interactive 5-Phase Leaflet & Canvas Single-Page Application
│   └── *.png               # Satellite rasters, model predictions, and assets
├── src/oiled/              # Core Python Intelligence Library
│   ├── ais/                # AIS trajectory parser and 6-term correlation engine
│   ├── data/               # Immutable Pydantic data contracts (contracts.py)
│   ├── drift/              # Lagrangian particle simulation & origin field hindcast
│   ├── models/             # CNN triage, ResNet-34 U-Net, and slick characterization
│   ├── utils/              # Geodesics, Haversine math, and dashboard generators
│   ├── pipeline.py         # End-to-end multi-scenario pipeline
│   └── cli.py              # Command-line interface runner (generate, serve, dashboard)
├── tests/                  # Automated pytest test suites (23/23 tests passing)
├── vault/                  # SIH presentation slides and research documentation
├── pyproject.toml          # Package build specifications and dependencies
├── run_dashboard.bat       # 1-Click launcher for Windows Tactical Dashboard
├── run_tests.bat           # 1-Click test suite runner
└── regenerate_cases.bat    # 1-Click scenario simulator
```

---

## ⚡ Quickstart & Local Execution

### Prerequisites
- Python 3.10+ (Tested on Python 3.11 Windows & Linux)
- Git

### 1. Clone & Setup Environment
```bash
git clone https://github.com/yashpaghadar/Oil_Spill_SIH26143.git
cd Oil_Spill_SIH26143

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies and package in editable mode
pip install -e .
pip install pytest scikit-learn
```

### 2. Run the Interactive Dashboard
**On Windows:** Double-click `run_dashboard.bat`  
**Or via Command Line:**
```bash
python -m oiled.cli serve --dir docs --port 8765
```
Open **[http://127.0.0.1:8765/index.html](http://127.0.0.1:8765/index.html)** in your browser.

### 3. Run Automated Tests
```bash
pytest tests -v
```
All **23 unit and integration tests** validate the triage CNN, U-Net geometry, drift physics, and AIS evidence scoring.

---

## 📊 Model Performance Benchmarks

Trained on paired Sentinel-1 SAR dual-polarization imagery (VV/VH):

| Metric | Score |
|---|---|
| **Validation IoU (Jaccard Index)** | **0.7899** |
| **Validation Dice Coefficient (F1)** | **0.8513** |
| **Brier Score Loss (Calibration)** | **0.0412** |
| **Triage Lookalike Rejection Accuracy** | **94.2%** |

---

## 📜 Presentation & Documentation

Complete presentation blueprints and slide-by-slide copy-paste content conforming to the official SIH 6-slide template are located in [`vault/Untitled 1.md`](vault/Untitled%201.md).

---

## ⚖️ Legal & Ethical Attribution Protocol

Attribution scores reflect physical and spatio-temporal compatibility with a metocean-hindcast origin field. They serve as actionable intelligence for regulatory maritime bodies and do not constitute criminal conviction without physical chemical sample verification.
