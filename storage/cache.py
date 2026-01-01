"""
ModelShelf Cache Manager
Caching layer for search results and model metadata.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from storage.database import get_database
from domain.models import Model, ModelFile

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages caching of model metadata and search results.
    """
    
    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialise cache manager.
        
        Args:
            cache_ttl_hours: Time-to-live for cached data in hours
        """
        self.db = get_database()
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
    
    def cache_model(self, model: Model) -> None:
        """
        Cache a model and its files.
        
        Args:
            model: Model to cache
        """
        try:
            with self.db.transaction() as conn:
                now = datetime.utcnow().isoformat()
                
                # Insert or replace model
                conn.execute("""
                    INSERT OR REPLACE INTO cached_models (
                        id, name, author, description, tags, licence,
                        downloads, likes, created_at, updated_at, source, cached_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    model.id,
                    model.name,
                    model.author,
                    model.description,
                    json.dumps(model.tags),
                    model.licence,
                    model.downloads,
                    model.likes,
                    model.created_at.isoformat() if model.created_at else None,
                    model.updated_at.isoformat() if model.updated_at else None,
                    model.source,
                    now
                ))
                
                # Delete existing files for this model
                conn.execute("DELETE FROM cached_files WHERE model_id = ?", (model.id,))
                
                # Insert files
                for file in model.files:
                    conn.execute("""
                        INSERT INTO cached_files (
                            model_id, filename, size, url, sha256, file_type, cached_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        model.id,
                        file.filename,
                        file.size,
                        file.url,
                        file.sha256,
                        file.file_type.value,
                        now
                    ))
            
            logger.debug(f"Cached model {model.id} with {len(model.files)} files")
            
        except Exception as e:
            logger.error(f"Failed to cache model {model.id}: {e}", exc_info=True)
    
    def get_cached_model(self, model_id: str) -> Optional[Model]:
        """
        Retrieve a cached model if it exists and is not expired.
        
        Args:
            model_id: Model identifier
        
        Returns:
            Cached Model or None if not found/expired
        """
        try:
            conn = self.db.get_connection()
            
            # Get model
            cursor = conn.execute(
                "SELECT * FROM cached_models WHERE id = ?",
                (model_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            # Check if expired
            cached_at = datetime.fromisoformat(row['cached_at'])
            if datetime.utcnow() - cached_at > self.cache_ttl:
                logger.debug(f"Cached model {model_id} expired")
                return None
            
            # Convert to Model object
            model = Model(
                id=row['id'],
                name=row['name'],
                author=row['author'],
                description=row['description'],
                tags=json.loads(row['tags']) if row['tags'] else [],
                licence=row['licence'],
                downloads=row['downloads'],
                likes=row['likes'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                source=row['source']
            )
            
            # Get files
            cursor = conn.execute(
                "SELECT * FROM cached_files WHERE model_id = ? ORDER BY filename",
                (model_id,)
            )
            
            files = []
            for file_row in cursor:
                files.append(ModelFile(
                    filename=file_row['filename'],
                    size=file_row['size'],
                    url=file_row['url'],
                    sha256=file_row['sha256']
                ))
            
            model.files = files
            logger.debug(f"Retrieved cached model {model_id}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to get cached model {model_id}: {e}", exc_info=True)
            return None
    
    def cache_models_batch(self, models: List[Model]) -> None:
        """
        Cache multiple models at once.
        
        Args:
            models: List of models to cache
        """
        for model in models:
            self.cache_model(model)
    
    def clear_expired_cache(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        try:
            expiry_time = datetime.utcnow() - self.cache_ttl
            
            with self.db.transaction() as conn:
                # Delete expired models (files will cascade)
                cursor = conn.execute(
                    "DELETE FROM cached_models WHERE cached_at < ?",
                    (expiry_time.isoformat(),)
                )
                count = cursor.rowcount
            
            if count > 0:
                logger.info(f"Cleared {count} expired cache entries")
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}", exc_info=True)
            return 0
    
    def clear_all_cache(self) -> None:
        """
        Clear all cached data.
        """
        try:
            with self.db.transaction() as conn:
                conn.execute("DELETE FROM cached_files")
                conn.execute("DELETE FROM cached_models")
            
            logger.info("Cleared all cache data")
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}", exc_info=True)
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            conn = self.db.get_connection()
            
            # Count models
            cursor = conn.execute("SELECT COUNT(*) as count FROM cached_models")
            model_count = cursor.fetchone()['count']
            
            # Count files
            cursor = conn.execute("SELECT COUNT(*) as count FROM cached_files")
            file_count = cursor.fetchone()['count']
            
            # Total size
            cursor = conn.execute("SELECT SUM(size) as total FROM cached_files")
            total_size = cursor.fetchone()['total'] or 0
            
            return {
                "models": model_count,
                "files": file_count,
                "total_size_bytes": total_size,
                "total_size_mb": total_size / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}", exc_info=True)
            return {"models": 0, "files": 0, "total_size_bytes": 0, "total_size_mb": 0}
