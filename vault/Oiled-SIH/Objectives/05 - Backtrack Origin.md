---
title: Estimate Origin Envelope
component: 5
---

# Component 5 — Estimate Origin Envelope

## Goal

Convert backward trajectories into the spatial-temporal search envelope used to query AIS.

## Output

```text
OriginEnvelope
  candidate region polygon(s)
  start/end UTC window
  confidence/coverage description
  drift assumptions and forcing version
```

## Method

- Choose a defensible backward horizon based on data quality and case context.
- Aggregate particle positions into a region/contour for each time horizon.
- Preserve more than one plausible region if the ensemble splits.
- Pass the complete envelope to AIS filtering; do not reduce it to a centroid.

## Rule

The origin is an inferred search region and time window, not a claim that the release happened at a precise point.
