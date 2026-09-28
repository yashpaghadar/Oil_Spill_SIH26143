---
title: System Technology Stack
---

# Technology Stack

The **Oiled** system features a **React** frontend for the graphical user interface (GUI) coupled with a clean, Python-based processing pipeline.

## 🛠️ Core Technology Components

| Layer | Technology Choice | Purpose |
|---|---|---|
| **Frontend GUI** | **React** (with MapLibre GL / Leaflet) | Modern, responsive web user interface for map layer inspection, drift temporal playback, and vessel ranking |
| **Backend API** | FastAPI / Python 3.10+ | Lightweight REST API serving geospatial GeoJSON layers, model results, and vessel tracks to the React GUI |
| **Deep Learning** | PyTorch | U-Net model for dual-channel (VV/VH) oil slick segmentation + lightweight ResNet for tile triage |
| **Geospatial Processing** | Rasterio + GeoPandas | Reading GeoTIFF SAR rasters, spatial CRS transformations, and GeoJSON polygon operations |
| **Drift Physics Engine** | NumPy + SciPy | Vectorized Lagrangian particle drift simulation (10m wind + surface currents) |
| **Data & Vector Store** | SQLite / GeoPackage + Local COGs | Simple, zero-configuration file storage for rasters, slick geometries, and AIS tracks |

---

## ⚙️ Pipeline & GUI Architecture

```text
Sentinel-1 GeoTIFF
   │
   ▼
Rasterio Preprocessing
   │
   ▼
PyTorch Triage & U-Net
   │
   ▼
GeoPandas Polygon Extraction
   │
   ▼
NumPy Drift Ensemble
   │
   ▼
AIS Trajectory Ranking
   │
   ▼
FastAPI Backend
   │
   ▼
React Web GUI
```

---

## 📑 Preprocessing & Interface Rules

1. **GUI Technology Standard:** React is the dedicated, exclusive frontend library for building all user interface components and map controls.
2. **Decoupled API:** The React GUI consumes standard GeoJSON and JSON endpoints provided by the Python FastAPI backend.
3. **2-Channel SAR Input:** Process calibrated Sentinel-1 VV and VH channels directly in decibels (dB).
4. **Simple Tiling:** Crop images into $512 \times 512$ tiles with 25% overlap for model inference.
