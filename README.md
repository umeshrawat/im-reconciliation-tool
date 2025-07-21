# Intelligent IM Reconciliation Tool

## Overview
The Intelligent IM Reconciliation Tool is a lightweight Proof-of-Concept (POC) system designed to monitor trade file flows for Initial Margin (IM) processes. This tool reconciles trade extract files with acknowledgment and error files, providing users with real-time notifications and insights through a chat-based Streamlit UI.

## Features
- **Folder Monitoring**: Continuously monitors specified directories for new trade extract, acknowledgment, and error files.
- **Reconciliation Engine**: Matches trade counts between outgoing extracts and incoming acknowledgment/nacknowledgment files, and summarizes errors from transformation and reconciliation processes.
- **Chat-Based UI**: Notifies users of new files and displays reconciliation results in a user-friendly chatbot-style interface.

## Project Structure
```
im-reconciliation-tool
├── src
│   ├── folder_monitor.py        # Implements folder monitoring functionality
│   ├── reconciliation_engine.py  # Implements the reconciliation logic
│   ├── chat_ui.py               # Sets up the chat-based user interface
│   ├── utils
│   │   ├── file_parsers.py      # Utility functions for file parsing
│   │   └── state_cache.py       # Manages state caching
│   └── types
│       └── index.py             # Defines custom types and interfaces
├── sample_data
│   ├── TRADE_EXTRACT_sample.csv  # Sample trade extract data
│   ├── ACK_sample.csv            # Sample acknowledgment data
│   ├── NACK_sample.csv           # Sample nacknowledgment data
│   ├── PARTIAL_TRANSFORM_FAILURE_sample.json # Sample error data
│   └── PARTIAL_ORE_sample.csv    # Sample reconciliation error data
├── requirements.txt              # Project dependencies
├── .env.example                   # Example environment variables
├── README.md                      # Project documentation
└── main.py                       # Entry point for the application
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone https://github.com/your-repo/im-reconciliation-tool.git
   cd im-reconciliation-tool
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env` and update the file paths and credentials as necessary.

## Usage
To run the application, execute the following command:
```
python main.py
```

## Future Enhancements
- Integration of CRIF parsing and margin logic.
- Implementation of a lightweight RAG database or retrieval UI for FAQs.

## License
This project is licensed under the MIT License. See the LICENSE file for details.