# 🧠 Intelligent IM Reconciliation Tool

A comprehensive, air-gapped enterprise solution for monitoring trade file flows, performing reconciliation, and providing intelligent chat-based querying using RAG (Retrieval-Augmented Generation).

## 🎯 Overview

This tool provides a complete IM (Initial Margin) reconciliation system that:

- **Monitors** three critical folders for trade files
- **Parses** and **reconciles** trade data automatically
- **Stores** all data in a local vector database for semantic search
- **Provides** an intelligent chat interface for querying reconciliation status
- **Learns** over time to provide better insights

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Folder        │    │   File          │    │   RAG Vector    │
│   Monitor       │───▶│   Parser        │───▶│   Store         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Reconciliation│    │   Chat          │    │   Local         │
│   Engine        │    │   Interface     │    │   Embeddings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Monitored Folders

- **`outgoing/`** - Trade extract files (`TRADE_EXTRACT_*.csv`)
- **`incoming/out/`** - Acknowledgment files (`ACK_*.csv`, `NACK_*.csv`)
- **`incoming/error/`** - Error files (`PARTIAL_TRANSFORM_FAILURE_*.json`, `PARTIAL_ORE_*.csv`)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd im-reconciliation-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Create configuration file
python config.py
```

This creates a `.env` file with default settings. Customize as needed:

```env
# Folder paths
OUTGOING_FOLDER=outgoing/
INCOMING_ACK_FOLDER=incoming/out/
INCOMING_ERROR_FOLDER=incoming/error/

# RAG settings
RAG_PERSIST_DIRECTORY=rag/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Monitoring settings
DEBOUNCE_TIME=2.0
MONITORING_ENABLED=true
```

### 3. Run the Application

```bash
# Start the Streamlit interface
streamlit run main.py
```

The application will:
- Create necessary folders
- Start monitoring for new files
- Process existing files
- Launch the chat interface

## 💬 Chat Interface

The chat interface supports natural language queries about your reconciliation status:

### Example Queries

- **"How many trades failed today?"**
- **"Show missing trade confirmations from yesterday"**
- **"What's the total trade count from ACK file vs outgoing?"**
- **"What's the latest reconciliation status?"**
- **"List trades with transform errors"**
- **"Show ORE reconciliation errors"**

### Features

- **Multi-turn conversations** with context memory
- **Real-time file monitoring** with automatic processing
- **Semantic search** across all reconciliation data
- **Structured data display** with expandable details
- **Example queries** for quick access

## 📊 File Formats

### Trade Extract Files (`TRADE_EXTRACT_*.csv`)
```csv
TradeID,Notional,Currency,Counterparty
T001,1000000,USD,ABC_BANK
T002,2500000,EUR,DEF_BANK
```

### Acknowledgment Files (`ACK_*.csv`, `NACK_*.csv`)
```csv
TradeID,Status
T001,ACK
T002,NACK
```

### Transform Failure Files (`PARTIAL_TRANSFORM_FAILURE_*.json`)
```json
{
  "file_name": "TRADE_EXTRACT_20250720.csv",
  "errors": [
    {"line": 4, "error": "Missing trade ID"},
    {"line": 8, "error": "Invalid counterparty code"}
  ]
}
```

### ORE Error Files (`PARTIAL_ORE_*.csv`)
```csv
TradeID,Issue
T001,Notional mismatch
T004,Currency mismatch
```

## 🔧 Technical Details

### Components

1. **Folder Monitor** (`watchers/folder_monitor.py`)
   - Uses `watchdog` for real-time file monitoring
   - Implements debouncing to prevent duplicate processing
   - Supports callback-based file processing

2. **File Parsers** (`utils/file_parsers.py`)
   - Robust CSV and JSON parsing
   - Error handling and validation
   - Structured output for reconciliation

3. **Reconciliation Engine** (`parsers/reconciliation_engine.py`)
   - Compares trade extracts with acknowledgments
   - Identifies discrepancies and errors
   - Provides comprehensive reconciliation summaries

4. **RAG Vector Store** (`rag/vector_store.py`)
   - Uses ChromaDB for local vector storage
   - Sentence transformers for embeddings
   - Semantic search across all data

5. **Chat Interface** (`chat/chat_interface.py`)
   - Streamlit-based UI with chat functionality
   - Multi-turn conversation support
   - Integration with RAG for intelligent responses

### Privacy & Security

- **100% Local** - No external API calls
- **Air-gapped** - Works in secure enterprise networks
- **No telemetry** - ChromaDB configured for privacy
- **Configurable** - All settings via environment variables

## 📈 Reconciliation Logic

The system performs comprehensive reconciliation:

1. **Trade Count Matching**
   - Compares outgoing trades vs acknowledgments
   - Identifies missing confirmations

2. **Error Detection**
   - Transform failures (parsing issues)
   - ORE errors (reconciliation mismatches)
   - NACK trades (rejected by counterparty)

3. **Status Classification**
   - `FULLY_RECONCILED` - All trades accounted for
   - `MISSING_ACKNOWLEDGMENTS` - Pending confirmations
   - `TRANSFORM_ERRORS` - File parsing issues
   - `ORE_ERRORS` - Reconciliation mismatches

## 🧪 Testing

### Sample Data

The `sample_data/` folder contains test files:

```bash
# Copy sample files to monitored folders
cp sample_data/TRADE_EXTRACT_*.csv outgoing/
cp sample_data/ACK_*.csv incoming/out/
cp sample_data/NACK_*.csv incoming/out/
cp sample_data/PARTIAL_*.json incoming/error/
cp sample_data/PARTIAL_ORE_*.csv incoming/error/
```

### CLI Mode

For testing without the UI:

```bash
python main.py
```

## 📝 Logging

Logs are written to `im_reconciliation.log` with detailed information about:

- File processing events
- Reconciliation results
- Error conditions
- System status

## 🔄 Continuous Learning

The system improves over time by:

- **Storing** all reconciliation results in the vector database
- **Learning** from historical patterns
- **Providing** better context for queries
- **Building** comprehensive knowledge base

## 🛠️ Development

### Project Structure

```
im-reconciliation-tool/
├── main.py                 # Main orchestration
├── config.py              # Configuration management
├── requirements.txt       # Dependencies
├── README.md             # This file
├── watchers/             # Folder monitoring
├── parsers/              # File parsing & reconciliation
├── rag/                  # Vector store & embeddings
├── chat/                 # Chat interface
├── utils/                # Utilities
├── sample_data/          # Test files
└── notebooks/            # Development notebooks
```

### Adding New File Types

1. Add parser function in `utils/file_parsers.py`
2. Update `get_file_parser()` function
3. Add to reconciliation logic in `parsers/reconciliation_engine.py`
4. Update vector store handling in `rag/vector_store.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the logs in `im_reconciliation.log`
2. Review the configuration in `.env`
3. Ensure all dependencies are installed
4. Verify folder permissions

## 🔮 Future Enhancements

- **Advanced Analytics** - Trend analysis and reporting
- **Alert System** - Email/Slack notifications for critical issues
- **API Endpoints** - REST API for integration
- **Dashboard** - Real-time metrics and visualizations
- **Machine Learning** - Predictive reconciliation insights