"""
ModelShelf Discover Controller
Bridge between QML UI and backend services.
"""

import logging
from typing import List, Optional
from PySide6.QtCore import QObject, Slot, Signal, Property, QThread

from sources.huggingface_hub import HuggingFaceHub
from storage.cache import CacheManager
from storage.settings import get_settings
from domain.models import Model, SearchFilter, SearchResult

logger = logging.getLogger(__name__)


class SearchWorker(QThread):
    """
    Background thread worker for model searches.
    Keeps UI responsive during API calls.
    """
    
    search_completed = Signal(object)  # SearchResult
    search_failed = Signal(str)  # Error message
    
    def __init__(self, hub: HuggingFaceHub, search_filter: SearchFilter):
        super().__init__()
        self.hub = hub
        self.search_filter = search_filter
    
    def run(self):
        """Execute search in background thread."""
        try:
            logger.info(f"Background search started: {self.search_filter.query}")
            result = self.hub.search_models(self.search_filter)
            self.search_completed.emit(result)
        except Exception as e:
            logger.error(f"Background search failed: {e}", exc_info=True)
            self.search_failed.emit(str(e))


class DiscoverController(QObject):
    """
    Controller for the Discover view.
    Handles search, filtering, and model details.
    """
    
    # Signals for UI updates
    searchStarted = Signal()
    searchCompleted = Signal(int)  # result count
    searchFailed = Signal(str)  # error message
    modelDetailsLoaded = Signal(object)  # Model
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.settings = get_settings()
        self.cache = CacheManager()
        
        # Initialize hub (no token for now)
        try:
            self.hub = HuggingFaceHub(token=None)
            logger.info("Discover controller initialized")
        except Exception as e:
            logger.error(f"Failed to initialize hub: {e}")
            self.hub = None
        
        self._current_results: Optional[SearchResult] = None
        self._current_filter = SearchFilter()
        self._search_worker: Optional[SearchWorker] = None
    
    @Slot(str, bool, str, int)
    def search(self, query: str, gguf_only: bool, sort_by: str, page: int = 1):
        """
        Perform a model search.
        
        Args:
            query: Search query text
            gguf_only: Filter for GGUF files only
            sort_by: Sort field name
            page: Page number
        """
        if self.hub is None:
            self.searchFailed.emit("Hub not initialized")
            return
        
        # Map UI sort names to domain
        sort_mapping = {
            "Downloads": "downloads",
            "Likes": "likes",
            "Recently updated": "updated",
            "Recently created": "created"
        }
        sort_field = sort_mapping.get(sort_by, "downloads")
        
        # Build filter
        self._current_filter = SearchFilter(
            query=query.strip(),
            has_gguf=gguf_only,
            sort_by=sort_field,
            sort_order="desc",
            page=page,
            per_page=20
        )
        
        logger.info(f"Starting search: '{query}', GGUF={gguf_only}, sort={sort_field}, page={page}")
        self.searchStarted.emit()
        
        # Cancel any existing search
        if self._search_worker and self._search_worker.isRunning():
            self._search_worker.terminate()
            self._search_worker.wait()
        
        # Start new search in background
        self._search_worker = SearchWorker(self.hub, self._current_filter)
        self._search_worker.search_completed.connect(self._on_search_completed)
        self._search_worker.search_failed.connect(self._on_search_failed)
        self._search_worker.start()
    
    def _on_search_completed(self, result: SearchResult):
        """Handle search completion."""
        self._current_results = result
        
        # Cache results
        self.cache.cache_models_batch(result.models)
        
        logger.info(f"Search completed: {len(result.models)} results")
        self.searchCompleted.emit(len(result.models))
    
    def _on_search_failed(self, error: str):
        """Handle search failure."""
        logger.error(f"Search failed: {error}")
        self.searchFailed.emit(error)
    
    @Slot(str, result=object)
    def get_model_details(self, model_id: str) -> Optional[dict]:
        """
        Get detailed information about a model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            Model data as dictionary for QML
        """
        if self.hub is None:
            return None
        
        logger.info(f"Loading details for: {model_id}")
        
        # Try cache first
        model = self.cache.get_cached_model(model_id)
        
        # Fetch from hub if not cached
        if model is None:
            model = self.hub.get_model_details(model_id)
            if model:
                self.cache.cache_model(model)
        
        if model is None:
            return None
        
        # Convert to dict for QML
        return self._model_to_dict(model)
    
    @Slot(result=list)
    def get_current_results(self) -> List[dict]:
        """
        Get current search results.
        
        Returns:
            List of model dictionaries for QML
        """
        if self._current_results is None:
            return []
        
        return [self._model_to_dict(m) for m in self._current_results.models]
    
    @Slot(result=dict)
    def get_pagination_info(self) -> dict:
        """
        Get pagination information.
        
        Returns:
            Dictionary with pagination data
        """
        if self._current_results is None:
            return {
                "page": 1,
                "total_pages": 1,
                "has_next": False,
                "has_previous": False,
                "total_count": 0
            }
        
        return {
            "page": self._current_results.page,
            "total_pages": self._current_results.total_pages,
            "has_next": self._current_results.has_next,
            "has_previous": self._current_results.has_previous,
            "total_count": self._current_results.total_count
        }
    
    def _model_to_dict(self, model: Model) -> dict:
        """
        Convert Model to dictionary for QML.
        
        Args:
            model: Model object
        
        Returns:
            Dictionary representation
        """
        return {
            "id": model.id,
            "name": model.name,
            "author": model.author or "Unknown",
            "description": model.description or "",
            "tags": model.tags,
            "licence": model.licence or "Not specified",
            "downloads": self._format_number(model.downloads),
            "likes": self._format_number(model.likes),
            "ggufCount": model.gguf_count,
            "fileCount": len(model.files),
            "totalSize": f"{model.total_size_gb:.2f} GB",
            "hasGGUF": model.has_gguf,
            "files": [
                {
                    "filename": f.filename,
                    "size": f.size_human,
                    "isGGUF": f.is_gguf,
                    "quantisation": f.get_quantisation_hint() or "",
                    "url": f.url or ""
                }
                for f in model.files
            ]
        }
    
    def _format_number(self, num: int) -> str:
        """
        Format large numbers for display.
        
        Args:
            num: Number to format
        
        Returns:
            Formatted string (e.g., "1.2M", "345K")
        """
        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        else:
            return str(num)
