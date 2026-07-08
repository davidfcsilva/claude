"""Tests for model classes."""

import torch

from src.models.cnn_model import CNNModel
from src.models.mlp_model import MLPModel
from src.models.transformer_model import TransformerModel


class TestMLPModel:
    """Test cases for MLPModel."""

    def test_instantiation(self):
        model = MLPModel(input_dim=64, num_classes=3)
        assert model.config["input_dim"] == 64
        assert model.config["num_classes"] == 3

    def test_forward_pass(self):
        model = MLPModel(input_dim=64, hidden_dims=[32, 16], num_classes=4)
        x = torch.randn(8, 64)
        out = model(x)
        assert out.shape == (8, 4)

    def test_train_eval_mode(self):
        model = MLPModel(input_dim=64)
        model.train()
        assert model.training is True
        model.eval()
        assert model.training is False

    def test_get_params_and_set_model_params(self):
        model = MLPModel(input_dim=10, num_classes=2)
        params = model.get_params()
        assert isinstance(params, dict)
        model.set_model_params(params)


class TestCNNModel:
    """Test cases for CNNModel."""

    def test_instantiation(self):
        model = CNNModel(in_channels=3, num_classes=10)
        assert model.config["in_channels"] == 3
        assert model.config["num_classes"] == 10

    def test_forward_pass(self):
        model = CNNModel(in_channels=3, num_classes=5)
        x = torch.randn(4, 3, 32, 32)
        out = model(x)
        assert out.shape[0] == 4
        assert out.shape[1] == 5

    def test_train_eval_mode(self):
        model = CNNModel()
        model.train()
        assert model.training is True
        model.eval()
        assert model.training is False


class TestTransformerModel:
    """Test cases for TransformerModel."""

    def test_instantiation(self):
        model = TransformerModel(input_dim=100, num_classes=3)
        assert model.config["input_dim"] == 100

    def test_forward_pass(self):
        model = TransformerModel(input_dim=50, hidden_dim=64, num_heads=2, num_classes=2)
        x = torch.randn(4, 16, 50)
        out = model(x)
        assert out.shape == (4, 2)

    def test_train_eval_mode(self):
        model = TransformerModel(input_dim=32)
        model.train()
        assert model.training is True
        model.eval()
        assert model.training is False

    def test_get_params_and_set_model_params(self):
        model = TransformerModel(input_dim=10, hidden_dim=32, num_heads=2)
        params = model.get_params()
        model.set_model_params(params)
