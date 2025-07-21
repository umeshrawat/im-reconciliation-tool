import os
from src.folder_monitor import monitor_folders
from src.chat_ui import main as chat_ui_main
import streamlit as st

def main():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Only start folder monitoring once per session
    if "monitor_started" not in st.session_state:
        folders_to_monitor = [
            os.getenv("OUTGOING_FOLDER", "outgoing/"),
            os.getenv("INCOMING_ACK_FOLDER", "incoming/out/"),
            os.getenv("INCOMING_ERROR_FOLDER", "incoming/error/")
        ]
        monitor_folders(folders_to_monitor)
        st.session_state["monitor_started"] = True

    # Start the chat UI
    chat_ui_main()

if __name__ == "__main__":
    main()