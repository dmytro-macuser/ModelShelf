"""
ModelShelf Database Layer
SQLite database for caching and persistence.
"""

import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session

from app.config import DATABASE_PATH

logger = logging.getLogger(__name__)

Base = declarative_base()


class CachedModel(Base):
    """Cached model metadata."""
    __tablename__ = 'cached_models'
    
    id = Column(String, primary_key=True)  # model_id
    name = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array as string
    licence = Column(String, nullable=True)
    downloads = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    has_gguf = Column(Boolean, default=False)
    total_size = Column(Integer, default=0)
    cached_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    files = relationship('CachedFile', back_populates='model', cascade='all, delete-orphan')


class CachedFile(Base):
    """Cached file metadata."""
    __tablename__ = 'cached_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String, ForeignKey('cached_models.id'), nullable=False)
    filename = Column(String, nullable=False)
    size = Column(Integer, default=0)
    url = Column(String, nullable=False)
    sha256 = Column(String, nullable=True)
    is_gguf = Column(Boolean, default=False)
    quantisation = Column(String, nullable=True)
    
    # Relationships
    model = relationship('CachedModel', back_populates='files')


class SearchCache(Base):
    """Search results cache."""
    __tablename__ = 'search_cache'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_hash = Column(String, unique=True, nullable=False)  # Hash of search params
    query = Column(String, nullable=False)
    has_gguf = Column(Boolean, default=False)
    sort_by = Column(String, default='downloads')
    page = Column(Integer, default=0)
    page_size = Column(Integer, default=20)
    result_ids = Column(Text, nullable=False)  # JSON array of model IDs
    total_count = Column(Integer, default=0)
    has_next = Column(Boolean, default=False)
    cached_at = Column(DateTime, default=datetime.utcnow)


class DownloadHistory(Base):
    """Download history."""
    __tablename__ = 'download_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    local_path = Column(String, nullable=False)
    size = Column(Integer, default=0)
    state = Column(String, default='completed')  # DownloadState enum value
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)


class DatabaseManager:
    """Database connection and session manager."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialise database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or str(DATABASE_PATH)
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialised: {self.db_path}")
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close database connection."""
        self.engine.dispose()


# Global database instance
_db_instance: Optional[DatabaseManager] = None


def get_database() -> DatabaseManager:
    """
    Get the global database instance.
    
    Returns:
        Global DatabaseManager instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
