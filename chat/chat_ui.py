import streamlit as st
import os
from utils.file_parsers import parse_trade_extract, parse_acknowledgment
from utils.state_cache import StateCache
from streamlit_autorefresh import st_autorefresh

# Initialize state cache
state_cache = StateCache()

# Streamlit UI setup
st.title("Intelligent IM Reconciliation Tool")

# Function to notify user of new files
def notify_user(new_files):
    for file in new_files:
        st.success(f"New file detected: {file}")

# Function to display reconciliation results
def display_reconciliation_results(results):
    if results:
        for result in results:
            st.write(result)
    else:
        st.info("No reconciliation results to display.")

# Main loop to check for new files and display results
def main():
    st_autorefresh(interval=2000, key="datarefresh")  # Refresh every 2 seconds
    # Placeholder for new files and results
    new_files = []
    reconciliation_results = []

    # List all files in monitored folders
    monitored_folders = [
        "outgoing/",
        "incoming/out/",
        "incoming/error/"
    ]
    for folder in monitored_folders:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    new_files.append(file_path)

    # Notify user of new files
    notify_user(new_files)

    # Simulate parsing and reconciliation
    for file in new_files:
        if "TRADE_EXTRACT" in file:
            trade_data = parse_trade_extract(file)
            state_cache.set("trade_data", trade_data)
        elif "ACK" in file:
            ack_data = parse_acknowledgment(file)
            reconciliation_results.append(f"Acknowledgment data parsed from {file}")

    # Display reconciliation results
    display_reconciliation_results(reconciliation_results)

if __name__ == "__main__":
    main()