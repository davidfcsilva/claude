"""Main training script."""

import argparse
import yaml
from src.models.base_model import BaseModel
from src.data.base_dataset import BaseDataset
from src.training.base_trainer import BaseTrainer


def load_config(path: str) -> dict:
    """Load configuration from YAML file."""
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def train(config_path: str) -> None:
    """Run training pipeline."""
    config = load_config(config_path)

    # Initialize model
    model = BaseModel(config.get('model_config', {}))

    # Initialize datasets
    train_dataset = BaseDataset(config.get('train_dataset_config', {}))

    # Initialize trainer
    trainer = BaseTrainer(
        model=model,
        dataset=train_dataset,
        config=config.get('training', {})
    )

    # Train
    for epoch in range(config.get('epochs', 10)):
        results = trainer.train_epoch()
        print(f"Epoch {epoch}: {results}")

    print("Training complete!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ML Training Script')
    parser.add_argument('--config', type=str, required=True, help='Path to config file')
    args = parser.parse_args()

    train(args.config)
