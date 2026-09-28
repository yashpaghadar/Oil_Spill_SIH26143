---
title: Visualize Incident for Review
component: 9
---

# Component 9 — Visualize Incident for Review

## System Function

Render comprehensive geospatial incident dashboards, enabling analysts to inspect satellite detections, particle drift envelopes, historical AIS tracks, and candidate vessel attributions.

## Visual Layer Map

- **SAR Imagery Layer:** Raw and calibrated Sentinel-1 VV/VH GeoTIFF/COG rasters with ocean/land masks.
- **Segmentation Layer:** Binarized oil slick masks, probability heatmaps, and extracted vector polygons.
- **Slick Metrics Overlay:** Computed surface area ($\text{km}^2$), perimeter, orientation vector, and centroid coordinates.
- **Hydrodynamic Drift Layer:** Interactive forward/backward Lagrangian particle trajectories and origin envelope contours across time steps.
- **AIS Traffic Layer:** Filtered vessel positions, trajectories, and speed/course profiles.
- **System Provenance Panel:** Audit panel displaying model version hashes, data provider IDs, preprocessing parameters, and pipeline execution logs.

## Interactive Capabilities

- **Temporal Playback:** Slide through historical time windows to visualize drift progression and vessel movements.
- **Candidate Inspection:** Click any candidate vessel card to view evidence breakdowns (proximity, heading compatibility, AIS signal quality).
- **Incident Report Export:** Generate standardized PDF/GeoJSON intelligence reports for operational stakeholders.

---

The React frontend client communicates with backend FastAPI microservices via REST and WebSocket interfaces. The React user interface renders map layers using MapLibre GL / Deck.gl / Leaflet, ensuring a clean separation between React UI state and Python core compute backends.
