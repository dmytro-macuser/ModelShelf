"""
ModelShelf Filter Utilities
Helper functions for filtering and sorting models.
"""

from typing import List, Callable
from domain.models import Model, SearchFilter


def sort_models(models: List[Model], sort_by: str, order: str = "desc") -> List[Model]:
    """
    Sort a list of models by specified criteria.
    
    Args:
        models: List of models to sort
        sort_by: Sort field (downloads, likes, updated, created, size)
        order: Sort order (asc or desc)
    
    Returns:
        Sorted list of models
    """
    reverse = (order.lower() == "desc")
    
    # Define sort key functions
    sort_keys: dict[str, Callable[[Model], any]] = {
        "downloads": lambda m: m.downloads,
        "likes": lambda m: m.likes,
        "updated": lambda m: m.updated_at if m.updated_at else 0,
        "created": lambda m: m.created_at if m.created_at else 0,
        "size": lambda m: m.total_size,
        "name": lambda m: m.name.lower(),
    }
    
    key_func = sort_keys.get(sort_by.lower(), sort_keys["downloads"])
    
    try:
        return sorted(models, key=key_func, reverse=reverse)
    except Exception:
        # Fallback if sorting fails
        return models


def filter_models(models: List[Model], search_filter: SearchFilter) -> List[Model]:
    """
    Filter a list of models based on search criteria.
    
    Args:
        models: List of models to filter
        search_filter: Filter criteria
    
    Returns:
        Filtered list of models
    """
    filtered = [m for m in models if search_filter.matches(m)]
    return sort_models(filtered, search_filter.sort_by, search_filter.sort_order)


def detect_gguf_quantisation_types(models: List[Model]) -> List[str]:
    """
    Extract all unique quantisation types from GGUF files.
    
    Args:
        models: List of models to analyse
    
    Returns:
        Sorted list of unique quantisation types found
    """
    quant_types = set()
    
    for model in models:
        for file in model.gguf_files:
            quant = file.get_quantisation_hint()
            if quant:
                quant_types.add(quant)
    
    return sorted(quant_types)
