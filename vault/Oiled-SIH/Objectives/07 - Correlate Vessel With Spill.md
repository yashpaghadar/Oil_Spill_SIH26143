---
title: Correlate Vessel Evidence
component: 7
---

# Component 7 — Correlate Vessel Evidence

## Goal

Filter AIS tracks using the inferred origin envelope, then calculate explainable evidence features for compatible tracks.

## Exclusion first

Reject a vessel when its valid track has no presence near the origin envelope during the candidate time range. Record the reason: spatial mismatch, temporal mismatch, insufficient data, or data-quality issue.

## Evidence features

| Feature | Question |
|---|---|
| Proximity | How near was a valid position/segment to the origin region? |
| Timing | How close was it to the candidate release window? |
| Track compatibility | Did the trajectory intersect or approach plausible source areas? |
| Direction/behaviour | Are heading or speed changes compatible with the scenario? |
| AIS quality | Is the supporting track complete and plausible enough to trust? |

These are evidence features, not labels proving pollution.
