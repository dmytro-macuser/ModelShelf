"""
ModelShelf Download Manager
Handles file downloads, queue management, and resumption.
"""

import asyncio
import hashlib
import logging
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable, Awaitable
from enum import Enum

import httpx

from app.config import DEFAULT_DOWNLOAD_DIR
from domain.models import DownloadState

logger = logging.getLogger(__name__)


@dataclass
class DownloadItem:
    """Represents a file in the download queue."""
    id: str  # Unique ID (e.g., "model_id/filename")
    model_id: str
    filename: str
    url: str
    destination_path: Path
    total_size: int = 0
    downloaded_size: int = 0
    state: DownloadState = DownloadState.QUEUED
    error_message: Optional[str] = None
    speed: float = 0.0  # bytes/second
    eta: Optional[float] = None  # seconds
    created_at: float = field(default_factory=time.time)
    
    # Internal
    _task: Optional[asyncio.Task] = None
    _cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
    
    @property
    def progress(self) -> float:
        """Download progress (0.0 to 1.0)."""
        if self.total_size == 0:
            return 0.0
        return min(1.0, self.downloaded_size / self.total_size)
    
    @property
    def is_active(self) -> bool:
        """Check if download is currently active."""
        return self.state == DownloadState.DOWNLOADING
    
    @property
    def is_finished(self) -> bool:
        """Check if download is finished (completed, failed, cancelled)."""
        return self.state in (DownloadState.COMPLETED, DownloadState.FAILED, DownloadState.CANCELLED)
    
    def reset_stats(self):
        """Reset speed and ETA stats."""
        self.speed = 0.0
        self.eta = None


