"""Unit tests for Stage 3 triage models and consensus engine."""

import unittest
import torch
from oiled.models.triage import (
    build_triage_classifier,
    evaluate_consensus,
    CLASS_NAMES,
)


class TestTriageModel(unittest.TestCase):
    def test_custom_lightweight_classifier_forward(self):
        model = build_triage_classifier(backbone="custom_lightweight", in_channels=2, num_classes=3)
        dummy_input = torch.randn(2, 2, 256, 256)
        output = model(dummy_input)
        self.assertEqual(output.shape, (2, 3))

    def test_resnet18_2channel_forward(self):
        model = build_triage_classifier(backbone="resnet18", in_channels=2, num_classes=3, pretrained=False)
        dummy_input = torch.randn(2, 2, 224, 224)
        output = model(dummy_input)
        self.assertEqual(output.shape, (2, 3))

    def test_consensus_alert_on_agreement(self):
        decision = evaluate_consensus(
            scene_id="oil_scene_01",
            seg_max_prob=0.85,
            seg_oil_pixels=250,
            triage_probs=[0.05, 0.10, 0.85],  # [clean, lookalike, oil]
        )
        self.assertEqual(decision.decision, "ALERT")
        self.assertEqual(decision.triage_class, "oil")
        self.assertIsNone(decision.rejection_reason)

    def test_consensus_rejection_on_lookalike(self):
        decision = evaluate_consensus(
            scene_id="lookalike_scene_01",
            seg_max_prob=0.75,
            seg_oil_pixels=120,
            triage_probs=[0.10, 0.80, 0.10],  # Lookalike classified by triage
        )
        self.assertEqual(decision.decision, "REJECTED")
        self.assertEqual(decision.triage_class, "lookalike")
        self.assertEqual(decision.rejection_reason, "lookalike_low_backscatter_smooth_water")

    def test_consensus_rejection_on_clean_sea(self):
        decision = evaluate_consensus(
            scene_id="clean_scene_01",
            seg_max_prob=0.15,
            seg_oil_pixels=0,
            triage_probs=[0.95, 0.03, 0.02],
        )
        self.assertEqual(decision.decision, "REJECTED")
        self.assertEqual(decision.triage_class, "clean")


if __name__ == "__main__":
    unittest.main()
