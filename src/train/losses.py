"""Loss function implementations."""

import torch
import torch.nn as nn


class CrossEntropyLoss(nn.CrossEntropyLoss):
    """CrossEntropyLoss with optional label smoothing and weight handling."""

    def __init__(self, weight=None, ignore_index=-100, reduce=True, reduction='mean', label_smoothing=0.0):
        """
        Initialize cross entropy loss.

        Args:
            weight: Optional weights per class
            ignore_index: Label to ignore
            reduce: Whether to reduce loss
            reduction: 'mean', 'sum', 'none'
            label_smoothing: Label smoothing factor (0-1)
        """
        super().__init__(weight=weight, ignore_index=ignore_index)
        self.label_smoothing = label_smoothing

    def forward(self, inputs, targets):
        """Apply loss."""
        if self.label_smoothing > 0:
            # Apply label smoothing
            smooth_loss = self._smoothed_loss(inputs, targets)
        else:
            smooth_loss = super().forward(inputs, targets)

        return smooth_loss


class FocalLoss(nn.Module):
    """Focal Loss for imbalanced datasets."""

    def __init__(self, gamma: float = 2.0, alpha: float = None, reduction: str = 'mean'):
        """
        Initialize Focal Loss.

        Args:
            gamma: Focusing parameter
            alpha: Class balance weights (optional)
            reduction: 'mean', 'sum', 'none'
        """
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha
        self.reduction = reduction

    def forward(self, inputs, targets):
        """
        Apply focal loss.

        Args:
            inputs: logits of shape (batch_size, num_classes)
            targets: targets of shape (batch_size,)

        Returns:
            loss value
        """
        ce_loss = nn.functional.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss

        if self.alpha is not None:
            # Apply alpha weights
            bce = ce_loss.unsqueeze(1)
            focal_loss = (self.alpha.float() * bce * 2 * pt +
                         (1 - self.alpha) * bce * (1 - pt)).squeeze(1)
            focal_loss = (1 - pt) ** self.gamma * focal_loss

        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        return focal_loss


class LabelSmoothedCrossEntropyLoss(nn.Module):
    """Label-smoothed cross entropy loss."""

    def __init__(self, num_classes: int, smoothing: float = 0.1, reduction: str = 'mean'):
        """
        Initialize label-smoothed cross entropy loss.

        Args:
            num_classes: Number of classes
            smoothing: Smoothing factor
            reduction: 'mean', 'sum', 'none'
        """
        super().__init__()
        self.num_classes = num_classes
        self.smoothing = smoothing
        self.reduction = reduction

    def forward(self, inputs, targets):
        """
        Apply label-smoothed cross entropy loss.

        Args:
            inputs: logits of shape (batch_size, num_classes)
            targets: targets of shape (batch_size,)

        Returns:
            loss value
        """
        assert inputs.dim() == 2
        assert targets.dim() == 1

        clog_softmax = nn.functional.log_softmax(inputs, dim=-1)
        nll_loss = -clog_softmax.gather(1, targets.unsqueeze(1))
        smooth_loss = -clog_softmax.mean(dim=1)

        loss = (1 - self.smoothing) * nll_loss + self.smoothing * smooth_loss

        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        return loss


class BCEWithLogitsLoss(nn.BCEWithLogitsLoss):
    """BCEWithLogitsLoss with optional positive/negative weight balancing."""

    def __init__(self, pos_weight=None, reduction='mean'):
        """
        Initialize binary cross entropy loss.

        Args:
            pos_weight: Weight for positive class (useful for imbalanced data)
            reduction: 'mean', 'sum', 'none'
        """
        super().__init__(pos_weight=pos_weight, reduction='none')
        self.reduction = reduction

    def forward(self, inputs, targets):
        """Apply loss."""
        loss = super().forward(inputs, targets)

        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        return loss


class MSELoss(nn.MSELoss):
    """Mean Squared Error loss."""

    def forward(self, inputs, targets):
        """Apply loss."""
        return super().forward(inputs, targets)


class MAELoss(nn.Module):
    """Mean Absolute Error loss."""

    def __init__(self, reduction: str = 'mean'):
        """
        Initialize MAE loss.

        Args:
            reduction: 'mean', 'sum', 'none'
        """
        super().__init__()
        self.reduction = reduction

    def forward(self, inputs, targets):
        """Apply loss."""
        loss = torch.abs(inputs - targets)

        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        return loss


class HingeLoss(nn.Module):
    """Hinge loss for SVM."""

    def forward(self, inputs, targets):
        """
        Apply hinge loss.

        Args:
            inputs: logits
            targets: labels in {-1, 1}

        Returns:
            hinge loss
        """
        targets = targets.float()
        loss = torch.relu(1 - targets * inputs)
        return loss.mean() if inputs.dim() > 1 else loss
