"""Main training script."""

import argparse
import logging
import sys
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.utils.data import DataLoader
import yaml

logger = logging.getLogger(__name__)


def load_config(path: str) -> dict:
    """Load configuration from YAML file."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def resolve_device(device_str: str) -> str:
    """Resolve device string to actual device."""
    if device_str == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device_str


class SimpleTrainer:
    """Concrete trainer for demonstration and quick experiments."""

    def __init__(self, model, dataset, config):
        """Initialize trainer with model, dataset, and training config.

        Args:
            model: PyTorch model to train
            dataset: Dataset (or DataLoader) to train on
            config: Training configuration dict
        """
        self.model = model
        self.dataset = dataset
        self.config = config
        self.device = torch.device(config.get("device", "cpu"))

        # Setup optimizer once so momentum state persists across epochs
        self.optimizer = Adam(model.parameters(), lr=config.get("learning_rate", 1e-3))
        self.criterion = nn.CrossEntropyLoss()

        from src.evaluation.metrics import Accuracy, Loss
        num_classes = model.config.get("num_classes", 10) if hasattr(model, "config") else 10
        self.accuracy = Accuracy(num_classes=num_classes)
        self.loss_metric = Loss()

    def train_epoch(self) -> dict[str, float]:
        """Train for one epoch using the dataset."""
        self.accuracy.reset()
        self.model.train()
        total_loss = 0.0
        num_batches = 0

        # Support both raw Dataset and DataLoader
        if isinstance(self.dataset, DataLoader):
            dataloader = self.dataset
        else:
            batch_size = self.config.get("batch_size", 32)
            dataloader = DataLoader(
                self.dataset,
                batch_size=batch_size,
                shuffle=True,
                drop_last=False,
            )

        for batch in dataloader:
            # Handle dict batches (e.g. {"image": x, "label": y}) and tuple batches
            if isinstance(batch, dict):
                x = batch.get("image", batch.get("input", batch.get("x")))
                y = batch.get("label", batch.get("target", batch.get("y")))
            elif isinstance(batch, (list, tuple)):
                x, y = batch[0], batch[1]
            else:
                # Fallback: assume raw tensor pair from simple datasets
                x, y = batch

            x = x.to(self.device)
            y = y.to(self.device)

            self.optimizer.zero_grad()
            out = self.model(x)
            loss = self.criterion(out, y)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()
            num_batches += 1

            preds = out.argmax(dim=1).tolist()
            targets = y.tolist()
            self.accuracy.update(preds, targets)

        if num_batches > 0:
            avg_loss = total_loss / num_batches
            self.loss_metric.update(avg_loss)

        return {"loss": avg_loss if num_batches > 0 else 0.0,
                "accuracy": self.accuracy.get_value()}

    def evaluate(self, val_dataset=None) -> dict[str, float]:
        """Evaluate the model."""
        self.accuracy.reset()
        self.model.eval()
        with torch.no_grad():
            # Track accuracy during evaluation
            total_correct = 0
            total_samples = 0
            dataset = val_dataset or self.dataset
            if isinstance(dataset, DataLoader):
                dataloader = dataset
            else:
                batch_size = self.config.get("batch_size", 32)
                dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

            total_loss = 0.0
            num_batches = 0
            for batch in dataloader:
                if isinstance(batch, dict):
                    x = batch.get("image", batch.get("input", batch.get("x")))
                    y = batch.get("label", batch.get("target", batch.get("y")))
                elif isinstance(batch, (list, tuple)):
                    x, y = batch[0], batch[1]
                else:
                    x, y = batch

                x = x.to(self.device)
                y = y.to(self.device)
                out = self.model(x)
                loss = self.criterion(out, y)
                total_loss += loss.item()
                num_batches += 1

                preds = out.argmax(dim=1).tolist()
                targets = y.tolist()
                total_correct += sum(1 for p, t in zip(preds, targets) if p == t)
                total_samples += len(targets)

        return {
            "loss": total_loss / num_batches if num_batches > 0 else 0.0,
            "accuracy": total_correct / total_samples if total_samples > 0 else 0.0,
        }


def train(config_path: str) -> None:
    """Run training pipeline."""
    config = load_config(config_path)

    # Resolve device
    device = resolve_device(
        config.get("training", {}).get("device", "cpu")
    )
    logger.info("Using device: %s", device)

    # Import and instantiate model based on config
    model_type = config.get("model", {}).get("type", "mlp").lower()
    model_config = config.get("model", {}).get("config", {})

    if model_type == "mlp":
        from src.models.mlp_model import MLPModel
        model = MLPModel(**model_config)
    elif model_type == "cnn":
        from src.models.cnn_model import CNNModel
        model = CNNModel(**model_config)
    elif model_type == "transformer":
        from src.models.transformer_model import TransformerModel
        model = TransformerModel(**model_config)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    model.to(device)
    logger.info("Model initialized: %s", model.__class__.__name__)

    # Import and instantiate dataset based on config
    dataset_type = config.get("dataset", {}).get("type", "mnist").lower()
    dataset_config = config.get("dataset", {}).get("config", {})

    if dataset_type == "mnist":
        from src.data.image_datasets import MNISTDataset
        train_dataset = MNISTDataset(config=dataset_config)
    elif dataset_type == "cifar":
        from src.data.image_datasets import CIFARDataset
        train_dataset = CIFARDataset(config=dataset_config)
    elif dataset_type == "imdb":
        from src.data.text_datasets import IMDBDataset
        train_dataset = IMDBDataset(config=dataset_config)
    else:
        raise ValueError(f"Unknown dataset type: {dataset_type}")

    logger.info("Dataset initialized: %s (%d samples)",
                train_dataset.__class__.__name__, len(train_dataset))

    # Merge device into training config for the trainer
    training_config = config.get("training", {})
    training_config["device"] = device

    trainer = SimpleTrainer(
        model=model,
        dataset=train_dataset,
        config=training_config,
    )

    # Train
    epochs = config.get("epochs", 10)
    for epoch in range(epochs):
        results = trainer.train_epoch()
        logger.info("Epoch %d/%d: loss=%.4f acc=%.4f",
                    epoch + 1, epochs, results["loss"], results["accuracy"])

    eval_results = trainer.evaluate()
    logger.info("Training complete! Final - loss=%.4f acc=%.4f",
                eval_results["loss"], eval_results["accuracy"])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stdout,
    )
    parser = argparse.ArgumentParser(description='ML Training Script')
    parser.add_argument('--config', type=str, required=True, help='Path to config file')
    args = parser.parse_args()

    train(args.config)
