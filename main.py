import os
from src.folder_monitor import start_folder_monitoring
from src.reconciliation_engine import start_reconciliation_process
from src.chat_ui import start_chat_ui

def main():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Start folder monitoring in a separate thread
    folder_monitor_thread = start_folder_monitoring()

    # Start the reconciliation process
    reconciliation_thread = start_reconciliation_process()

    # Start the chat UI
    start_chat_ui()

if __name__ == "__main__":
    main()