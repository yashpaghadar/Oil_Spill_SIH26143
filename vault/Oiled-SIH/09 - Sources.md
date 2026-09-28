---
title: System Data & Technical Reference Register
---

# System Data & Technical Reference Register

This document maintains the official registry of data sources, technical standards, and scientific literature governing the **Oiled** system.

## Operational & Regulatory Context

- **SIH 2026 Problem Statement Brief:** https://sih.gov.in/sih2026PS
- **SIH26143 Specification:** https://sih-explorer.amanuniyal47.workers.dev/problem/SIH26143
- **EMSA CleanSeaNet Operational Framework:** https://www.emsa.europa.eu/csn-menu.html
- **NOAA Oil Spill Trajectory Modeling Overview:** https://response.restoration.noaa.gov/node/400
- **NOAA PyGNOME Particle Drift Engine:** https://response.restoration.noaa.gov/oil-and-chemical-spills/oil-spills/pygnome

---

## Satellite Synthetic Aperture Radar (SAR) Data & Labels

- **Sentinel-1 SAR Oil Spill Benchmark Corpus (Part I):** https://zenodo.org/records/8346860
- **Held-Out Validation Benchmark (Part III):** https://zenodo.org/records/13761290
- **Peer-Reviewed SAR Oil Spill Dataset Paper:** https://doi.org/10.1016/j.marpolbul.2024.116549
- **Copernicus Sentinel Data Access & Attribution License:** https://cds.climate.copernicus.eu/licences/ec-sentinel
- **Zenodo Repository Data Governance Guidance:** https://support.zenodo.org/help/en-gb/2-content/21-can-i-get-permission-to-use-a-specific-record

---

## MetOcean & Environmental Forcing Data

- **ECMWF ERA5 Atmospheric Reanalysis (10m Surface Wind Vectors):** https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=documentation
- **Copernicus Marine Service (Global Ocean Surface Currents & Physics):** https://data.marine.copernicus.eu/
- **Copernicus Marine Toolbox API & Automated Subset Downloader:** https://help.marine.copernicus.eu/en/articles/8283072-copernicus-marine-toolbox-api-subset

---

## AIS Vessel Tracking Standards

- **MarineCadastre AccessAIS Format & Spatial Infrastructure:** https://marinecadastre.gov/accessais/
- **NOAA National AIS Data Dictionary & Field Specifications:** https://www.fisheries.noaa.gov/inport/item/80362
- **IMO Regulations on Automatic Identification System (AIS) Carriage Requirements:** https://www.imo.org/en/OurWork/Safety/Pages/AIS.aspx

---

## Scientific Foundations of System Design

Operational marine surveillance frameworks (e.g., CleanSeaNet) rely on a combined approach: **dual-channel SAR segmentation** for precise slick boundary extraction, **hydrodynamic particle trajectory modeling** for drift calculation, and **spatio-temporal AIS correlation** for candidate vessel ranking. This multi-layered design ensures that system outputs remain scientifically robust, transparent, and defensible for analyst evaluation.
