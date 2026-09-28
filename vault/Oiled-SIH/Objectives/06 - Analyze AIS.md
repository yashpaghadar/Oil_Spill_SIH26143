---
title: Analyze AIS Tracks
component: 6
---

# Component 6 — Analyze AIS Tracks

## System Function

Ingest raw AIS message streams, filter anomalies, and normalize vessel trajectories into continuous, quality-aware tracks for spatial-temporal correlation.

## Schema Specification

```text
VesselTrack
  ├── mmsi               : integer (Maritime Mobile Service Identity)
  ├── vessel_name        : string
  ├── vessel_type        : string
  ├── timestamp_utc      : datetime
  ├── latitude           : float
  ├── longitude          : float
  ├── sog_knots          : float
  ├── cog_degrees        : float
  ├── data_source        : string ("TERRESTRIAL_AIS", "SATELLITE_AIS")
  └── quality_flags      : bitmask (gap_flag, speed_jump, interpolation_flag)
```

## Processing Engine

1. **Ingestion & Parsing:** Decode NMEA / JSON AIS payloads and validate UTC timestamps and spatial coordinate bounds.
2. **Track Sorting & Deduplication:** Partition messages by MMSI and sort chronologically.
3. **Anomaly & Quality Auditing:** Identify signal gaps, unrealistic speed-over-ground (SOG) spikes, or GPS noise.
4. **Trajectory Reconstruction:** Perform cubic spline interpolation across continuous intervals while flagging missing transmission windows.
5. **Database Indexing:** Persist normalized trajectories into PostGIS spatial databases indexed by spatial R-Tree and timestamp.

---

## Data Policy & Source Integrity

Historical AIS data streams undergo rigorous validation. Data feeds from terrestrial and satellite providers are tagged with source provenance flags. Synthetic or benchmark tracks used during offline testing are explicitly labeled as test data to maintain evidentiary integrity.
