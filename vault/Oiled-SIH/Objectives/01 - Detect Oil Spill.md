---
title: Detect Oil Spill
component: 1
---

# Component 1 — Detect Oil Spill

## System Function

Process incoming Sentinel-1 SAR observations (VV/VH dual-polarisation) and generate calibrated, georeferenced **oil probability masks**, or log a scene-level triage rejection.

## Module Input

```text
Scene
  ├── VV/VH Sigma0 dB GeoTIFF/COG
  ├── valid ocean bitmask
  └── acquisition metadata (UTC, CRS, orbit direction)
```

## Processing Method

```text
Scene Triage Classifier (Lightweight CNN)
  ├── Candidate Oil Tile --> Route to Dense Segmentation
  └── Clean Sea / Lookalike --> Log Rejection & Exit
                │
                ▼
Dual-Channel U-Net Segmentation (in_channels=2)
  ├── Generates Pixel-Level Oil Probability Raster
  └── Applies Calibrated Confidence Thresholding
                │
                ▼
Detection Object Output
```

## Module Output

```text
Detection
  ├── oil_probability_mask_uri
  ├── binary_slick_mask
  ├── confidence_and_quality_flags
  └── metadata (model_hash, preprocessing_version, timestamp_utc)
```

## Operational Rules

- Input format remains 2-channel numeric SAR backscatter (VV/VH Sigma0 dB), avoiding lossy RGB/JPEG transformations.
- High probability pixels are assigned a **possible oil slick** classification until corroborated by analysts or multi-source evidence.
- Detection relies on semantic segmentation rather than bounding box detectors to preserve physical slick geometry.

---

## Baseline Segmentation Benchmark

The core segmentation engine is validated against held-out dual-polarisation SAR benchmark datasets:

| System Parameter | Specification |
|---|---|
| **Architecture** | U-Net with ResNet-34 Encoder Backbone |
| **Model Parameters** | 24.4 Million parameters |
| **Input Tensor Format** | 2 channels (VV + VH Sigma0 dB clipped to [-40, 10] dB) |
| **Spatial Tiling** | $512 \times 512$ px tiles with 384 px stride overlap |
| **Loss Function** | Combined BCE + Dice Loss |
| **Optimizer** | AdamW ($\text{lr}=10^{-4}, \text{weight\_decay}=10^{-4}$) |

### Validation Performance Benchmark

| Benchmark Metric | Target Performance |
|---|---|
| **Validation IoU (Intersection over Union)** | **0.7899** |
| **Validation Dice / F1 Score** | **0.8513** |
| **Validation Loss** | 0.3619 |

### Exported System Artifacts

- `seg_best.pt` — PyTorch model checkpoint.
- `unet_segmentation.onnx` — Exported ONNX Runtime inference artifact.
- `metrics.json` — System metric evaluation log.
- `manifest_part3_paired.csv` — Paired dataset scene manifest.
