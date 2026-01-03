"""
ModelShelf Application Services
High-level business operations.
"""

import logging
import asyncio
from typing import Optional, List
from pathlib import Path

from sources.hub_adapter import SearchResult, ModelInfo
from sources.huggingface_adapter import HuggingFaceAdapter
from storage.cache import get_cache
from domain.models import SearchFilter, DownloadState
from downloader.manager import DownloadManager, DownloadItem
from library.indexer import LibraryIndexer, ModelEntry, get_indexer

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for searching and browsing models.
    Coordinates between hub adapter and cache.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialise search service.
        
        Args:
            token: Optional HF API token
        """
        self.hub = HuggingFaceAdapter(token=token)
        self.cache = get_cache()
    
    async def search(
        self,
        filter: SearchFilter,
        use_cache: bool = True
    ) -> SearchResult:
        """
        Search for models with caching.
        
        Args:
            filter: Search filter configuration
            use_cache: Whether to use cached results
        
        Returns:
            SearchResult with models and pagination
        """
        try:
            # Try cache first if enabled
            if use_cache:
                cached = self.cache.get_cached_search(
                    query=filter.query,
                    has_gguf=filter.has_gguf,
                    sort_by=filter.sort_by,
                    page=filter.page,
                    page_size=filter.page_size
                )
                
                if cached:
                    logger.info(f"Cache hit for query: {filter.query}")
                    return cached
            
            # Fetch from hub
            logger.info(f"Fetching from hub: {filter.query}")
            result = await self.hub.search_models(
                query=filter.query,
                page=filter.page,
                page_size=filter.page_size,
                has_gguf=filter.has_gguf,
                sort_by=filter.sort_by,
                tags=filter.tags
            )
            
            # Cache the result
            if use_cache and result.models:
                self.cache.cache_search_result(
                    query=filter.query,
                    has_gguf=filter.has_gguf,
                    sort_by=filter.sort_by,
                    page=filter.page,
                    page_size=filter.page_size,
                    result=result
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            # Return empty result on error
            return SearchResult(
                models=[],
                total_count=0,
                page=filter.page,
                page_size=filter.page_size,
                has_next=False
            )
    
    async def get_model_details(
        self,
        model_id: str,
        use_cache: bool = True
    ) -> Optional[ModelInfo]:
        """
        Get detailed model information with files.
        
        Args:
            model_id: Model identifier
            use_cache: Whether to use cached data
        
        Returns:
            ModelInfo with files or None
        """
        try:
            # Try cache first
            if use_cache:
                cached = self.cache.get_cached_model(model_id)
                if cached and cached.files:  # Only use if files are cached
                    logger.info(f"Cache hit for model: {model_id}")
                    return cached
            
            # Fetch from hub
            logger.info(f"Fetching model details: {model_id}")
            model = await self.hub.get_model_info(model_id)
            
            if model:
                # Get file list
                files = await self.hub.list_model_files(model_id)
                model.files = files
                
                # Cache the result
                if use_cache:
                    self.cache.cache_model(model)
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to get model details for {model_id}: {e}")
            return None
    
    async def list_model_files(self, model_id: str) -> List:
        """
        List files for a model.
        
        Args:
            model_id: Model identifier
        
        Returns:
            List of ModelFile objects
        """
        try:
            return await self.hub.list_model_files(model_id)
        except Exception as e:
            logger.error(f"Failed to list files for {model_id}: {e}")
            return []
    
    def get_download_url(self, model_id: str, filename: str) -> str:
        """
        Get download URL for a file.
        
        Args:
            model_id: Model identifier
            filename: File name
        
        Returns:
            Download URL
        """
        return self.hub.get_download_url(model_id, filename)
    
    async def close(self):
        """Clean up resources."""
        await self.hub.close()


class DownloadService:
    """
    Service for managing downloads.
    """
    
    def __init__(self, manager: DownloadManager):
        self.manager = manager
    
    def add_download(self, model_id: str, filename: str, url: str, size: int) -> str:
        """Add file to download queue."""
        logger.info(f"Adding download: {model_id}/{filename}")
        return self.manager.add_download(model_id, filename, url, size)
    
    def pause_download(self, download_id: str):
        """Pause a download."""
        self.manager.pause_download(download_id)
    
    def resume_download(self, download_id: str):
        """Resume a download."""
        self.manager.resume_download(download_id)
    
    def cancel_download(self, download_id: str):
        """Cancel a download."""
        self.manager.cancel_download(download_id)
    
    def get_downloads(self) -> List[DownloadItem]:
        """Get all downloads."""
        return self.manager.get_all_items()
    
    async def close(self):
        """Cleanup."""
        await self.manager.cleanup()


class LibraryService:
    """
    Service for managing the local library.
    """
    
    def __init__(self, indexer: Optional[LibraryIndexer] = None):
        self.indexer = indexer or get_indexer()
    
    def scan_library(self, force: bool = False) -> List[ModelEntry]:
        """Scan library and return all models."""
        return self.indexer.scan(force=force)
    
    def get_all_models(self) -> List[ModelEntry]:
        """Get all indexed models."""
        return self.indexer.get_all_models()
    
    def get_model(self, model_id: str) -> Optional[ModelEntry]:
        """Get specific model."""
        return self.indexer.get_model(model_id)
    
    def get_total_size(self) -> int:
        """Get total library size in bytes."""
        return self.indexer.get_total_size()
    
    def get_model_count(self) -> int:
        """Get number of models."""
        return self.indexer.get_model_count()
    
    def delete_model(self, model_id: str) -> bool:
        """Delete a model from library."""
        return self.indexer.delete_model(model_id)
    
    def open_model_folder(self, model_id: str) -> bool:
        """Open model folder in file explorer."""
        import subprocess
        import platform
        
        entry = self.indexer.get_model(model_id)
        if not entry or not entry.path.exists():
            return False
        
        try:
            system = platform.system()
            if system == 'Windows':
                subprocess.run(['explorer', str(entry.path)])
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', str(entry.path)])
            else:  # Linux
                subprocess.run(['xdg-open', str(entry.path)])
            return True
        except Exception as e:
            logger.error(f"Failed to open folder: {e}")
            return False


class ServiceManager:
    """
    Central manager for all application services.
    """
    
    def __init__(self):
        self._search_service: Optional[SearchService] = None
        self._download_service: Optional[DownloadService] = None
        self._download_manager: Optional[DownloadManager] = None
        self._library_service: Optional[LibraryService] = None
    
    def get_search_service(self, token: Optional[str] = None) -> SearchService:
        """Get or create search service instance."""
        if self._search_service is None:
            self._search_service = SearchService(token=token)
        return self._search_service
    
    def get_download_service(self) -> DownloadService:
        """Get or create download service instance."""
        if self._download_service is None:
            if self._download_manager is None:
                self._download_manager = DownloadManager()
            self._download_service = DownloadService(self._download_manager)
        return self._download_service
    
    def get_library_service(self) -> LibraryService:
        """Get or create library service instance."""
        if self._library_service is None:
            self._library_service = LibraryService()
        return self._library_service
    
    async def close_all(self):
        """Close all services."""
        if self._search_service:
            await self._search_service.close()
        if self._download_service:
            await self._download_service.close()


# Global service manager
_service_manager: Optional[ServiceManager] = None


def get_service_manager() -> ServiceManager:
    """
    Get the global service manager instance.
    
    Returns:
        Global ServiceManager instance
    """
    global _service_manager
    if _service_manager is None:
        _service_manager = ServiceManager()
    return _service_manager
