"""Evaluation, calibration, and operating threshold utilities for Oiled Stage 3."""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    precision_recall_curve,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
)


def compute_precision_recall_curve_stats(
    y_true: np.ndarray,
    y_prob: np.ndarray,
) -> Dict[str, Any]:
    """Compute PR curve and Average Precision (AP)."""
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    ap = float(average_precision_score(y_true, y_prob))

    # Compute F1 scores along the curve
    eps = 1e-8
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + eps)
    best_idx = int(np.argmax(f1_scores))

    return {
        "average_precision": round(ap, 4),
        "best_threshold": float(thresholds[best_idx]),
        "best_f1": float(f1_scores[best_idx]),
        "best_precision": float(precision[best_idx]),
        "best_recall": float(recall[best_idx]),
        "thresholds": thresholds.tolist(),
        "precision": precision.tolist(),
        "recall": recall.tolist(),
    }


def compute_expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> float:
    """Compute Expected Calibration Error (ECE) for binary detection."""
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    total_samples = len(y_true)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        in_bin = (y_prob > bin_lower) & (y_prob <= bin_upper)
        bin_size = np.sum(in_bin)

        if bin_size > 0:
            bin_acc = np.mean(y_true[in_bin])
            bin_conf = np.mean(y_prob[in_bin])
            ece += (bin_size / total_samples) * np.abs(bin_acc - bin_conf)

    return float(ece)


def compute_brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Compute Brier Score (mean squared error of probabilistic predictions)."""
    return float(brier_score_loss(y_true, y_prob))


def evaluate_scene_triage(
    scene_records: List[Dict[str, Any]],
    threshold: float,
    min_slick_pixels: int = 50,
) -> Dict[str, Any]:
    """Evaluate scene-level alert performance and category breakdown.

    Each record should contain:
      - scene_id: str
      - category: 'oil' | 'lookalike' | 'clean'
      - max_prob: float
      - oil_pixels: int
    """
    total_by_cat = {"oil": 0, "lookalike": 0, "clean": 0}
    flagged_by_cat = {"oil": 0, "lookalike": 0, "clean": 0}

    for rec in scene_records:
        cat = rec["category"]
        if cat not in total_by_cat:
            total_by_cat[cat] = 0
            flagged_by_cat[cat] = 0

        total_by_cat[cat] += 1
        is_alert = (rec["max_prob"] >= threshold) and (rec["oil_pixels"] >= min_slick_pixels)
        if is_alert:
            flagged_by_cat[cat] += 1

    oil_recall = (
        flagged_by_cat["oil"] / total_by_cat["oil"]
        if total_by_cat["oil"] > 0
        else 0.0
    )
    lookalike_false_alert_rate = (
        flagged_by_cat["lookalike"] / total_by_cat["lookalike"]
        if total_by_cat["lookalike"] > 0
        else 0.0
    )
    clean_false_alert_rate = (
        flagged_by_cat["clean"] / total_by_cat["clean"]
        if total_by_cat["clean"] > 0
        else 0.0
    )

    return {
        "operating_threshold": threshold,
        "min_slick_pixels": min_slick_pixels,
        "oil_recall": round(oil_recall, 4),
        "lookalike_false_alert_rate": round(lookalike_false_alert_rate, 4),
        "clean_false_alert_rate": round(clean_false_alert_rate, 4),
        "breakdown": {
            cat: {
                "detected": flagged_by_cat[cat],
                "total": total_by_cat[cat],
                "alert_rate": round(flagged_by_cat[cat] / total_by_cat[cat], 4)
                if total_by_cat[cat] > 0
                else 0.0,
            }
            for cat in total_by_cat
        },
    }
