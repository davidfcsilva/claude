"""Configuration management for training."""

import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Optional


@dataclass
class ModelConfig:
    """Model configuration."""
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    momentum: float = 0.9
    batch_size: int = 32
    num_epochs: int = 100
    patience: int = 10  # Early stopping patience
    dropout: float = 0.1
    weight_init: str = 'kaiming_uniform'
    bias: bool = True


@dataclass
class OptimizerConfig:
    """Optimizer configuration."""
    type: str = 'Adam'
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    betas: tuple = (0.9, 0.999)
    eps: float = 1e-8


@dataclass
class TrainingConfig:
    """Training configuration."""
    batch_size: int = 32
    num_epochs: int = 100
    patience: int = 10
    learning_rate: float = 0.001
    weight_decay: float = 0.0001
    momentum: float = 0.9
    dropout: float = 0.1


class Config:
    """Configuration manager."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to config file
        """
        self.config_path = config_path
        self.model = ModelConfig()
        self.optimizer = OptimizerConfig()
        self.training = TrainingConfig()
        self.device = None
        self.num_workers = 0
        self.pin_memory = False
        self.enable_progress_bar = False

    def load(self, path: Optional[str] = None):
        """
        Load configuration from file.

        Args:
            path: Path to config file
        """
        path = path or self.config_path
        if path is not None:
            with open(path, 'r') as f:
                data = json.load(f)
            self._update_from_dict(data)

    def _update_from_dict(self, data: dict):
        """
        Update config from dictionary.

        Args:
            data: Config data
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            elif key == 'model':
                for k, v in value.items():
                    if hasattr(self.model, k):
                        setattr(self.model, k, v)
            elif key == 'optimizer':
                for k, v in value.items():
                    if hasattr(self.optimizer, k):
                        setattr(self.optimizer, k, v)
            elif key == 'training':
                for k, v in value.items():
                    if hasattr(self.training, k):
                        setattr(self.training, k, v)
            elif key == 'device':
                self.device = v
            elif key == 'num_workers':
                self.num_workers = v
            elif key == 'pin_memory':
                self.pin_memory = v
            elif key == 'enable_progress_bar':
                self.enable_progress_bar = v

    def to_dict(self) -> dict:
        """
        Convert config to dictionary.

        Returns:
            Config as dictionary
        """
        return {
            'model': asdict(self.model),
            'optimizer': asdict(self.optimizer),
            'training': asdict(self.training),
            'device': self.device,
            'num_workers': self.num_workers,
            'pin_memory': self.pin_memory,
            'enable_progress_bar': self.enable_progress_bar,
        }

    def save(self, path: Optional[str] = None):
        """
        Save configuration to file.

        Args:
            path: Path to save config
        """
        path = path or self.config_path
        if path is not None:
            with open(path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        """
        Create config from dictionary.

        Args:
            data: Config dictionary

        Returns:
            Config instance
        """
        config = cls()
        config._update_from_dict(data)
        return config

    def merge(self, other: 'Config'):
        """
        Merge another config into this one.

        Args:
            other: Other config to merge
        """
        if other.model:
            for k, v in other.model.__dict__.items():
                if hasattr(self.model, k):
                    setattr(self.model, k, v)
        if other.optimizer:
            for k, v in other.optimizer.__dict__.items():
                if hasattr(self.optimizer, k):
                    setattr(self.optimizer, k, v)
        if other.training:
            for k, v in other.training.__dict__.items():
                if hasattr(self.training, k):
                    setattr(self.training, k, v)

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            Config string
        """
        return f"Config(model={self.model}, optimizer={self.optimizer}, training={self.training})"
