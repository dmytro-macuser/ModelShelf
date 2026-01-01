"""
ModelShelf Domain Models
Core entities for models, files, and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class ModelFileType(Enum):
    """Types of model files."""
    GGUF = "gguf"
    SAFETENSORS = "safetensors"
    PYTORCH = "pytorch"
    ONNX = "onnx"
    OTHER = "other"


@dataclass
class ModelFile:
    """
    Represents a single file within a model repository.
    """
    filename: str
    size: int  # bytes
    url: Optional[str] = None
    sha256: Optional[str] = None
    
    @property
    def file_type(self) -> ModelFileType:
        """Detect file type from extension."""
        lower_name = self.filename.lower()
        
        if lower_name.endswith('.gguf'):
            return ModelFileType.GGUF
        elif lower_name.endswith('.safetensors'):
            return ModelFileType.SAFETENSORS
        elif lower_name.endswith(('.bin', '.pt', '.pth')):
            return ModelFileType.PYTORCH
        elif lower_name.endswith('.onnx'):
            return ModelFileType.ONNX
        else:
            return ModelFileType.OTHER
    
    @property
    def is_gguf(self) -> bool:
        """Check if this is a GGUF file."""
        return self.file_type == ModelFileType.GGUF
    
    @property
    def size_mb(self) -> float:
        """Get size in megabytes."""
        return self.size / (1024 * 1024)
    
    @property
    def size_gb(self) -> float:
        """Get size in gigabytes."""
        return self.size / (1024 * 1024 * 1024)
    
    @property
    def size_human(self) -> str:
        """Get human-readable size string."""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size_mb:.1f} MB"
        else:
            return f"{self.size_gb:.2f} GB"
    
    def get_quantisation_hint(self) -> Optional[str]:
        """
        Extract quantisation hint from filename (e.g., Q4_K_M, Q5_0).
        Returns None if no quantisation pattern detected.
        """
        import re
        
        # Common GGUF quantisation patterns
        patterns = [
            r'[Qq](\d+)[_-]([KkMmSs])[_-]?([LlMmSsXxLl])?',  # Q4_K_M, Q5_K_S, etc.
            r'[Qq](\d+)[_-](\d+)',  # Q4_0, Q5_1, etc.
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.filename)
            if match:
                return match.group(0).upper()
        
        return None


@dataclass
class Model:
    """
    Represents a model from a hub/source.
    """
    id: str  # e.g., "TheBloke/Llama-2-7B-GGUF"
    name: str  # Display name
    author: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    licence: Optional[str] = None
    downloads: int = 0
    likes: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    files: List[ModelFile] = field(default_factory=list)
    source: str = "huggingface"  # Source identifier
    
    @property
    def has_gguf(self) -> bool:
        """Check if model has any GGUF files."""
        return any(f.is_gguf for f in self.files)
    
    @property
    def gguf_files(self) -> List[ModelFile]:
        """Get only GGUF files."""
        return [f for f in self.files if f.is_gguf]
    
    @property
    def total_size(self) -> int:
        """Get total size of all files in bytes."""
        return sum(f.size for f in self.files)
    
    @property
    def total_size_gb(self) -> float:
        """Get total size in gigabytes."""
        return self.total_size / (1024 * 1024 * 1024)
    
    @property
    def gguf_count(self) -> int:
        """Count of GGUF files."""
        return len(self.gguf_files)
    
    def get_file_by_name(self, filename: str) -> Optional[ModelFile]:
        """Find a file by exact filename."""
        for f in self.files:
            if f.filename == filename:
                return f
        return None


@dataclass
class SearchFilter:
    """
    Search and filter criteria for model discovery.
    """
    query: str = ""
    has_gguf: bool = False
    min_size_gb: Optional[float] = None
    max_size_gb: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    sort_by: str = "downloads"  # downloads, likes, updated, created
    sort_order: str = "desc"  # asc, desc
    page: int = 1
    per_page: int = 20
    
    def matches(self, model: Model) -> bool:
        """
        Check if a model matches this filter.
        
        Args:
            model: Model to check
        
        Returns:
            True if model matches all filter criteria
        """
        # GGUF filter
        if self.has_gguf and not model.has_gguf:
            return False
        
        # Size filters
        if self.min_size_gb is not None and model.total_size_gb < self.min_size_gb:
            return False
        if self.max_size_gb is not None and model.total_size_gb > self.max_size_gb:
            return False
        
        # Tag filters (all tags must be present)
        if self.tags:
            model_tags_lower = [t.lower() for t in model.tags]
            for tag in self.tags:
                if tag.lower() not in model_tags_lower:
                    return False
        
        return True


@dataclass
class SearchResult:
    """
    Result container for model searches.
    """
    models: List[Model]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_previous: bool
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total_count + self.per_page - 1) // self.per_page
