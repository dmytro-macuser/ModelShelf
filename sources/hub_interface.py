"""
ModelShelf Hub Interface
Abstract interface for model hub sources.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import Model, SearchFilter, SearchResult


class HubInterface(ABC):
    """
    Abstract interface for model hub sources.
    Allows for multiple hub implementations (HuggingFace, local, etc.)
    """
    
    @abstractmethod
    def search_models(self, search_filter: SearchFilter) -> SearchResult:
        """
        Search for models based on filter criteria.
        
        Args:
            search_filter: Search and filter parameters
        
        Returns:
            SearchResult with matching models
        """
        pass
    
    @abstractmethod
    def get_model_details(self, model_id: str) -> Optional[Model]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_id: Unique model identifier
        
        Returns:
            Model object with full details, or None if not found
        """
        pass
    
    @abstractmethod
    def get_model_files(self, model_id: str) -> List:
        """
        Get list of files for a model.
        
        Args:
            model_id: Unique model identifier
        
        Returns:
            List of ModelFile objects
        """
        pass
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """
        Get the name of this hub source.
        
        Returns:
            Source name (e.g., "huggingface", "local")
        """
        pass
