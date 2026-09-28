---
title: Characterize Spill Geometry
component: 2
---

# Component 2 — Characterize Spill Geometry

## Goal

Turn an accepted segmentation mask into map-ready measurements while preserving uncertainty.

## Process

```text
oil probability mask
→ threshold + connected components
→ map pixels through scene CRS
→ spill polygons
→ geometry and quality fields
```

## Measurements

- observation time (UTC);
- polygon/centroid and CRS;
- area and perimeter;
- major-axis orientation and length where meaningful;
- number of components; and
- segmentation confidence/quality flags.

## Rules

- Derive measures from the mask, not a bounding box.
- Calculate area in a suitable projected CRS, then render in latitude/longitude.
- Report estimates with model and geolocation uncertainty; do not imply laboratory precision.

Output: `SpillEvent`. Next: [[Objectives/04 - Model Spill Drift]].
