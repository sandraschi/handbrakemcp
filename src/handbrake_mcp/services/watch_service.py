"""Watch folder service for automatic video processing."""
import asyncio
import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from handbrake_mcp.core.config import settings

logger = logging.getLogger(__name__)


class WatchHandler(FileSystemEventHandler):
    """Handler for file system events."""
    
    def __init__(self, callback: Callable[[Path], None], patterns: Optional[List[str]] = None):
        """Initialize the handler.
        
        Args:
            callback: Function to call when a matching file is created
            patterns: List of file patterns to watch (e.g., ['*.mp4', '*.mkv'])
        """
        self.callback = callback
        self.patterns = patterns or ['*.mp4', '*.mkv', '*.avi', '*.mov', '*.m4v']
        self.processed_files: Set[Path] = set()
    
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if self._should_process(file_path):
            logger.info(f"New file detected: {file_path}")
            self.processed_files.add(file_path)
            self.callback(file_path)
    
    def _should_process(self, file_path: Path) -> bool:
        """Check if a file should be processed."""
        # Skip if already processed
        if file_path in self.processed_files:
            return False
        
        # Check file extension
        if not any(file_path.match(p) for p in self.patterns):
            return False
        
        # Check if file is fully written (not being downloaded)
        try:
            initial_size = file_path.stat().st_size
            await asyncio.sleep(1)  # Wait a bit
            return file_path.stat().st_size == initial_size
        except (OSError, PermissionError) as e:
            logger.warning(f"Error checking file {file_path}: {e}")
            return False


class WatchService:
    """Service for watching directories for new video files."""
    
    def __init__(self):
        """Initialize the watch service."""
        self.observer = Observer()
        self.handlers: Dict[Path, WatchHandler] = {}
        self.running = False
    
    async def start(self, callback: Callable[[Path], None], watch_dirs: List[Path], patterns: Optional[List[str]] = None):
        """Start watching directories for new files.
        
        Args:
            callback: Function to call when a new file is detected
            watch_dirs: List of directories to watch
            patterns: List of file patterns to watch
        """
        if self.running:
            logger.warning("Watch service is already running")
            return
        
        self.running = True
        
        # Start the observer in a separate thread
        def start_observer():
            for watch_dir in watch_dirs:
                if not watch_dir.exists():
                    logger.warning(f"Watch directory does not exist: {watch_dir}")
                    continue
                
                handler = WatchHandler(callback, patterns)
                self.handlers[watch_dir] = handler
                self.observer.schedule(handler, str(watch_dir), recursive=True)
                logger.info(f"Watching directory: {watch_dir}")
            
            self.observer.start()
        
        # Run the observer in a separate thread
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, start_observer)
        logger.info("Watch service started")
    
    async def stop(self):
        """Stop watching directories."""
        if not self.running:
            return
        
        self.running = False
        
        # Stop the observer
        def stop_observer():
            self.observer.stop()
            self.observer.join()
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, stop_observer)
        
        self.handlers.clear()
        logger.info("Watch service stopped")
    
    def is_running(self) -> bool:
        """Check if the watch service is running."""
        return self.running


# Global instance
watch_service = WatchService()
