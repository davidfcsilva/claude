"""Example usage of the train package."""

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import AdamW

from .trainer import Trainer
from .metrics import AccuracyMetric, LossMetric
from .callbacks import EarlyStopping, ModelCheckpoint, ProgressLogger


class SimpleModel(nn.Module):
    """Simple model for demonstration."""

    def __init__(self, input_size: int = 100, hidden_size: int = 64, num_classes: int = 2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size, num_classes),
        )

    def forward(self, x):
        return self.net(x)


def main():
    """Main example function."""
    # Create sample data
    torch.manual_seed(42)
    x = torch.randn(1000, 100)
    y = torch.randint(0, 2, (1000,))

    # Create dataset and dataloader
    train_dataset = TensorDataset(x, y)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    test_x = torch.randn(100, 100)
    test_y = torch.randint(0, 2, (100,))
    test_dataset = TensorDataset(test_x, test_y)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    # Create model
    model = SimpleModel(input_size=100, hidden_size=64, num_classes=2)

    # Create trainer with callbacks
    early_stopping = EarlyStopping(patience=5, mode='max')
    checkpoint = ModelCheckpoint(save_path='./checkpoints', monitor='accuracy', mode='max')
    progress_logger = ProgressLogger()

    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=test_loader,
        criterion=torch.nn.CrossEntropyLoss(),
        callbacks=[early_stopping, checkpoint, progress_logger],
    )

    # Train
    history = trainer.train(epochs=10)

    print(f"Training complete!")
    print(f"Final training loss: {history['loss'][-1]:.4f}")
    print(f"Final accuracy: {history['accuracy'][-1]:.4f}")


if __name__ == '__main__':
    main()