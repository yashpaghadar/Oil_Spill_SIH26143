---
title: Model Spill Drift
component: 4
---

# Component 4 — Model Spill Drift

## Goal

Simulate plausible forward and backward movement from the observed spill using wind/current fields and parameter uncertainty.

## Initial model

```text
particle velocity = surface current + windage × 10 m wind
```

Seed particles across the spill polygon. Vary windage and forcing perturbations across the ensemble. Interpolate all fields in time/space with units and coordinate transforms tested.

## Output

```text
TrajectoryEnsemble
  forward paths
  backward paths
  parameters + forcing sources
  uncertainty regions at chosen time horizons
```

## Rules

- This is physics-based modelling, not an ML output.
- Never display one deterministic path without its uncertainty envelope.
- A future PyGNOME-compatible engine is a plug-in replacement behind the same contract.

Data: [[Data/02 - Environmental Data]].
