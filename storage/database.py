"""
ModelShelf Database
SQLite schema and connection management.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
from app.config import DATABASE_PATH

logger = logging.getLogger(__name__)


class Database:
    """
    Database connection and schema manager.
    """
    
    SCHEMA_VERSION = 1
    
    # Schema definition
    SCHEMA = """
    -- Schema version tracking
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY
    );
    
    -- Cached model search results
    CREATE TABLE IF NOT EXISTS cached_models (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        author TEXT,
        description TEXT,
        tags TEXT,  -- JSON array
        licence TEXT,
        downloads INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        created_at TEXT,
        updated_at TEXT,
        source TEXT NOT NULL,
        cached_at TEXT NOT NULL,
        UNIQUE(id, source)
    );
    
    -- Cached model files
    CREATE TABLE IF NOT EXISTS cached_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        size INTEGER NOT NULL,
        url TEXT,
        sha256 TEXT,
        file_type TEXT,
        cached_at TEXT NOT NULL,
        FOREIGN KEY (model_id) REFERENCES cached_models(id) ON DELETE CASCADE,
        UNIQUE(model_id, filename)
    );
    
    -- Download history
    CREATE TABLE IF NOT EXISTS download_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        local_path TEXT NOT NULL,
        size INTEGER NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT,
        status TEXT NOT NULL,  -- queued, downloading, paused, completed, failed, cancelled
        error_message TEXT,
        FOREIGN KEY (model_id) REFERENCES cached_models(id)
    );
    
    -- Local shelf index
    CREATE TABLE IF NOT EXISTS shelf_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        local_path TEXT NOT NULL UNIQUE,
        size INTEGER NOT NULL,
        added_at TEXT NOT NULL,
        last_accessed_at TEXT,
        FOREIGN KEY (model_id) REFERENCES cached_models(id)
    );
    
    -- Indices for performance
    CREATE INDEX IF NOT EXISTS idx_cached_models_downloads ON cached_models(downloads DESC);
    CREATE INDEX IF NOT EXISTS idx_cached_models_likes ON cached_models(likes DESC);
    CREATE INDEX IF NOT EXISTS idx_cached_models_updated ON cached_models(updated_at DESC);
    CREATE INDEX IF NOT EXISTS idx_cached_files_model ON cached_files(model_id);
    CREATE INDEX IF NOT EXISTS idx_download_history_model ON download_history(model_id);
    CREATE INDEX IF NOT EXISTS idx_download_history_status ON download_history(status);
    CREATE INDEX IF NOT EXISTS idx_shelf_items_model ON shelf_items(model_id);
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialise database connection.
        
        Args:
            db_path: Path to database file (defaults to configured path)
        """
        self.db_path = db_path or DATABASE_PATH
        self._connection: Optional[sqlite3.Connection] = None
        self._initialise_database()
    
    def _initialise_database(self) -> None:
        """
        Create database file and tables if they don't exist.
        """
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create/open database
            conn = self.get_connection()
            
            # Execute schema
            conn.executescript(self.SCHEMA)
            
            # Set schema version
            cursor = conn.execute("SELECT version FROM schema_version")
            if cursor.fetchone() is None:
                conn.execute("INSERT INTO schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,))
            
            conn.commit()
            logger.info(f"Database initialised at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialise database: {e}", exc_info=True)
            raise
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection (creates if needed).
        
        Returns:
            SQLite connection
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False  # Allow multi-threaded access
            )
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            # Use Row factory for dict-like access
            self._connection.row_factory = sqlite3.Row
        
        return self._connection
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Yields:
            Database connection
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")
    
    def vacuum(self) -> None:
        """Optimize database."""
        try:
            self.get_connection().execute("VACUUM")
            logger.info("Database vacuumed")
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")


# Global database instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """
    Get the global database instance.
    Creates it if it doesn't exist.
    
    Returns:
        Global Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
