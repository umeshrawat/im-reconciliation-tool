import streamlit as st
import os
from utils.file_parsers import parse_trade_extract, parse_acknowledgment, parse_error_files
from utils.state_cache import StateCache

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
    # Placeholder for new files and results
    new_files = []
    reconciliation_results = []

    # Check for new files (this should be replaced with actual folder monitoring logic)
    # For demonstration, we will simulate new files
    simulated_new_files = ["TRADE_EXTRACT_20250720.csv", "ACK_20250720.csv"]
    new_files.extend(simulated_new_files)

    # Notify user of new files
    notify_user(new_files)

    # Simulate parsing and reconciliation
    for file in new_files:
        if "TRADE_EXTRACT" in file:
            trade_data = parse_trade_extract(file)
            state_cache.store_trade_data(trade_data)
        elif "ACK" in file:
            ack_data = parse_acknowledgment(file)
            reconciliation_results.append(f"Acknowledgment data parsed from {file}")

    # Display reconciliation results
    display_reconciliation_results(reconciliation_results)

if __name__ == "__main__":
    main()