class DownloadManager:
    """
    Manages the download queue and executes downloads.
    """
    
    def __init__(self, max_concurrent: int = 3, download_dir: Optional[Path] = None):
        self.max_concurrent = max_concurrent
        self.download_dir = download_dir or DEFAULT_DOWNLOAD_DIR
        self._queue: List[DownloadItem] = []
        self._items: Dict[str, DownloadItem] = {}  # id -> item
        self._active_downloads: Set[str] = set()
        self._client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self._shutdown = False
        
        # Callbacks
        self.on_progress: Optional[Callable[[DownloadItem], None]] = None
        self.on_state_change: Optional[Callable[[DownloadItem], None]] = None
        
        # Ensure download directory exists
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def add_download(self, model_id: str, filename: str, url: str, size: int) -> str:
        """
        Add a file to the download queue.
        
        Returns:
            Download ID
        """
        download_id = f"{model_id}/{filename}"
        
        # Check if already exists
        if download_id in self._items:
            item = self._items[download_id]
            if item.state in (DownloadState.FAILED, DownloadState.CANCELLED):
                # Retry/Resume
                self.resume_download(download_id)
            return download_id
            
        # Determine destination
        model_dir = self.download_dir / model_id.replace("/", "_")
        model_dir.mkdir(parents=True, exist_ok=True)
        dest_path = model_dir / filename
        
        # Check if already downloaded on disk
        initial_state = DownloadState.QUEUED
        downloaded = 0
        
        if dest_path.exists():
            current_size = dest_path.stat().st_size
            if current_size == size:
                initial_state = DownloadState.COMPLETED
                downloaded = size
            elif current_size < size:
                # Partial download exists
                downloaded = current_size
        
        item = DownloadItem(
            id=download_id,
            model_id=model_id,
            filename=filename,
            url=url,
            destination_path=dest_path,
            total_size=size,
            downloaded_size=downloaded,
            state=initial_state
        )
        
        self._items[download_id] = item
        
        if initial_state != DownloadState.COMPLETED:
            self._queue.append(item)
            self._process_queue()
        
        self._notify_state(item)
        return download_id
    
    def pause_download(self, download_id: str):
        """Pause a download."""
        item = self._items.get(download_id)
        if not item or item.state != DownloadState.DOWNLOADING:
            return
            
        item._cancel_event.set()
        item.state = DownloadState.PAUSED
        if download_id in self._active_downloads:
            self._active_downloads.remove(download_id)
        
        self._notify_state(item)
        self._process_queue()
    
    def resume_download(self, download_id: str):
        """Resume a paused/failed/cancelled download."""
        item = self._items.get(download_id)
        if not item:
            return
            
        if item.state == DownloadState.COMPLETED:
            return
            
        if item.state == DownloadState.DOWNLOADING:
            return
            
        # Reset cancel event
        item._cancel_event.clear()
        item.state = DownloadState.QUEUED
        item.error_message = None
        
        if item not in self._queue:
            self._queue.append(item)
            
        self._notify_state(item)
        self._process_queue()
    
    def cancel_download(self, download_id: str, delete_file: bool = False):
        """Cancel a download."""
        item = self._items.get(download_id)
        if not item:
            return
            
        if item.state == DownloadState.DOWNLOADING:
            item._cancel_event.set()
        
        item.state = DownloadState.CANCELLED
        if download_id in self._active_downloads:
            self._active_downloads.remove(download_id)
            
        if item in self._queue:
            self._queue.remove(item)
            
        if delete_file and item.destination_path.exists():
            # Only delete partial files, not completed ones unless explicit
            if item.downloaded_size < item.total_size:
                try:
                    item.destination_path.unlink()
                    item.downloaded_size = 0
                except OSError as e:
                    logger.error(f"Failed to delete file {item.destination_path}: {e}")
        
        self._notify_state(item)
        self._process_queue()
    
    def get_item(self, download_id: str) -> Optional[DownloadItem]:
        """Get download item by ID."""
        return self._items.get(download_id)
    
    def get_all_items(self) -> List[DownloadItem]:
        """Get all download items."""
        return list(self._items.values())
    
    async def cleanup(self):
        """Cleanup resources."""
        self._shutdown = True
        for item in self._items.values():
            if item.state == DownloadState.DOWNLOADING:
                item._cancel_event.set()
        
        await self._client.aclose()
    
    def _process_queue(self):
        """Process the download queue."""
        if self._shutdown:
            return
            
        # Clean up finished tasks from active set
        finished_ids = []
        for did in self._active_downloads:
            item = self._items.get(did)
            if item and not item.is_active:
                finished_ids.append(did)
        
        for did in finished_ids:
            self._active_downloads.remove(did)
            
        # Start new downloads if slot available
        while len(self._active_downloads) < self.max_concurrent and self._queue:
            # Find next queued item
            next_item = None
            for item in self._queue:
                if item.state == DownloadState.QUEUED:
                    next_item = item
                    break
            
            if not next_item:
                break
                
            # Start download
            self._queue.remove(next_item)
            self._active_downloads.add(next_item.id)
            next_item.state = DownloadState.DOWNLOADING
            self._notify_state(next_item)
            
            # Launch async task
            asyncio.create_task(self._download_task(next_item))
    
    async def _download_task(self, item: DownloadItem):
        """
        Async download task implementation with resume support.
        """
        try:
            headers = {}
            mode = "wb"
            
            # Check for existing partial file
            if item.destination_path.exists():
                current_size = item.destination_path.stat().st_size
                if current_size > 0 and current_size < item.total_size:
                    headers["Range"] = f"bytes={current_size}-"
                    mode = "ab"
                    item.downloaded_size = current_size
                    logger.info(f"Resuming download for {item.filename} from {current_size} bytes")
                elif current_size == item.total_size:
                    # Already finished
                    item.downloaded_size = current_size
                    item.state = DownloadState.COMPLETED
                    self._notify_state(item)
                    self._process_queue()
                    return
            
            async with self._client.stream("GET", item.url, headers=headers) as response:
                if response.status_code not in (200, 206):
                    raise Exception(f"HTTP error {response.status_code}")
                
                # Verify content length if not resuming or if server supports it
                content_length = response.headers.get("content-length")
                if content_length and mode == "wb":
                    # Note: For resume (206), content-length is the chunk size, not total
                    server_size = int(content_length)
                    if item.total_size == 0:
                        item.total_size = server_size
                
                with open(item.destination_path, mode) as f:
                    last_time = time.time()
                    bytes_since_last = 0
                    
                    async for chunk in response.aiter_bytes():
                        if item._cancel_event.is_set():
                            # Download paused or cancelled
                            if item.state == DownloadState.DOWNLOADING:
                                item.state = DownloadState.PAUSED
                            return
                        
                        f.write(chunk)
                        chunk_size = len(chunk)
                        item.downloaded_size += chunk_size
                        bytes_since_last += chunk_size
                        
                        # Update stats every 0.5 seconds
                        now = time.time()
                        if now - last_time >= 0.5:
                            duration = now - last_time
                            speed = bytes_since_last / duration
                            item.speed = speed
                            
                            remaining = item.total_size - item.downloaded_size
                            item.eta = remaining / speed if speed > 0 else None
                            
                            self._notify_progress(item)
                            
                            last_time = now
                            bytes_since_last = 0
            
            # Download complete
            item.state = DownloadState.COMPLETED
            item.reset_stats()
            item.downloaded_size = item.total_size  # Ensure consistency
            self._notify_state(item)
            logger.info(f"Download completed: {item.filename}")
            
        except Exception as e:
            logger.error(f"Download error for {item.filename}: {e}")
            item.state = DownloadState.FAILED
            item.error_message = str(e)
            item.reset_stats()
            self._notify_state(item)
            
        finally:
            if item.id in self._active_downloads:
                self._active_downloads.remove(item.id)
            self._process_queue()
            
    def _notify_state(self, item: DownloadItem):
        """Notify state change listener."""
        if self.on_state_change:
            try:
                self.on_state_change(item)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
                
    def _notify_progress(self, item: DownloadItem):
        """Notify progress listener."""
        if self.on_progress:
            try:
                self.on_progress(item)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
