---
title: Candidate Vessel Assessment
component: 8
---

# Component 8 — Candidate Vessel Assessment

## Goal

Produce a transparent ordering of candidate vessels without representing it as causal attribution.

## Initial ranking design

Use deterministic, inspected component scores rather than a learned “culprit” classifier:

```text
assessment score =
  spatial compatibility
  + temporal compatibility
  + track compatibility
  + behaviour support
  + AIS data-quality adjustment
```

Weights and normalisation must be versioned and shown. The user must be able to see why a vessel was excluded or ranked.

## Output

```text
CandidateAssessment
  rank
  score and component breakdown
  supporting observations
  data gaps/exclusions
  disclaimer: candidate assessment, not proof
```

## Future rule

Only consider learned ranking after collecting verified historical incidents with known source-vessel outcomes. Evaluate it with ranking metrics such as Precision@k/NDCG, not synthetic stories alone.
