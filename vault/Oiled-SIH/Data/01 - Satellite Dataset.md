---
title: Satellite Imagery Data Register
---

# Satellite Imagery Data Register

## Canonical Input Specification

| Property | Production Standard |
|---|---|
| **Sensor & Mode** | Sentinel-1 Synthetic Aperture Radar (SAR) Interferometric Wide (IW) Ground Range Detected (GRD) |
| **Polarisation Channels** | Dual-polarisation VV and VH co-registered channels |
| **Radiometric Processing** | Calibrated Sigma0 ($\sigma^0$) values expressed in decibels (dB) |
| **Raster Format** | Cloud-Optimized GeoTIFF (COG) with embedded Spatial Reference System (EPSG:4326 / UTM) |
| **Metadata Requirements** | Acquisition UTC timestamp, Scene UUID, Orbit direction, Sub-swath metadata, Source provider license |
| **Labels & Annotations** | Georeferenced binary masks and GeoJSON polygons categorized into high-confidence oil slicks and lookalike features |
| **Spatial Tiling** | $512 \times 512$ pixel tiles with 64-pixel overlap, georeferenced bounding boxes, and valid ocean bitmasks |

---

## Dataset Roles & Repositories

### 1. Sentinel-1 SAR Oil Spill Benchmark Corpus
- **Primary Training Corpus (Part I):** https://zenodo.org/records/8346860 — Dual-pol scenes providing paired oil slick annotations and clean ocean patches.
- **Held-Out Evaluation Benchmark (Part III):** https://zenodo.org/records/13761290 — Scene-level held-out test benchmark for leakage-safe validation.

---

## Data Governance & Quality Standards

- **Scene-Level Partitioning:** Individual SAR scenes belong exclusively to one split (Training, Validation, or Held-Out Test) to prevent spatial autocorrelation leakage.
- **Semantic Mask Precision:** Ground truth is defined by pixel-level masks and vectors rather than coarse bounding boxes.
- **Lookalike Categorization:** Non-oil dark ocean features (low wind areas, biogenic slicks, internal waves) are explicitly tagged in the label taxonomy.
- **Traceable Lineage:** Every ingested raster scene retains raw source metadata, preprocessing version hashes, and licensing terms in the system data store.
