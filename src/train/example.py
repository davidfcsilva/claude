"""Example usage of the train package."""

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from torch.optim import AdamW

from train import (
    Trainer,
    EarlyStopping,
    ModelCheckpoint,
    ProgressLogger,
    MetricTracker,
    accuracy,
    get_default_loader,
    get_tensor_dataset,
)


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
    dataset = TensorDataset(x, y)
    dataloader = get_default_loader(dataset, batch_size=32, shuffle=True)

    # Create model
    model = SimpleModel(input_size=100, hidden_size=64, num_classes=2)

    # Create metric tracker
    tracker = MetricTracker()
    tracker.add_metric('accuracy', AccuracyMetric())
    tracker.add_metric('loss', LossMetric())

    # Create trainer
    trainer = Trainer(
        model=model,
        optimizer=AdamW(model.parameters(), lr=0.001),
        criterion=torch.nn.CrossEntropyLoss(),
        train_dataloader=dataloader,
        metrics=tracker,
    )

    # Create callbacks
    early_stopping = EarlyStopping(patience=5, monitor='accuracy')
    checkpoint = ModelCheckpoint(monitor='accuracy', save_best=True, save_last=True)
    progress_logger = ProgressLogger()

    # Train
    trainer.fit(
        epochs=10,
        callbacks=[early_stopping, checkpoint, progress_logger],
    )

    # Evaluate
    test_x = torch.randn(100, 100)
    test_y = torch.randint(0, 2, (100,))
    test_dataset = TensorDataset(test_x, test_y)
    test_loader = get_default_loader(test_dataset, batch_size=32, shuffle=False)

    predictions = model(test_loader.dataset.x).detach().cpu()
    labels = test_loader.dataset.y

    current_metrics = tracker.compute(labels, predictions)
    print(f"Test accuracy: {current_metrics['accuracy']:.4f}")


if __name__ == '__main__':
    main()
