"""Model architectures: CNN triage classifier, consensus engine, and U-Net segmentation."""

from oiled.models.segmentation import (
    BCEDiceLoss,
    build_unet_segmentation_model,
    compute_dice,
    compute_iou,
)
from oiled.models.triage import (
    CLASS_NAMES,
    LightweightSARClassifier,
    TriageDecision,
    build_triage_classifier,
    evaluate_consensus,
)
from oiled.models.evaluation import (
    compute_precision_recall_curve_stats,
    compute_expected_calibration_error,
    compute_brier_score,
    evaluate_scene_triage,
)
from oiled.models.characterize import (
    AgeInterval,
    SlickCharacterization,
    fay_surface_tension_hours,
    morphology_age_prior,
    wind_gate,
    characterize_slick,
    characterization_to_dict,
)

__all__ = [
    "build_unet_segmentation_model",
    "BCEDiceLoss",
    "compute_iou",
    "compute_dice",
    "CLASS_NAMES",
    "LightweightSARClassifier",
    "TriageDecision",
    "build_triage_classifier",
    "evaluate_consensus",
    "compute_precision_recall_curve_stats",
    "compute_expected_calibration_error",
    "compute_brier_score",
    "evaluate_scene_triage",
    "wind_gate",
    "fay_surface_tension_hours",
    "morphology_age_prior",
    "characterize_slick",
    "characterization_to_dict",
    "SlickCharacterization",
    "AgeInterval",
]
