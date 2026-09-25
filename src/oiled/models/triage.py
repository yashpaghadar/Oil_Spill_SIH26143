"""Lookalike rejection and triage classification models for dual-channel Sentinel-1 SAR imagery."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import torch
import torch.nn as nn
import torchvision.models as tv_models

CLASS_NAMES = ["clean", "lookalike", "oil"]


class ConvBlock(nn.Module):
    def __init__(self, in_c: int, out_c: int):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_c, out_c, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_c),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.conv(x)


class LightweightSARClassifier(nn.Module):
    """Compact fallback CNN for dual-channel SAR triage (VV/VH)."""

    def __init__(self, in_channels: int = 2, num_classes: int = 3):
        super().__init__()
        self.features = nn.Sequential(
            ConvBlock(in_channels, 32),
            ConvBlock(32, 64),
            ConvBlock(64, 128),
            ConvBlock(128, 256),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(256, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.features(x)
        return self.fc(feat)


def build_triage_classifier(
    backbone: str = "resnet18",
    in_channels: int = 2,
    num_classes: int = 3,
    pretrained: bool = False,
) -> nn.Module:
    """Build a 2-channel input SAR triage classifier.

    Args:
        backbone: 'resnet18' or 'custom_lightweight'.
        in_channels: Number of input channels (2 for VV + VH).
        num_classes: Output classes (clean, lookalike, oil).
        pretrained: If True, loads ImageNet pretrained weights and adapts conv1.
    """
    if backbone == "custom_lightweight":
        return LightweightSARClassifier(in_channels=in_channels, num_classes=num_classes)

    if backbone == "resnet18":
        weights = tv_models.ResNet18_Weights.DEFAULT if pretrained else None
        model = tv_models.resnet18(weights=weights)

        # Adapt first conv layer for in_channels (e.g. 2 channels instead of 3)
        orig_conv1 = model.conv1
        new_conv1 = nn.Conv2d(
            in_channels,
            orig_conv1.out_channels,
            kernel_size=orig_conv1.kernel_size,
            stride=orig_conv1.stride,
            padding=orig_conv1.padding,
            bias=False,
        )

        if pretrained:
            with torch.no_grad():
                # Copy first 2 channels from RGB weights or average
                new_conv1.weight[:, :min(in_channels, 3)] = orig_conv1.weight[:, :min(in_channels, 3)]

        model.conv1 = new_conv1
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model

    raise ValueError(f"Unsupported backbone: {backbone}. Choose 'resnet18' or 'custom_lightweight'.")


@dataclass
class TriageDecision:
    """Consensus decision output combining segmentation evidence and triage classification."""
    scene_id: str
    decision: str  # 'ALERT' or 'REJECTED'
    triage_class: str  # 'oil', 'lookalike', 'clean'
    triage_confidence: float
    seg_max_prob: float
    seg_mean_prob: float
    seg_oil_pixels: int
    rejection_reason: Optional[str] = None
    calibration_status: Dict[str, Any] = None


def evaluate_consensus(
    scene_id: str,
    seg_max_prob: float,
    seg_oil_pixels: int,
    triage_probs: torch.Tensor | list[float],
    seg_threshold: float = 0.50,
    min_slick_pixels: int = 50,
    triage_confidence_threshold: float = 0.50,
) -> TriageDecision:
    """Evaluate agreement between segmentation and triage models.

    Args:
        scene_id: Identifier for the SAR scene.
        seg_max_prob: Maximum pixel probability from segmentation model.
        seg_oil_pixels: Count of pixels >= seg_threshold.
        triage_probs: Probabilities for [clean, lookalike, oil].
        seg_threshold: Threshold to confirm segmentation detection.
        min_slick_pixels: Minimum pixel area to consider a valid slick.
        triage_confidence_threshold: Minimum confidence required from classifier.
    """
    if isinstance(triage_probs, torch.Tensor):
        probs = triage_probs.detach().cpu().numpy().tolist()
    else:
        probs = list(triage_probs)

    clean_p, lookalike_p, oil_p = probs[0], probs[1], probs[2]
    pred_idx = int(torch.tensor(probs).argmax().item())
    pred_class = CLASS_NAMES[pred_idx]
    pred_conf = float(probs[pred_idx])

    seg_has_oil = (seg_max_prob >= seg_threshold) and (seg_oil_pixels >= min_slick_pixels)

    # Agreement rules
    if seg_has_oil and pred_class == "oil" and oil_p >= triage_confidence_threshold:
        return TriageDecision(
            scene_id=scene_id,
            decision="ALERT",
            triage_class="oil",
            triage_confidence=oil_p,
            seg_max_prob=seg_max_prob,
            seg_mean_prob=0.0,
            seg_oil_pixels=seg_oil_pixels,
            rejection_reason=None,
        )

    # Rejection: Lookalike flagged by triage
    if pred_class == "lookalike" or lookalike_p > 0.40:
        return TriageDecision(
            scene_id=scene_id,
            decision="REJECTED",
            triage_class="lookalike",
            triage_confidence=lookalike_p,
            seg_max_prob=seg_max_prob,
            seg_mean_prob=0.0,
            seg_oil_pixels=seg_oil_pixels,
            rejection_reason="lookalike_low_backscatter_smooth_water",
        )

    # Rejection: Clean water / background noise
    if pred_class == "clean" or not seg_has_oil:
        reason = "clean_sea_insufficient_signal" if not seg_has_oil else "triage_clean_disagreement"
        return TriageDecision(
            scene_id=scene_id,
            decision="REJECTED",
            triage_class="clean",
            triage_confidence=clean_p,
            seg_max_prob=seg_max_prob,
            seg_mean_prob=0.0,
            seg_oil_pixels=seg_oil_pixels,
            rejection_reason=reason,
        )

    # Default fallback
    return TriageDecision(
        scene_id=scene_id,
        decision="REJECTED",
        triage_class=pred_class,
        triage_confidence=pred_conf,
        seg_max_prob=seg_max_prob,
        seg_mean_prob=0.0,
        seg_oil_pixels=seg_oil_pixels,
        rejection_reason="confidence_below_operating_threshold",
    )
