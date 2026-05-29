"""Data utilities for loading and preprocessing datasets."""

import torch
from torch.utils.data import DataLoader, Dataset, TensorDataset, Dataset
from typing import Dict, Any, Optional


def get_default_loader(
    dataset: Dataset,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 0,
    pin_memory: bool = False,
    persistent_workers: bool = False,
) -> DataLoader:
    """
    Create a default DataLoader.

    Args:
        dataset: Dataset to create loader for
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Num workers
        pin_memory: Pin memory flag
        persistent_workers: Keep workers alive

    Returns:
        DataLoader
    """
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
    )


def get_tensor_dataset(
    tensors: Dict[str, torch.Tensor],
    drop_last: bool = False,
) -> Dataset:
    """
    Create a dataset from tensors.

    Args:
        tensors: Dictionary of tensors (keys will be columns)
        drop_last: Whether to drop last batch

    Returns:
        TensorDataset
    """
    return TensorDataset(*tensors.values())


def get_dataset_from_csv(
    path: str,
    columns: Optional[list] = None,
    transform: Optional[callable] = None,
    **kwargs,
) -> Dataset:
    """
    Create dataset from CSV file.

    Args:
        path: Path to CSV file
        columns: Columns to load (all if None)
        transform: Transform to apply
        **kwargs: Additional args for CSV loading

    Returns:
        Dataset
    """
    import pandas as pd
    from torch.utils.data import Dataset

    df = pd.read_csv(path)

    if columns is not None:
        df = df[columns]

    return Dataset.from_pandas(df, transform=transform, **kwargs)


def get_collate_fn(
    use_dict: bool = True,
    padding_value: float = 0.0,
) -> callable:
    """
    Create collate function for DataLoaders.

    Args:
        use_dict: Whether to use dictionary collation
        padding_value: Padding value for sequences

    Returns:
        Collate function
    """
    if use_dict:
        return lambda batch: {
            k: torch.stack([b[k] for b in batch], dim=0)
            for k in batch[0]
        } if isinstance(batch[0], dict) else {
            list(batch[0].keys())[0]: torch.stack([b[0] for b in batch], dim=0)
        }
    return torch.utils.data.default_collate


def get_batch(
    dataloader: DataLoader,
) -> Dict[str, torch.Tensor]:
    """
    Get next batch from dataloader.

    Args:
        dataloader: DataLoader

    Returns:
        Batch data
    """
    for batch in dataloader:
        if isinstance(batch, dict):
            yield batch
        else:
            yield {'x': batch}
    return {}
