import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradeFileHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable = None, debounce_time: float = 2.0):
        self.callback = callback
        self.debounce_time = debounce_time
        self.last_processed = {}
        self.lock = threading.Lock()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        current_time = time.time()
        
        with self.lock:
            # Debounce: only process if enough time has passed since last event for this file
            if file_path in self.last_processed:
                if current_time - self.last_processed[file_path] < self.debounce_time:
                    logger.info(f"Debounced event for {file_path}")
                    return
            
            self.last_processed[file_path] = current_time
        
        logger.info(f"New file detected: {file_path}")
        
        # Wait a moment for file to be fully written
        time.sleep(0.5)
        
        # Call the callback function if provided
        if self.callback:
            try:
                self.callback(file_path)
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
    
    def on_modified(self, event):
        # Handle file modifications (in case files are updated)
        if not event.is_directory:
            logger.info(f"File modified: {event.src_path}")

def monitor_folders(folder_paths: List[str], callback: Callable = None, debounce_time: float = 2.0):
    """
    Start monitoring folders for new files.
    
    Args:
        folder_paths: List of folder paths to monitor
        callback: Function to call when new files are detected
        debounce_time: Minimum time between processing events for the same file
    """
    # Check if monitoring is already active
    if hasattr(monitor_folders, '_observer') and monitor_folders._observer.is_alive():
        logger.info("Folder monitoring is already active")
        return monitor_folders._thread
    
    event_handler = TradeFileHandler(callback=callback, debounce_time=debounce_time)
    observer = Observer()
    
    for folder in folder_paths:
        if os.path.exists(folder):
            try:
                observer.schedule(event_handler, folder, recursive=False)
                logger.info(f"Monitoring folder: {folder}")
            except Exception as e:
                logger.error(f"Error scheduling folder {folder}: {e}")
        else:
            logger.warning(f"Folder does not exist: {folder}")
    
    observer.start()
    logger.info("Folder monitoring started")

    def monitor():
        try:
            while True:
                time.sleep(1)  # Check every second
        except KeyboardInterrupt:
            logger.info("Stopping folder monitoring...")
            observer.stop()
        observer.join()

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    
    # Store references to prevent garbage collection
    monitor_folders._observer = observer
    monitor_folders._thread = thread
    
    return thread

if __name__ == "__main__":
    folders_to_monitor = [
        os.getenv("OUTGOING_FOLDER", "outgoing/"),
        os.getenv("INCOMING_ACK_FOLDER", "incoming/out/"),
        os.getenv("INCOMING_ERROR_FOLDER", "incoming/error/")
    ]
    
    def test_callback(file_path):
        print(f"Processing file: {file_path}")
    
    monitor_folders(folders_to_monitor, callback=test_callback)