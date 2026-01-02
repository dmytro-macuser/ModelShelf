"""
ModelShelf Cache Manager
High-level caching operations.
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from sources.hub_adapter import ModelInfo, ModelFile, SearchResult
from .database import get_database, CachedModel, CachedFile, SearchCache

logger = logging.getLogger(__name__)


class CacheManager:
    """Manager for cached search results and model metadata."""
    
    # Cache expiry times
    SEARCH_CACHE_HOURS = 6
    MODEL_CACHE_HOURS = 24
    
    def __init__(self):
        self.db = get_database()
    
    def cache_search_result(
        self,
        query: str,
        has_gguf: bool,
        sort_by: str,
        page: int,
        page_size: int,
        result: SearchResult
    ) -> None:
        """
        Cache a search result.
        
        Args:
            query: Search query
            has_gguf: GGUF filter
            sort_by: Sort option
            page: Page number
            page_size: Page size
            result: SearchResult to cache
        """
        try:
            query_hash = self._hash_query(query, has_gguf, sort_by, page, page_size)
            result_ids = [model.id for model in result.models]
            
            session = self.db.get_session()
            try:
                # Check if exists
                cached = session.query(SearchCache).filter_by(query_hash=query_hash).first()
                
                if cached:
                    # Update existing
                    cached.result_ids = json.dumps(result_ids)
                    cached.total_count = result.total_count
                    cached.has_next = result.has_next
                    cached.cached_at = datetime.utcnow()
                else:
                    # Create new
                    cached = SearchCache(
                        query_hash=query_hash,
                        query=query,
                        has_gguf=has_gguf,
                        sort_by=sort_by,
                        page=page,
                        page_size=page_size,
                        result_ids=json.dumps(result_ids),
                        total_count=result.total_count,
                        has_next=result.has_next
                    )
                    session.add(cached)
                
                # Cache individual models
                for model in result.models:
                    self._cache_model(session, model)
                
                session.commit()
                logger.debug(f"Cached search result: {query_hash}")
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to cache search result: {e}")
    
    def get_cached_search(
        self,
        query: str,
        has_gguf: bool,
        sort_by: str,
        page: int,
        page_size: int
    ) -> Optional[SearchResult]:
        """
        Retrieve cached search result if not expired.
        
        Returns:
            SearchResult or None if not cached/expired
        """
        try:
            query_hash = self._hash_query(query, has_gguf, sort_by, page, page_size)
            session = self.db.get_session()
            
            try:
                cached = session.query(SearchCache).filter_by(query_hash=query_hash).first()
                
                if not cached:
                    return None
                
                # Check expiry
                expiry = datetime.utcnow() - timedelta(hours=self.SEARCH_CACHE_HOURS)
                if cached.cached_at < expiry:
                    logger.debug(f"Search cache expired: {query_hash}")
                    return None
                
                # Load models
                result_ids = json.loads(cached.result_ids)
                models = []
                
                for model_id in result_ids:
                    model = self._get_cached_model(session, model_id)
                    if model:
                        models.append(model)
                
                if not models:
                    return None
                
                return SearchResult(
                    models=models,
                    total_count=cached.total_count,
                    page=cached.page,
                    page_size=cached.page_size,
                    has_next=cached.has_next
                )
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to retrieve cached search: {e}")
            return None
    
    def cache_model(self, model: ModelInfo) -> None:
        """
        Cache a single model.
        
        Args:
            model: ModelInfo to cache
        """
        session = self.db.get_session()
        try:
            self._cache_model(session, model)
            session.commit()
        finally:
            session.close()
    
    def get_cached_model(self, model_id: str) -> Optional[ModelInfo]:
        """
        Retrieve cached model if not expired.
        
        Args:
            model_id: Model identifier
        
        Returns:
            ModelInfo or None if not cached/expired
        """
        session = self.db.get_session()
        try:
            return self._get_cached_model(session, model_id)
        finally:
            session.close()
    
    def clear_expired_cache(self) -> None:
        """
        Remove expired cache entries.
        """
        try:
            session = self.db.get_session()
            try:
                search_expiry = datetime.utcnow() - timedelta(hours=self.SEARCH_CACHE_HOURS)
                model_expiry = datetime.utcnow() - timedelta(hours=self.MODEL_CACHE_HOURS)
                
                # Delete expired searches
                session.query(SearchCache).filter(
                    SearchCache.cached_at < search_expiry
                ).delete()
                
                # Delete expired models
                session.query(CachedModel).filter(
                    CachedModel.cached_at < model_expiry
                ).delete()
                
                session.commit()
                logger.info("Expired cache cleared")
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}")
    
    def _hash_query(self, query: str, has_gguf: bool, sort_by: str, page: int, page_size: int) -> str:
        """Generate hash for query parameters."""
        params = f"{query}|{has_gguf}|{sort_by}|{page}|{page_size}"
        return hashlib.md5(params.encode()).hexdigest()
    
    def _cache_model(self, session, model: ModelInfo) -> None:
        """Cache a model in the session."""
        cached = session.query(CachedModel).filter_by(id=model.id).first()
        
        if cached:
            # Update existing
            cached.name = model.name
            cached.author = model.author
            cached.description = model.description
            cached.tags = json.dumps(model.tags)
            cached.licence = model.licence
            cached.downloads = model.downloads
            cached.likes = model.likes
            cached.created_at = model.created_at
            cached.updated_at = model.updated_at
            cached.has_gguf = model.has_gguf
            cached.total_size = model.total_size
            cached.cached_at = datetime.utcnow()
            
            # Update files if provided
            if model.files:
                # Clear old files
                session.query(CachedFile).filter_by(model_id=model.id).delete()
                
                # Add new files
                for file in model.files:
                    cached_file = CachedFile(
                        model_id=model.id,
                        filename=file.filename,
                        size=file.size,
                        url=file.url,
                        sha256=file.sha256,
                        is_gguf=file.is_gguf,
                        quantisation=file.quantisation
                    )
                    session.add(cached_file)
        else:
            # Create new
            cached = CachedModel(
                id=model.id,
                name=model.name,
                author=model.author,
                description=model.description,
                tags=json.dumps(model.tags),
                licence=model.licence,
                downloads=model.downloads,
                likes=model.likes,
                created_at=model.created_at,
                updated_at=model.updated_at,
                has_gguf=model.has_gguf,
                total_size=model.total_size
            )
            session.add(cached)
            
            # Add files if provided
            if model.files:
                for file in model.files:
                    cached_file = CachedFile(
                        model_id=model.id,
                        filename=file.filename,
                        size=file.size,
                        url=file.url,
                        sha256=file.sha256,
                        is_gguf=file.is_gguf,
                        quantisation=file.quantisation
                    )
                    session.add(cached_file)
    
    def _get_cached_model(self, session, model_id: str) -> Optional[ModelInfo]:
        """Get cached model from session."""
        cached = session.query(CachedModel).filter_by(id=model_id).first()
        
        if not cached:
            return None
        
        # Check expiry
        expiry = datetime.utcnow() - timedelta(hours=self.MODEL_CACHE_HOURS)
        if cached.cached_at < expiry:
            return None
        
        # Convert to ModelInfo
        files = []
        for cached_file in cached.files:
            files.append(ModelFile(
                filename=cached_file.filename,
                size=cached_file.size,
                url=cached_file.url,
                sha256=cached_file.sha256,
                is_gguf=cached_file.is_gguf,
                quantisation=cached_file.quantisation
            ))
        
        return ModelInfo(
            id=cached.id,
            name=cached.name,
            author=cached.author,
            description=cached.description,
            tags=json.loads(cached.tags) if cached.tags else [],
            licence=cached.licence,
            downloads=cached.downloads,
            likes=cached.likes,
            created_at=cached.created_at,
            updated_at=cached.updated_at,
            has_gguf=cached.has_gguf,
            total_size=cached.total_size,
            files=files
        )


# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        Global CacheManager instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance
