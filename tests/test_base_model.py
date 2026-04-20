"""Tests for base model."""

import pytest
from src.models.base_model import BaseModel


class TestBaseModel:
    """Test cases for BaseModel."""

    def test_instantiation(self):
        """Test model instantiation."""
        model = BaseModel()
        assert model.config == {}

    def test_init_with_config(self):
        """Test model initialization with config."""
        config = {"lr": 0.01}
        model = BaseModel(config=config)
        assert model.config == config
