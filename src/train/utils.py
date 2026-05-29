"""Utility functions."""

import os
import hashlib
from typing import Dict, Any, Optional, List


def setup_device(
    device_name: Optional[str] = None,
) -> torch.device:
    """
    Setup device for training.

    Args:
        device_name: Device name ('cuda', 'cpu', None for auto)

    Returns:
        torch.device
    """
    import torch

    if device_name is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(device_name)

    return device


def save_dict(
    path: str,
    data: Dict[str, Any],
    protocol: int = 2,
    **kwargs,
):
    """
    Save dictionary to JSON.

    Args:
        path: Path to save
        data: Dict to save
        protocol: JSON protocol
        **kwargs: Additional args
    """
    import json
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, protocol=protocol, **kwargs)


def load_dict(path: str, **kwargs) -> Dict[str, Any]:
    """
    Load dictionary from JSON.

    Args:
        path: Path to load
        **kwargs: Additional args

    Returns:
        Dict
    """
    import json
    with open(path, 'r', encoding='utf-8', **kwargs) as f:
        return json.load(f)


def get_rank(is_distributed: bool = False) -> int:
    """
    Get rank for distributed training.

    Args:
        is_distributed: Whether training is distributed

    Returns:
        Rank (0 if not distributed)
    """
    if not is_distributed:
        return 0

    import torch.distributed as dist
    return dist.get_rank()


def is_master(is_distributed: bool = False) -> bool:
    """
    Check if on master process.

    Args:
        is_distributed: Whether training is distributed

    Returns:
        True if master
    """
    if not is_distributed:
        return True

    import torch.distributed as dist
    return dist.get_rank() == 0


def hash_name(name: str) -> str:
    """
    Hash a name for distributed training.

    Args:
        name: Name to hash

    Returns:
        Hashed name
    """
    return hashlib.md5(name.encode()).hexdigest()


def get_logger(
    log_dir: str = 'logs',
    name: str = 'train',
    **kwargs,
):
    """
    Get a logger for distributed training.

    Args:
        log_dir: Log directory
        name: Logger name
        **kwargs: Additional args

    Returns:
        Logger
    """
    import logging
    log_path = os.path.join(log_dir, f'{name}.log')
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
