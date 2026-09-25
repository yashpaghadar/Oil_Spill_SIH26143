"""U-Net segmentation model and losses for dual-channel Sentinel-1 SAR imagery."""

import torch
import torch.nn as nn
try:
    import segmentation_models_pytorch as smp
except ImportError:
    smp = None


def build_unet_segmentation_model(
    encoder_name: str = "resnet34",
    in_channels: int = 2,
    encoder_weights: str | None = None,
    activation: str | None = None,
) -> nn.Module:
    """Build a 2-channel input U-Net for SAR oil spill segmentation.

    Args:
        encoder_name: Backbone encoder name (e.g. 'resnet34').
        in_channels: Input channels (2 for Sentinel-1 VV + VH).
        encoder_weights: Pretrained weights (e.g. None or 'imagenet').
        activation: Output activation ('sigmoid' or None for raw logits).
    """
    if smp is None:
        raise ImportError(
            "segmentation_models_pytorch is required for build_unet_segmentation_model. "
            "Install it via: pip install segmentation-models-pytorch"
        )
    return smp.Unet(
        encoder_name=encoder_name,
        encoder_weights=encoder_weights,
        in_channels=in_channels,
        classes=1,
        activation=activation,
    )


class BCEDiceLoss(nn.Module):
    """Combined Binary Cross Entropy and Soft Dice loss for imbalanced slick masks."""

    def __init__(self, bce_weight: float = 0.5, smooth: float = 1.0):
        super().__init__()
        self.bce_weight = bce_weight
        self.smooth = smooth
        self.bce = nn.BCEWithLogitsLoss()

    def dice(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        p = torch.sigmoid(logits)
        num = 2.0 * (p * target).sum(dim=(2, 3)) + self.smooth
        den = p.sum(dim=(2, 3)) + target.sum(dim=(2, 3)) + self.smooth
        return 1.0 - (num / den).mean()

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        return self.bce_weight * self.bce(logits, target) + (1.0 - self.bce_weight) * self.dice(logits, target)


def compute_iou(logits: torch.Tensor, target: torch.Tensor, threshold: float = 0.5, eps: float = 1e-6) -> float:
    """Compute Intersection over Union (Jaccard Index) metric."""
    p = (torch.sigmoid(logits) > threshold).float()
    intersection = (p * target).sum()
    union = p.sum() + target.sum() - intersection
    return ((intersection + eps) / (union + eps)).item()


def compute_dice(logits: torch.Tensor, target: torch.Tensor, threshold: float = 0.5, eps: float = 1e-6) -> float:
    """Compute Dice similarity coefficient (F1 Score)."""
    p = (torch.sigmoid(logits) > threshold).float()
    return ((2.0 * (p * target).sum() + eps) / (p.sum() + target.sum() + eps)).item()
