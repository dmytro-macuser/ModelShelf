"""
ModelShelf UI Bridge
Python-QML communication layer.
"""

import logging
import asyncio
from typing import Optional, Dict
from PySide6.QtCore import QObject, Signal, Slot, Property, QThread, QTimer
from PySide6.QtQml import QmlElement

from app.services import get_service_manager
from domain.models import SearchFilter, format_size, DownloadState
from sources.hub_adapter import ModelInfo
from downloader.manager import DownloadItem

logger = logging.getLogger(__name__)

# QML registration
QML_IMPORT_NAME = "ModelShelf"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class SearchBridge(QObject):
    """
    Bridge for search operations between QML and Python.
    """
    
    # Signals
    searchStarted = Signal()
    searchCompleted = Signal(list, int, bool)  # models, total_count, has_next
    searchFailed = Signal(str)  # error_message
    modelDetailsLoaded = Signal('QVariantMap')  # model details
    modelDetailsLoadFailed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._service = get_service_manager().get_search_service()
        self._loop = None
        self._current_filter = SearchFilter()
    
    @Slot(str, bool, str, int, int)
    def search(
        self,
        query: str,
        has_gguf: bool,
        sort_by: str,
        page: int,
        page_size: int
    ):
        """
        Perform search with given parameters.
        
        Args:
            query: Search query text
            has_gguf: Filter for GGUF files
            sort_by: Sort criterion
            page: Page number (0-indexed)
            page_size: Results per page
        """
        logger.info(f"Search requested: query='{query}', has_gguf={has_gguf}, sort={sort_by}")
        
        # Update filter
        self._current_filter.query = query
        self._current_filter.has_gguf = has_gguf
        self._current_filter.sort_by = sort_by
        self._current_filter.page = page
        self._current_filter.page_size = page_size
        
        self.searchStarted.emit()
        
        # Run async search in thread
        thread = SearchThread(self._service, self._current_filter)
        thread.finished.connect(self._on_search_finished)
        thread.failed.connect(self._on_search_failed)
        thread.start()
    
    @Slot(str)
    def loadModelDetails(self, model_id: str):
        """
        Load detailed model information.
        
        Args:
            model_id: Model identifier
        """
        logger.info(f"Loading model details: {model_id}")
        
        thread = ModelDetailsThread(self._service, model_id)
        thread.finished.connect(self._on_model_details_loaded)
        thread.failed.connect(self._on_model_details_failed)
        thread.start()
    
    def _on_search_finished(self, result):
        """Handle search completion."""
        # Convert models to QML-friendly format
        models = []
        for model in result.models:
            models.append({
                'id': model.id,
                'name': model.name,
                'author': model.author,
                'description': model.description or '',
                'tags': model.tags,
                'licence': model.licence or 'Unknown',
                'downloads': model.downloads,
                'likes': model.likes,
                'hasGguf': model.has_gguf,
                'totalSize': format_size(model.total_size),
                'totalSizeBytes': model.total_size
            })
        
        self.searchCompleted.emit(models, result.total_count, result.has_next)
    
    def _on_search_failed(self, error: str):
        """Handle search failure."""
        logger.error(f"Search failed: {error}")
        self.searchFailed.emit(error)
    
    def _on_model_details_loaded(self, model: ModelInfo):
        """Handle model details loaded."""
        # Convert to QML-friendly format
        files = []
        for file in model.files:
            files.append({
                'filename': file.filename,
                'size': format_size(file.size),
                'sizeBytes': file.size,
                'url': file.url,
                'isGguf': file.is_gguf,
                'quantisation': file.quantisation or 'N/A'
            })
        
        details = {
            'id': model.id,
            'name': model.name,
            'author': model.author,
            'description': model.description or 'No description available.',
            'tags': model.tags,
            'licence': model.licence or 'Unknown',
            'downloads': model.downloads,
            'likes': model.likes,
            'hasGguf': model.has_gguf,
            'totalSize': format_size(model.total_size),
            'files': files
        }
        
        self.modelDetailsLoaded.emit(details)
    
    def _on_model_details_failed(self, error: str):
        """Handle model details load failure."""
        logger.error(f"Model details load failed: {error}")
        self.modelDetailsLoadFailed.emit(error)


@QmlElement
class DownloadBridge(QObject):
    """
    Bridge for download operations.
    """
    
    # Signals
    downloadAdded = Signal(str)  # download_id
    downloadStateChanged = Signal(str, str)  # id, state
    downloadProgress = Signal(str, float, str, str)  # id, progress, speed, eta
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._service = get_service_manager().get_download_service()
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Setup callbacks from manager."""
        self._service.manager.on_state_change = self._on_state_change
        self._service.manager.on_progress = self._on_progress
    
    @Slot(str, str, str, int)
    def addDownload(self, model_id: str, filename: str, url: str, size: int):
        """Add a download."""
        download_id = self._service.add_download(model_id, filename, url, size)
        self.downloadAdded.emit(download_id)
    
    @Slot(str)
    def pauseDownload(self, download_id: str):
        """Pause a download."""
        self._service.pause_download(download_id)
    
    @Slot(str)
    def resumeDownload(self, download_id: str):
        """Resume a download."""
        self._service.resume_download(download_id)
    
    @Slot(str)
    def cancelDownload(self, download_id: str):
        """Cancel a download."""
        self._service.cancel_download(download_id)
    
    @Slot(result=list)
    def getDownloads(self):
        """Get all downloads."""
        items = self._service.get_downloads()
        result = []
        for item in items:
            result.append(self._format_item(item))
        return result
    
    def _on_state_change(self, item: DownloadItem):
        """Handle state change."""
        self.downloadStateChanged.emit(item.id, item.state.value)
    
    def _on_progress(self, item: DownloadItem):
        """Handle progress update."""
        speed_str = f"{format_size(item.speed)}/s"
        
        eta_str = "--"
        if item.eta is not None:
            if item.eta < 60:
                eta_str = f"{int(item.eta)}s"
            elif item.eta < 3600:
                eta_str = f"{int(item.eta/60)}m"
            else:
                eta_str = f"{int(item.eta/3600)}h"
        
        self.downloadProgress.emit(item.id, item.progress, speed_str, eta_str)
    
    def _format_item(self, item: DownloadItem) -> Dict:
        """Format item for QML."""
        return {
            'id': item.id,
            'modelId': item.model_id,
            'filename': item.filename,
            'totalSize': format_size(item.total_size),
            'downloadedSize': format_size(item.downloaded_size),
            'progress': item.progress,
            'state': item.state.value,
            'speed': "0 B/s",
            'eta': "--"
        }


class SearchThread(QThread):
    """Thread for running async search operations."""
    
    finished = Signal(object)  # SearchResult
    failed = Signal(str)  # error message
    
    def __init__(self, service, filter: SearchFilter):
        super().__init__()
        self.service = service
        self.filter = filter
    
    def run(self):
        """Run the search."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.service.search(self.filter))
            loop.close()
            self.finished.emit(result)
        except Exception as e:
            self.failed.emit(str(e))


class ModelDetailsThread(QThread):
    """Thread for loading model details."""
    
    finished = Signal(object)  # ModelInfo
    failed = Signal(str)  # error message
    
    def __init__(self, service, model_id: str):
        super().__init__()
        self.service = service
        self.model_id = model_id
    
    def run(self):
        """Load model details."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            model = loop.run_until_complete(self.service.get_model_details(self.model_id))
            loop.close()
            
            if model:
                self.finished.emit(model)
            else:
                self.failed.emit("Model not found")
        except Exception as e:
            self.failed.emit(str(e))
