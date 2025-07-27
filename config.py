import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for IM Reconciliation Tool."""
    
    # Folder paths
    OUTGOING_FOLDER = os.getenv("OUTGOING_FOLDER", "outgoing/")
    INCOMING_ACK_FOLDER = os.getenv("INCOMING_ACK_FOLDER", "incoming/out/")
    INCOMING_ERROR_FOLDER = os.getenv("INCOMING_ERROR_FOLDER", "incoming/error/")
    
    # RAG settings
    RAG_PERSIST_DIRECTORY = os.getenv("RAG_PERSIST_DIRECTORY", "rag/chroma_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Monitoring settings
    DEBOUNCE_TIME = float(os.getenv("DEBOUNCE_TIME", "2.0"))
    MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "im_reconciliation.log")
    
    # Chat settings
    CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "100"))
    AUTO_REFRESH_INTERVAL = int(os.getenv("AUTO_REFRESH_INTERVAL", "2000"))
    
    # File processing settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    SUPPORTED_EXTENSIONS = {
        'csv': ['.csv'],
        'json': ['.json']
    }
    
    # Privacy settings
    ANONYMIZE_TELEMETRY = os.getenv("ANONYMIZE_TELEMETRY", "false").lower() == "true"
    ENABLE_EXTERNAL_CALLS = os.getenv("ENABLE_EXTERNAL_CALLS", "false").lower() == "true"
    
    @classmethod
    def get_monitored_folders(cls):
        """Get list of monitored folders."""
        return [
            cls.OUTGOING_FOLDER,
            cls.INCOMING_ACK_FOLDER,
            cls.INCOMING_ERROR_FOLDER
        ]
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings."""
        errors = []
        
        # Check if folders exist or can be created
        for folder in cls.get_monitored_folders():
            if not os.path.exists(folder):
                try:
                    os.makedirs(folder, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create folder {folder}: {e}")
        
        # Validate settings
        if cls.DEBOUNCE_TIME < 0:
            errors.append("DEBOUNCE_TIME must be positive")
        
        if cls.CHAT_HISTORY_LIMIT < 1:
            errors.append("CHAT_HISTORY_LIMIT must be at least 1")
        
        if cls.MAX_FILE_SIZE_MB < 1:
            errors.append("MAX_FILE_SIZE_MB must be at least 1")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Print current configuration."""
        print("IM Reconciliation Tool Configuration:")
        print(f"  Outgoing Folder: {cls.OUTGOING_FOLDER}")
        print(f"  Incoming ACK Folder: {cls.INCOMING_ACK_FOLDER}")
        print(f"  Incoming Error Folder: {cls.INCOMING_ERROR_FOLDER}")
        print(f"  RAG Persist Directory: {cls.RAG_PERSIST_DIRECTORY}")
        print(f"  Embedding Model: {cls.EMBEDDING_MODEL}")
        print(f"  Debounce Time: {cls.DEBOUNCE_TIME}s")
        print(f"  Monitoring Enabled: {cls.MONITORING_ENABLED}")
        print(f"  Log Level: {cls.LOG_LEVEL}")
        print(f"  Log File: {cls.LOG_FILE}")
        print(f"  Chat History Limit: {cls.CHAT_HISTORY_LIMIT}")
        print(f"  Auto Refresh Interval: {cls.AUTO_REFRESH_INTERVAL}ms")
        print(f"  Max File Size: {cls.MAX_FILE_SIZE_MB}MB")
        print(f"  Anonymize Telemetry: {cls.ANONYMIZE_TELEMETRY}")
        print(f"  Enable External Calls: {cls.ENABLE_EXTERNAL_CALLS}")

# Create .env template if it doesn't exist
def create_env_template():
    """Create a .env template file."""
    env_template = """# IM Reconciliation Tool Environment Variables

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

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=im_reconciliation.log

# Chat settings
CHAT_HISTORY_LIMIT=100
AUTO_REFRESH_INTERVAL=2000

# File processing settings
MAX_FILE_SIZE_MB=100

# Privacy settings
ANONYMIZE_TELEMETRY=false
ENABLE_EXTERNAL_CALLS=false
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_template)
        print("Created .env template file")

if __name__ == "__main__":
    # Create .env template
    create_env_template()
    
    # Print configuration
    Config.print_config()
    
    # Validate configuration
    errors = Config.validate_config()
    if errors:
        print("\nConfiguration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\nConfiguration is valid!") 