"""
ModelShelf Library Indexer
Scans and indexes downloaded model files.
"""

import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

from app.config import DEFAULT_DOWNLOAD_DIR
from domain.models import format_size

logger = logging.getLogger(__name__)


@dataclass
class ModelFile:
    """Represents a file in the library."""
    filename: str
    path: Path
    size: int
    is_gguf: bool = False
    quantisation: Optional[str] = None
    modified_at: Optional[datetime] = None


@dataclass
class ModelEntry:
    """Represents a model in the library."""
    id: str  # e.g., "TheBloke_Llama-2-7B-GGUF"
    name: str  # Display name
    path: Path  # Root folder
    files: List[ModelFile] = field(default_factory=list)
    total_size: int = 0
    file_count: int = 0
    gguf_count: int = 0
    added_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    
    def calculate_stats(self):
        """Calculate statistics from files."""
        self.total_size = sum(f.size for f in self.files)
        self.file_count = len(self.files)
        self.gguf_count = sum(1 for f in self.files if f.is_gguf)


class LibraryIndexer:
    """
    Indexes and manages the local model library.
    """
    
    GGUF_EXTENSIONS = ('.gguf',)
    METADATA_FILE = '.modelshelf_index.json'
    
    def __init__(self, library_path: Optional[Path] = None):
        """
        Initialise library indexer.
        
        Args:
            library_path: Path to library folder
        """
        self.library_path = library_path or DEFAULT_DOWNLOAD_DIR
        self.library_path.mkdir(parents=True, exist_ok=True)
        self._index: Dict[str, ModelEntry] = {}
        self._metadata_path = self.library_path / self.METADATA_FILE
    
    def scan(self, force: bool = False) -> List[ModelEntry]:
        """
        Scan library folder and build index.
        
        Args:
            force: Force full rescan even if metadata exists
        
        Returns:
            List of ModelEntry objects
        """
        logger.info(f"Scanning library at {self.library_path}")
        
        # Load existing metadata if available
        if not force and self._metadata_path.exists():
            self._load_metadata()
        
        scanned_models: Set[str] = set()
        
        # Scan for model folders
        if not self.library_path.exists():
            logger.warning(f"Library path doesn't exist: {self.library_path}")
            return []
        
        for item in self.library_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                model_id = item.name
                scanned_models.add(model_id)
                
                # Check if already indexed and up-to-date
                if model_id in self._index and not force:
                    # Quick check if folder modified time changed
                    cached_entry = self._index[model_id]
                    if cached_entry.path.stat().st_mtime == item.stat().st_mtime:
                        continue
                
                # Scan this model
                entry = self._scan_model_folder(item)
                if entry:
                    self._index[model_id] = entry
        
        # Remove entries for models that no longer exist
        removed = set(self._index.keys()) - scanned_models
        for model_id in removed:
            del self._index[model_id]
            logger.info(f"Removed deleted model from index: {model_id}")
        
        # Save metadata
        self._save_metadata()
        
        return list(self._index.values())
    
    def _scan_model_folder(self, folder: Path) -> Optional[ModelEntry]:
        """
        Scan a single model folder.
        
        Args:
            folder: Path to model folder
        
        Returns:
            ModelEntry or None if invalid
        """
        try:
            model_id = folder.name
            
            # Extract display name (replace underscores with slashes)
            display_name = model_id.replace('_', '/', 1) if '_' in model_id else model_id
            
            files: List[ModelFile] = []
            
            # Scan all files
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    file_info = self._scan_file(file_path)
                    if file_info:
                        files.append(file_info)
            
            if not files:
                return None
            
            # Create entry
            entry = ModelEntry(
                id=model_id,
                name=display_name,
                path=folder,
                files=files,
                added_at=datetime.fromtimestamp(folder.stat().st_ctime),
                last_accessed=datetime.fromtimestamp(folder.stat().st_atime)
            )
            
            entry.calculate_stats()
            
            logger.info(f"Indexed model: {display_name} ({entry.file_count} files, {format_size(entry.total_size)})")
            
            return entry
            
        except Exception as e:
            logger.error(f"Failed to scan model folder {folder}: {e}")
            return None
    
    def _scan_file(self, file_path: Path) -> Optional[ModelFile]:
        """
        Scan a single file.
        
        Args:
            file_path: Path to file
        
        Returns:
            ModelFile or None
        """
        try:
            stat = file_path.stat()
            is_gguf = file_path.suffix.lower() in self.GGUF_EXTENSIONS
            
            # Extract quantisation from filename if GGUF
            quantisation = None
            if is_gguf:
                quantisation = self._extract_quantisation(file_path.name)
            
            return ModelFile(
                filename=file_path.name,
                path=file_path,
                size=stat.st_size,
                is_gguf=is_gguf,
                quantisation=quantisation,
                modified_at=datetime.fromtimestamp(stat.st_mtime)
            )
            
        except Exception as e:
            logger.error(f"Failed to scan file {file_path}: {e}")
            return None
    
    def _extract_quantisation(self, filename: str) -> Optional[str]:
        """Extract quantisation type from filename."""
        import re
        patterns = [
            r'Q[2-8]_[KM](?:_[SML])?',
            r'IQ[1-4]_[XYSM]',
            r'F(?:16|32)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(0).upper()
        
        return None
    
    def get_all_models(self) -> List[ModelEntry]:
        """Get all indexed models."""
        return list(self._index.values())
    
    def get_model(self, model_id: str) -> Optional[ModelEntry]:
        """Get a specific model by ID."""
        return self._index.get(model_id)
    
    def get_total_size(self) -> int:
        """Get total size of all models in bytes."""
        return sum(entry.total_size for entry in self._index.values())
    
    def get_model_count(self) -> int:
        """Get number of models."""
        return len(self._index)
    
    def delete_model(self, model_id: str) -> bool:
        """
        Delete a model from library.
        
        Args:
            model_id: Model identifier
        
        Returns:
            True if deleted successfully
        """
        entry = self._index.get(model_id)
        if not entry:
            return False
        
        try:
            # Delete folder
            import shutil
            shutil.rmtree(entry.path)
            
            # Remove from index
            del self._index[model_id]
            self._save_metadata()
            
            logger.info(f"Deleted model: {entry.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete model {model_id}: {e}")
            return False
    
    def _save_metadata(self):
        """Save index metadata to disk."""
        try:
            metadata = {
                'version': '1.0',
                'last_scan': datetime.now().isoformat(),
                'models': {
                    model_id: {
                        'name': entry.name,
                        'total_size': entry.total_size,
                        'file_count': entry.file_count,
                        'gguf_count': entry.gguf_count,
                        'added_at': entry.added_at.isoformat() if entry.added_at else None
                    }
                    for model_id, entry in self._index.items()
                }
            }
            
            with open(self._metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _load_metadata(self):
        """Load index metadata from disk."""
        try:
            with open(self._metadata_path, 'r') as f:
                metadata = json.load(f)
            
            logger.info(f"Loaded metadata from {metadata.get('last_scan')}")
            
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")


# Global indexer instance
_indexer_instance: Optional[LibraryIndexer] = None


def get_indexer() -> LibraryIndexer:
    """
    Get the global library indexer instance.
    
    Returns:
        Global LibraryIndexer instance
    """
    global _indexer_instance
    if _indexer_instance is None:
        _indexer_instance = LibraryIndexer()
    return _indexer_instance
