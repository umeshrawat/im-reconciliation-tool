import pandas as pd
import os
import json
from typing import List, Dict, Tuple, Any
import logging
from datetime import datetime
from utils.file_parsers import get_file_parser

logger = logging.getLogger(__name__)

class ReconciliationEngine:
    def __init__(self):
        self.trade_data = {}
        self.ack_data = {}
        self.error_data = {}
        self.reconciliation_history = []
    
    def add_file_data(self, parsed_data: Dict[str, Any]) -> None:
        """
        Add parsed file data to the reconciliation engine.
        """
        file_type = parsed_data.get('file_type')
        file_path = parsed_data.get('file_path')
        
        if 'error' in parsed_data:
            logger.error(f"File {file_path} has parsing errors: {parsed_data['error']}")
            return
        
        if file_type == 'trade_extract':
            self.trade_data[file_path] = parsed_data
        elif file_type == 'acknowledgment':
            self.ack_data[file_path] = parsed_data
        elif file_type in ['transform_failure', 'ore_error']:
            self.error_data[file_path] = parsed_data
        
        logger.info(f"Added {file_type} data from {file_path}")
    
    def reconcile_all(self) -> Dict[str, Any]:
        """
        Perform comprehensive reconciliation across all loaded data.
        """
        reconciliation_results = {
            'timestamp': datetime.now().isoformat(),
            'trade_files': list(self.trade_data.keys()),
            'ack_files': list(self.ack_data.keys()),
            'error_files': list(self.error_data.keys()),
            'summary': {},
            'discrepancies': [],
            'errors': []
        }
        
        # Process trade extracts
        total_trades_sent = 0
        all_trade_ids = set()
        
        for file_path, trade_data in self.trade_data.items():
            trades = trade_data.get('trades', [])
            total_trades_sent += len(trades)
            trade_ids = {trade.get('TradeID') for trade in trades if trade.get('TradeID')}
            all_trade_ids.update(trade_ids)
        
        # Process acknowledgments
        total_acks = 0
        total_nacks = 0
        acknowledged_trades = set()
        nacked_trades = set()
        
        for file_path, ack_data in self.ack_data.items():
            acks = ack_data.get('acknowledgments', [])
            total_acks += len([ack for ack in acks if ack.get('Status') == 'ACK'])
            total_nacks += len([ack for ack in acks if ack.get('Status') == 'NACK'])
            
            for ack in acks:
                trade_id = ack.get('TradeID')
                status = ack.get('Status')
                if trade_id:
                    if status == 'ACK':
                        acknowledged_trades.add(trade_id)
                    elif status == 'NACK':
                        nacked_trades.add(trade_id)
        
        # Find discrepancies
        missing_acks = all_trade_ids - acknowledged_trades - nacked_trades
        unexpected_acks = (acknowledged_trades | nacked_trades) - all_trade_ids
        
        # Process errors
        transform_errors = []
        ore_errors = []
        
        for file_path, error_data in self.error_data.items():
            if error_data.get('file_type') == 'transform_failure':
                transform_errors.extend(error_data.get('errors', []))
            elif error_data.get('file_type') == 'ore_error':
                ore_errors.extend(error_data.get('ore_errors', []))
        
        # Build summary
        reconciliation_results['summary'] = {
            'total_trades_sent': total_trades_sent,
            'total_acknowledgments': total_acks,
            'total_nacknowledgments': total_nacks,
            'missing_acknowledgments': len(missing_acks),
            'transform_errors': len(transform_errors),
            'ore_errors': len(ore_errors),
            'reconciliation_status': self._get_reconciliation_status(
                total_trades_sent, total_acks, total_nacks, len(missing_acks), len(transform_errors), len(ore_errors)
            )
        }
        
        # Build discrepancies list
        if missing_acks:
            reconciliation_results['discrepancies'].append({
                'type': 'missing_acknowledgments',
                'trade_ids': list(missing_acks),
                'count': len(missing_acks)
            })
        
        if unexpected_acks:
            reconciliation_results['discrepancies'].append({
                'type': 'unexpected_acknowledgments',
                'trade_ids': list(unexpected_acks),
                'count': len(unexpected_acks)
            })
        
        if transform_errors:
            reconciliation_results['errors'].append({
                'type': 'transform_failures',
                'errors': transform_errors,
                'count': len(transform_errors)
            })
        
        if ore_errors:
            reconciliation_results['errors'].append({
                'type': 'ore_errors',
                'errors': ore_errors,
                'count': len(ore_errors)
            })
        
        # Store in history
        self.reconciliation_history.append(reconciliation_results)
        
        return reconciliation_results
    
    def _get_reconciliation_status(self, trades_sent, acks, nacks, missing_acks, transform_errors, ore_errors):
        """
        Determine overall reconciliation status.
        """
        if trades_sent == 0:
            return "NO_TRADES"
        elif missing_acks == 0 and transform_errors == 0 and ore_errors == 0:
            return "FULLY_RECONCILED"
        elif missing_acks > 0:
            return "MISSING_ACKNOWLEDGMENTS"
        elif transform_errors > 0:
            return "TRANSFORM_ERRORS"
        elif ore_errors > 0:
            return "ORE_ERRORS"
        else:
            return "PARTIALLY_RECONCILED"
    
    def get_reconciliation_history(self) -> List[Dict[str, Any]]:
        """
        Get all reconciliation results.
        """
        return self.reconciliation_history
    
    def get_latest_reconciliation(self) -> Dict[str, Any]:
        """
        Get the most recent reconciliation result.
        """
        if self.reconciliation_history:
            return self.reconciliation_history[-1]
        return {}
    
    def clear_data(self) -> None:
        """
        Clear all loaded data.
        """
        self.trade_data.clear()
        self.ack_data.clear()
        self.error_data.clear()
        logger.info("Cleared all reconciliation data")

def process_file_for_reconciliation(file_path: str, reconciliation_engine: ReconciliationEngine) -> Dict[str, Any]:
    """
    Process a single file for reconciliation.
    """
    try:
        # Get appropriate parser
        parser = get_file_parser(file_path)
        if not parser:
            return {'error': f'No parser found for file: {file_path}'}
        
        # Parse the file
        parsed_data = parser(file_path)
        
        # Add to reconciliation engine
        reconciliation_engine.add_file_data(parsed_data)
        
        # Perform reconciliation
        reconciliation_result = reconciliation_engine.reconcile_all()
        
        return {
            'file_path': file_path,
            'parsed_data': parsed_data,
            'reconciliation_result': reconciliation_result
        }
    
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return {'error': str(e), 'file_path': file_path}