---
title: Validate Detection and Confidence
component: 3
---

# Component 3 — Validate Detection and Confidence

## Goal

Measure whether the model finds masks on new scenes and avoids false alerts on difficult negatives.

## Validation protocol

1. Assign entire scenes/events/orbits to train, validation or test.
2. Use validation scenes to tune probability and triage thresholds.
3. Keep the final benchmark sealed until thresholds are fixed.
4. Report public-core, lookalike-negative and external-domain results separately.
5. Inspect every high-confidence false alert and missed event.

## Required metrics

| Metric | Use |
|---|---|
| Oil IoU and Dice/F1 | mask overlap |
| Object/event recall | whether a spill is found at all |
| Precision and false-alert rate | review workload |
| False alerts on lookalikes | operational robustness |
| Area error | downstream geometry quality |
| ECE/Brier score | whether confidence is meaningful |

Pixel accuracy is not sufficient because water-background pixels dominate.

## Output

A versioned evaluation report and an approved operating threshold—not an unqualified accuracy claim.
