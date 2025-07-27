import pandas as pd
import json
import os
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def parse_trade_extract(file_path: str) -> Dict[str, Any]:
    """
    Parse trade extract CSV files.
    
    Expected format:
    TradeID,Notional,Currency,Counterparty
    T001,1000000,USD,ABC_BANK
    """
    try:
        df = pd.read_csv(file_path)
        
        # Clean column names (remove whitespace)
        df.columns = df.columns.str.strip()
        
        required_columns = ['TradeID', 'Notional', 'Currency', 'Counterparty']
        
        # Validate required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Convert to structured format
        trades = df.to_dict('records')
        
        return {
            'file_type': 'trade_extract',
            'file_path': file_path,
            'trade_count': len(trades),
            'trades': trades,
            'summary': {
                'total_notional': df['Notional'].sum() if 'Notional' in df.columns else 0,
                'currencies': df['Currency'].unique().tolist() if 'Currency' in df.columns else [],
                'counterparties': df['Counterparty'].unique().tolist() if 'Counterparty' in df.columns else []
            }
        }
    except Exception as e:
        logger.error(f"Error parsing trade extract file {file_path}: {e}")
        return {
            'file_type': 'trade_extract',
            'file_path': file_path,
            'error': str(e),
            'trade_count': 0,
            'trades': [],
            'summary': {}
        }

def parse_acknowledgment(file_path: str) -> Dict[str, Any]:
    """
    Parse acknowledgment CSV files.
    
    Expected format:
    TradeID,Status
    T001,ACK
    """
    try:
        df = pd.read_csv(file_path)
        
        # Clean column names (remove whitespace)
        df.columns = df.columns.str.strip()
        
        required_columns = ['TradeID', 'Status']
        
        # Validate required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Convert to structured format
        acknowledgments = df.to_dict('records')
        
        return {
            'file_type': 'acknowledgment',
            'file_path': file_path,
            'ack_count': len(acknowledgments),
            'acknowledgments': acknowledgments,
            'summary': {
                'ack_trades': df[df['Status'] == 'ACK']['TradeID'].tolist(),
                'nack_trades': df[df['Status'] == 'NACK']['TradeID'].tolist() if 'NACK' in df['Status'].values else []
            }
        }
    except Exception as e:
        logger.error(f"Error parsing acknowledgment file {file_path}: {e}")
        return {
            'file_type': 'acknowledgment',
            'file_path': file_path,
            'error': str(e),
            'ack_count': 0,
            'acknowledgments': [],
            'summary': {}
        }

def parse_nacknowledgment(file_path: str) -> Dict[str, Any]:
    """
    Parse nacknowledgment CSV files (same format as acknowledgment).
    """
    return parse_acknowledgment(file_path)

def parse_partial_transform_failure(file_path: str) -> Dict[str, Any]:
    """
    Parse JSON transform failure files.
    
    Expected format:
    {
      "file_name": "TRADE_EXTRACT_20250720.csv",
      "errors": [
        {"line": 4, "error": "Missing trade ID"},
        {"line": 8, "error": "Invalid counterparty code"}
      ]
    }
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return {
            'file_type': 'transform_failure',
            'file_path': file_path,
            'source_file': data.get('file_name', ''),
            'error_count': len(data.get('errors', [])),
            'errors': data.get('errors', []),
            'summary': {
                'failed_lines': [error.get('line') for error in data.get('errors', [])],
                'error_types': list(set([error.get('error', '').split(':')[0] for error in data.get('errors', [])]))
            }
        }
    except Exception as e:
        logger.error(f"Error parsing transform failure file {file_path}: {e}")
        return {
            'file_type': 'transform_failure',
            'file_path': file_path,
            'error': str(e),
            'error_count': 0,
            'errors': [],
            'summary': {}
        }

def parse_partial_ore(file_path: str) -> Dict[str, Any]:
    """
    Parse ORE reconciliation error CSV files.
    
    Expected format:
    TradeID,Issue
    T001,Notional mismatch
    """
    try:
        df = pd.read_csv(file_path)
        required_columns = ['TradeID', 'Issue']
        
        # Validate required columns
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Convert to structured format
        ore_errors = df.to_dict('records')
        
        return {
            'file_type': 'ore_error',
            'file_path': file_path,
            'error_count': len(ore_errors),
            'ore_errors': ore_errors,
            'summary': {
                'affected_trades': df['TradeID'].tolist(),
                'issue_types': df['Issue'].unique().tolist()
            }
        }
    except Exception as e:
        logger.error(f"Error parsing ORE error file {file_path}: {e}")
        return {
            'file_type': 'ore_error',
            'file_path': file_path,
            'error': str(e),
            'error_count': 0,
            'ore_errors': [],
            'summary': {}
        }

def get_file_parser(file_path: str) -> Optional[callable]:
    """
    Determine the appropriate parser based on file path and content.
    """
    filename = os.path.basename(file_path).lower()
    
    if 'trade_extract' in filename and file_path.endswith('.csv'):
        return parse_trade_extract
    elif ('ack' in filename or 'nack' in filename) and file_path.endswith('.csv'):
        return parse_acknowledgment
    elif 'transform_failure' in filename and file_path.endswith('.json'):
        return parse_partial_transform_failure
    elif 'ore' in filename and file_path.endswith('.csv'):
        return parse_partial_ore
    else:
        logger.warning(f"No parser found for file: {file_path}")
        return None