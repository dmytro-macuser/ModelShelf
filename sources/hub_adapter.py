"""
ModelShelf Hub Adapter Interface
Abstract interface for model repository sources.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ModelFile:
    """Represents a file within a model repository."""
    filename: str
    size: int  # bytes
    url: str
    sha256: Optional[str] = None
    is_gguf: bool = False
    quantisation: Optional[str] = None  # e.g., "Q4_K_M", "Q8_0"


@dataclass
class ModelInfo:
    """Represents a model from a hub."""
    id: str  # e.g., "TheBloke/Llama-2-7B-GGUF"
    name: str
    author: str
    description: Optional[str] = None
    tags: List[str] = None
    licence: Optional[str] = None
    downloads: int = 0
    likes: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    has_gguf: bool = False
    total_size: int = 0  # Total size in bytes
    files: List[ModelFile] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.files is None:
            self.files = []


@dataclass
class SearchResult:
    """Search result with pagination."""
    models: List[ModelInfo]
    total_count: int
    page: int
    page_size: int
    has_next: bool


class HubAdapter(ABC):
    """Abstract base class for hub adapters."""
    
    @abstractmethod
    async def search_models(
        self,
        query: str = "",
        page: int = 0,
        page_size: int = 20,
        has_gguf: bool = False,
        sort_by: str = "downloads",
        tags: Optional[List[str]] = None
    ) -> SearchResult:
        """
        Search for models.
        
        Args:
            query: Search query text
            page: Page number (0-indexed)
            page_size: Number of results per page
            has_gguf: Filter for models with GGUF files
            sort_by: Sort criterion (downloads, likes, trending, recent)
            tags: Filter by tags
        
        Returns:
            SearchResult with models and pagination info
        """
        pass
    
    @abstractmethod
    async def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            ModelInfo or None if not found
        """
        pass
    
    @abstractmethod
    async def list_model_files(self, model_id: str) -> List[ModelFile]:
        """
        List all files in a model repository.
        
        Args:
            model_id: Model identifier
        
        Returns:
            List of ModelFile objects
        """
        pass
    
    @abstractmethod
    def get_download_url(self, model_id: str, filename: str) -> str:
        """
        Get direct download URL for a file.
        
        Args:
            model_id: Model identifier
            filename: File name
        
        Returns:
            Download URL
        """
        pass
