import os
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st

# Import our modules
from watchers.folder_monitor import monitor_folders
from parsers.reconciliation_engine import ReconciliationEngine, process_file_for_reconciliation
from rag.vector_store import add_reconciliation_result, add_file_data, persist_vector_store
from chat.chat_interface import IMReconciliationChat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('im_reconciliation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IMReconciliationOrchestrator:
    def __init__(self):
        """Initialize the IM Reconciliation orchestrator."""
        self.reconciliation_engine = ReconciliationEngine()
        self.monitoring_thread = None
        self.setup_folders()
    
    def setup_folders(self):
        """Ensure required folders exist."""
        folders = [
            "outgoing/",
            "incoming/out/",
            "incoming/error/",
            "rag/chroma_db",
            "logs/"
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            logger.info(f"Ensured folder exists: {folder}")
    
    def process_new_file(self, file_path: str):
        """
        Process a new file that was detected by the folder monitor.
        
        Args:
            file_path: Path to the new file
        """
        try:
            logger.info(f"Processing new file: {file_path}")
            
            # Process the file for reconciliation
            result = process_file_for_reconciliation(file_path, self.reconciliation_engine)
            
            if 'error' in result:
                logger.error(f"Error processing file {file_path}: {result['error']}")
                return
            
            # Add parsed data to vector store
            if 'parsed_data' in result:
                doc_id = add_file_data(result['parsed_data'])
                if doc_id:
                    logger.info(f"Added file data to vector store: {doc_id}")
            
            # Add reconciliation result to vector store
            if 'reconciliation_result' in result:
                doc_id = add_reconciliation_result(result['reconciliation_result'])
                if doc_id:
                    logger.info(f"Added reconciliation result to vector store: {doc_id}")
            
            # Persist vector store
            persist_vector_store()
            
            logger.info(f"Successfully processed file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    def start_folder_monitoring(self):
        """Start monitoring folders for new files."""
        try:
            # Get folder paths from environment variables
            folders_to_monitor = [
                os.getenv("OUTGOING_FOLDER", "outgoing/"),
                os.getenv("INCOMING_ACK_FOLDER", "incoming/out/"),
                os.getenv("INCOMING_ERROR_FOLDER", "incoming/error/")
            ]
            
            # Start monitoring with callback
            self.monitoring_thread = monitor_folders(
                folder_paths=folders_to_monitor,
                callback=self.process_new_file,
                debounce_time=2.0
            )
            
            logger.info("Folder monitoring started successfully")
            
        except Exception as e:
            logger.error(f"Error starting folder monitoring: {e}")
    
    def process_existing_files(self):
        """Process any existing files in the monitored folders."""
        try:
            folders_to_monitor = [
                os.getenv("OUTGOING_FOLDER", "outgoing/"),
                os.getenv("INCOMING_ACK_FOLDER", "incoming/out/"),
                os.getenv("INCOMING_ERROR_FOLDER", "incoming/error/")
            ]
            
            for folder in folders_to_monitor:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path):
                            logger.info(f"Processing existing file: {file_path}")
                            self.process_new_file(file_path)
            
            logger.info("Finished processing existing files")
            
        except Exception as e:
            logger.error(f"Error processing existing files: {e}")
    
    def get_system_status(self) -> dict:
        """Get current system status."""
        try:
            from rag.vector_store import get_vector_store_stats
            
            stats = get_vector_store_stats()
            latest_reconciliation = self.reconciliation_engine.get_latest_reconciliation()
            
            return {
                'vector_store_stats': stats,
                'latest_reconciliation': latest_reconciliation,
                'monitoring_active': self.monitoring_thread is not None and self.monitoring_thread.is_alive(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}

def main():
    """Main function to run the IM Reconciliation Tool."""
    # Load environment variables
    load_dotenv()
    
    # Initialize orchestrator only once per session
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = IMReconciliationOrchestrator()
        
        # Process existing files on startup (only once)
        st.session_state.orchestrator.process_existing_files()
        
        # Start folder monitoring (only once)
        st.session_state.orchestrator.start_folder_monitoring()
    
    # Start the chat interface
    chat = IMReconciliationChat()
    chat.run()

def run_cli():
    """Run the tool in CLI mode (for testing)."""
    # Load environment variables
    load_dotenv()
    
    # Initialize orchestrator
    orchestrator = IMReconciliationOrchestrator()
    
    # Process existing files
    orchestrator.process_existing_files()
    
    # Start folder monitoring
    orchestrator.start_folder_monitoring()
    
    try:
        print("IM Reconciliation Tool started. Press Ctrl+C to stop.")
        print("Monitoring folders for new files...")
        
        # Keep the main thread alive
        while True:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        if orchestrator.monitoring_thread:
            orchestrator.monitoring_thread.join(timeout=5)
        print("Shutdown complete.")

if __name__ == "__main__":
    # Check if running in Streamlit
    if 'streamlit' in os.environ.get('STREAMLIT_SERVER_RUN_ON_SAVE', ''):
        main()
    else:
        # Run in CLI mode
        run_cli()