---
title: Environmental Forcing Data Register
---

# Environmental Forcing Data Register

## System Function & Integration

Hydrodynamic current vectors and 10m atmospheric wind fields drive the Lagrangian particle drift simulation engine within **Oiled**. These metocean forcing fields are ingested dynamically to compute forward slick migration and backward origin envelopes.

---

## Environmental Field Data Schema

```text
EnvironmentalField
  ├── provider_id        : string (e.g. "ECMWF_ERA5", "COPERNICUS_MARINE")
  ├── source_revision    : string
  ├── time_bounds_utc    : (datetime_start, datetime_end)
  ├── spatial_extent     : (min_lon, min_lat, max_lon, max_lat, EPSG)
  ├── grid_resolution    : float (degrees or km)
  ├── u10, v10           : 2D arrays (10m surface wind components in m/s)
  ├── uo, vo             : 2D arrays (ocean surface current components in m/s)
  ├── interpolation_type : enum ("bilinear", "bicubic", "nearest")
  └── quality_mask       : 2D array (valid marine mask & data quality flags)
```

---

## Operational Data Sources

| Environmental Variable | Operational Data Provider | Access Mechanism |
|---|---|---|
| **10m Surface Wind Vectors ($u_{10}, v_{10}$)** | ECMWF ERA5 Reanalysis / GFS Forecast | Copernicus Climate Data Store (CDS) API |
| **Ocean Surface Currents ($u_o, v_o$)** | Copernicus Marine Environment Monitoring Service (CMEMS) | CMEMS Marine Toolbox API / NetCDF Subsets |

---

## Drift Velocity Physics Engine

Slick drift velocity $\vec{V}_{\text{drift}}$ is computed as the vector sum of ocean surface current and wind leeway:

$$\vec{V}_{\text{drift}} = \vec{V}_{\text{current}} + \gamma \cdot \vec{V}_{\text{wind}}$$

where $\gamma$ is the windage coefficient (typically set between $0.02$ and $0.04$ depending on slick thickness and oil type).

An ensemble of Lagrangian particles is propagated across plausible perturbations of windage and current velocity fields to generate probabilistic trajectory envelopes with explicit spatial uncertainty bounds.
