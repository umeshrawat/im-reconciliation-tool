import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TradeFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        print(f"New file detected: {file_path}")
        # Here you would call the reconciliation engine or other processing functions

def monitor_folders(folder_paths):
    event_handler = TradeFileHandler()
    observer = Observer()
    
    for folder in folder_paths:
        observer.schedule(event_handler, folder, recursive=False)
    
    observer.start()

    def monitor():
        try:
            while True:
                pass  # Keep thread alive
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    folders_to_monitor = [
        os.getenv("OUTGOING_FOLDER", "outgoing/"),
        os.getenv("INCOMING_ACK_FOLDER", "incoming/out/"),
        os.getenv("INCOMING_ERROR_FOLDER", "incoming/error/")
    ]
    monitor_folders(folders_to_monitor)