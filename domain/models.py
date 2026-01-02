"""
ModelShelf Domain Models
Core business entities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class DownloadState(Enum):
    """Download states."""
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SearchFilter:
    """Search filter configuration."""
    query: str = ""
    has_gguf: bool = False
    sort_by: str = "downloads"  # downloads, likes, trending, recent
    tags: List[str] = field(default_factory=list)
    min_size: Optional[int] = None  # bytes
    max_size: Optional[int] = None  # bytes
    page: int = 0
    page_size: int = 20


def format_size(bytes: int) -> str:
    """
    Format bytes to human-readable size.
    
    Args:
        bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} PB"


def parse_size(size_str: str) -> Optional[int]:
    """
    Parse human-readable size to bytes.
    
    Args:
        size_str: Size string (e.g., "1.5GB", "500MB")
    
    Returns:
        Size in bytes or None if invalid
    """
    import re
    
    match = re.match(r'([0-9.]+)\s*([KMGT]?B)', size_str.upper())
    if not match:
        return None
    
    value = float(match.group(1))
    unit = match.group(2)
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    
    return int(value * multipliers.get(unit, 1))
