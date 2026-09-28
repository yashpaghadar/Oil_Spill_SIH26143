---
title: AIS Data & Evidence Policy
---

# AIS Data & Evidence Policy

## Canonical Vessel Track Schema

```text
VesselTrack
  ├── mmsi               : integer (Maritime Mobile Service Identity)
  ├── vessel_name        : string
  ├── vessel_type        : string / IMO category
  ├── timestamp_utc      : datetime
  ├── latitude           : float (-90.0 to 90.0)
  ├── longitude          : float (-180.0 to 180.0)
  ├── sog_knots          : float (Speed Over Ground)
  ├── cog_degrees        : float (Course Over Ground)
  ├── data_source        : string ("TERRESTRIAL_AIS", "SATELLITE_AIS")
  └── quality_flags      : bitmask (GPS drift, speed anomaly, gap flag)
```

---

## AIS Data Ingestion & Normalization

1. **Multi-Source Ingestion:** Ingest raw AIS feeds from terrestrial receivers and satellite constellations (e.g., Spire, MarineTraffic, AISHub).
2. **Quality Audit & Interpolation:** Audit tracks for position jumps, invalid coordinates, or missing transmissions. Apply Hermite/cubic spline interpolation across valid segments to establish continuous vessel trajectories.
3. **Spatial Indexing:** Store normalized trajectories in PostGIS with R-Tree spatial indexing to enable fast spatial-temporal bounding box queries.

---

## Candidate Vessel Ranking Policy

The evidence ranking module evaluates candidate vessels intersecting the origin envelope based on four criteria:

1. **Spatial-Temporal Proximity:** Distance between the backtracked origin envelope and vessel trajectory at the estimated release time window.
2. **Route & Heading Alignment:** Compatibility between vessel course ($\text{COG}$) and the slick orientation/drift trajectory.
3. **Operational Behavior:** Sudden speed drops, prolonged loitering, or maneuvering pattern anomalies during ocean transit.
4. **Data Reliability & Quality:** Integrity of the vessel's AIS transmission stream, flagging any unexpected transmission blackouts.

```text
Overall Rank Score = w1 * Proximity + w2 * Heading + w3 * Behavior + w4 * SignalQuality
```

All outputs are structured as **Candidate Vessel Assessments** featuring individual score components, transparent rejection logs, and explicit disclaimer notices.
