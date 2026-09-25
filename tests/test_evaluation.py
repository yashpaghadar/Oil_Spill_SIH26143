"""Unit tests for Stage 3 evaluation and calibration metrics."""

import unittest
import numpy as np
from oiled.models.evaluation import (
    compute_precision_recall_curve_stats,
    compute_expected_calibration_error,
    compute_brier_score,
    evaluate_scene_triage,
)


class TestEvaluationMetrics(unittest.TestCase):
    def test_precision_recall_curve(self):
        y_true = np.array([0, 0, 1, 1, 1, 0, 1, 0])
        y_prob = np.array([0.1, 0.2, 0.8, 0.9, 0.7, 0.3, 0.65, 0.4])
        res = compute_precision_recall_curve_stats(y_true, y_prob)
        self.assertIn("best_threshold", res)
        self.assertGreater(res["average_precision"], 0.7)
        self.assertGreater(res["best_f1"], 0.7)

    def test_expected_calibration_error(self):
        y_true = np.array([0, 0, 1, 1])
        # Well calibrated
        y_prob_good = np.array([0.05, 0.05, 0.95, 0.95])
        ece_good = compute_expected_calibration_error(y_true, y_prob_good, n_bins=5)
        # Poorly calibrated
        y_prob_bad = np.array([0.9, 0.9, 0.1, 0.1])
        ece_bad = compute_expected_calibration_error(y_true, y_prob_bad, n_bins=5)
        self.assertLess(ece_good, ece_bad)

    def test_brier_score(self):
        y_true = np.array([0, 1])
        y_prob = np.array([0.0, 1.0])
        score = compute_brier_score(y_true, y_prob)
        self.assertAlmostEqual(score, 0.0)

    def test_evaluate_scene_triage(self):
        records = [
            {"scene_id": "oil_1", "category": "oil", "max_prob": 0.9, "oil_pixels": 200},
            {"scene_id": "oil_2", "category": "oil", "max_prob": 0.3, "oil_pixels": 10},
            {"scene_id": "lookalike_1", "category": "lookalike", "max_prob": 0.8, "oil_pixels": 100},
            {"scene_id": "lookalike_2", "category": "lookalike", "max_prob": 0.2, "oil_pixels": 0},
            {"scene_id": "clean_1", "category": "clean", "max_prob": 0.1, "oil_pixels": 0},
        ]
        summary = evaluate_scene_triage(records, threshold=0.5, min_slick_pixels=50)
        self.assertEqual(summary["oil_recall"], 0.5)
        self.assertEqual(summary["lookalike_false_alert_rate"], 0.5)
        self.assertEqual(summary["clean_false_alert_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
