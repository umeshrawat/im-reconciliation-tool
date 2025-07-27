import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class IMReconciliationVectorStore:
    def __init__(self, persist_directory: str = "rag/chroma_db"):
        """
        Initialize the vector store for IM reconciliation data.
        
        Args:
            persist_directory: Directory to persist the ChromaDB data
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False  # Ensure no external calls
        ))
        
        # Create collections for different types of data
        self.reconciliation_collection = self.client.get_or_create_collection(
            "im_reconciliation_results",
            metadata={"description": "Reconciliation results and summaries"}
        )
        
        self.file_data_collection = self.client.get_or_create_collection(
            "im_file_data",
            metadata={"description": "Parsed file data and metadata"}
        )
        
        self.error_collection = self.client.get_or_create_collection(
            "im_errors",
            metadata={"description": "Error reports and issues"}
        )
        
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded sentence transformer model")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.embedding_model = None
    
    def add_reconciliation_result(self, reconciliation_data: Dict[str, Any]) -> str:
        """
        Add a reconciliation result to the vector store.
        
        Args:
            reconciliation_data: Reconciliation result dictionary
            
        Returns:
            Document ID
        """
        try:
            # Create a text representation of the reconciliation result
            summary = reconciliation_data.get('summary', {})
            text_content = f"""
            Reconciliation Status: {summary.get('reconciliation_status', 'UNKNOWN')}
            Total Trades Sent: {summary.get('total_trades_sent', 0)}
            Total Acknowledgments: {summary.get('total_acknowledgments', 0)}
            Total Nacknowledgments: {summary.get('total_nacknowledgments', 0)}
            Missing Acknowledgments: {summary.get('missing_acknowledgments', 0)}
            Transform Errors: {summary.get('transform_errors', 0)}
            ORE Errors: {summary.get('ore_errors', 0)}
            """
            
            # Add discrepancy details
            discrepancies = reconciliation_data.get('discrepancies', [])
            for disc in discrepancies:
                text_content += f"\nDiscrepancy: {disc['type']} - {disc['count']} items"
            
            # Add error details
            errors = reconciliation_data.get('errors', [])
            for error in errors:
                text_content += f"\nError: {error['type']} - {error['count']} items"
            
            # Create metadata
            metadata = {
                'timestamp': reconciliation_data.get('timestamp', datetime.now().isoformat()),
                'type': 'reconciliation_result',
                'status': summary.get('reconciliation_status', 'UNKNOWN'),
                'trade_files': len(reconciliation_data.get('trade_files', [])),
                'ack_files': len(reconciliation_data.get('ack_files', [])),
                'error_files': len(reconciliation_data.get('error_files', []))
            }
            
            # Generate document ID
            doc_id = f"reconciliation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Add to collection
            self.reconciliation_collection.add(
                documents=[text_content],
                ids=[doc_id],
                metadatas=[metadata]
            )
            
            logger.info(f"Added reconciliation result: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding reconciliation result: {e}")
            return None
    
    def add_file_data(self, file_data: Dict[str, Any]) -> str:
        """
        Add parsed file data to the vector store.
        
        Args:
            file_data: Parsed file data dictionary
            
        Returns:
            Document ID
        """
        try:
            file_type = file_data.get('file_type', 'unknown')
            file_path = file_data.get('file_path', '')
            
            # Create text content based on file type
            if file_type == 'trade_extract':
                summary = file_data.get('summary', {})
                text_content = f"""
                Trade Extract File: {os.path.basename(file_path)}
                Total Trades: {file_data.get('trade_count', 0)}
                Total Notional: {summary.get('total_notional', 0)}
                Currencies: {', '.join(summary.get('currencies', []))}
                Counterparties: {', '.join(summary.get('counterparties', []))}
                """
            elif file_type == 'acknowledgment':
                summary = file_data.get('summary', {})
                text_content = f"""
                Acknowledgment File: {os.path.basename(file_path)}
                Total Acknowledgments: {file_data.get('ack_count', 0)}
                ACK Trades: {len(summary.get('ack_trades', []))}
                NACK Trades: {len(summary.get('nack_trades', []))}
                """
            elif file_type == 'transform_failure':
                text_content = f"""
                Transform Failure File: {os.path.basename(file_path)}
                Source File: {file_data.get('source_file', '')}
                Error Count: {file_data.get('error_count', 0)}
                """
            elif file_type == 'ore_error':
                summary = file_data.get('summary', {})
                text_content = f"""
                ORE Error File: {os.path.basename(file_path)}
                Error Count: {file_data.get('error_count', 0)}
                Affected Trades: {len(summary.get('affected_trades', []))}
                Issue Types: {', '.join(summary.get('issue_types', []))}
                """
            else:
                text_content = f"File: {os.path.basename(file_path)} - Type: {file_type}"
            
            # Create metadata
            metadata = {
                'file_type': file_type,
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'type': 'file_data'
            }
            
            # Generate document ID
            doc_id = f"file_{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Add to collection
            self.file_data_collection.add(
                documents=[text_content],
                ids=[doc_id],
                metadatas=[metadata]
            )
            
            logger.info(f"Added file data: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error adding file data: {e}")
            return None
    
    def query_reconciliation_data(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query reconciliation results.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            
        Returns:
            List of query results
        """
        try:
            results = self.reconciliation_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            return [
                {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                for i in range(len(results['ids'][0]))
            ]
        except Exception as e:
            logger.error(f"Error querying reconciliation data: {e}")
            return []
    
    def query_file_data(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query file data.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            
        Returns:
            List of query results
        """
        try:
            results = self.file_data_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            return [
                {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                for i in range(len(results['ids'][0]))
            ]
        except Exception as e:
            logger.error(f"Error querying file data: {e}")
            return []
    
    def query_all(self, query_text: str, n_results: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Query all collections.
        
        Args:
            query_text: Query text
            n_results: Number of results per collection
            
        Returns:
            Dictionary with results from each collection
        """
        return {
            'reconciliation_results': self.query_reconciliation_data(query_text, n_results),
            'file_data': self.query_file_data(query_text, n_results),
            'errors': self.query_error_data(query_text, n_results)
        }
    
    def query_error_data(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Query error data.
        
        Args:
            query_text: Query text
            n_results: Number of results to return
            
        Returns:
            List of query results
        """
        try:
            results = self.error_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            return [
                {
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                for i in range(len(results['ids'][0]))
            ]
        except Exception as e:
            logger.error(f"Error querying error data: {e}")
            return []
    
    def persist(self) -> None:
        """
        Persist the database to disk.
        """
        try:
            # ChromaDB automatically persists when using persist_directory
            # No need to call persist() method in newer versions
            logger.info("Vector store data is automatically persisted")
        except Exception as e:
            logger.error(f"Error persisting vector store: {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collections.
        """
        try:
            return {
                'reconciliation_results': self.reconciliation_collection.count(),
                'file_data': self.file_data_collection.count(),
                'errors': self.error_collection.count(),
                'total_documents': (
                    self.reconciliation_collection.count() +
                    self.file_data_collection.count() +
                    self.error_collection.count()
                )
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

# Global instance
vector_store = IMReconciliationVectorStore()

def add_reconciliation_result(reconciliation_data: Dict[str, Any]) -> str:
    """Add reconciliation result to vector store."""
    return vector_store.add_reconciliation_result(reconciliation_data)

def add_file_data(file_data: Dict[str, Any]) -> str:
    """Add file data to vector store."""
    return vector_store.add_file_data(file_data)

def query_reconciliation_data(query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """Query reconciliation data."""
    return vector_store.query_reconciliation_data(query_text, n_results)

def query_file_data(query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """Query file data."""
    return vector_store.query_file_data(query_text, n_results)

def query_all(query_text: str, n_results: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """Query all collections."""
    return vector_store.query_all(query_text, n_results)

def persist_vector_store() -> None:
    """Persist vector store to disk."""
    vector_store.persist()

def get_vector_store_stats() -> Dict[str, Any]:
    """Get vector store statistics."""
    return vector_store.get_collection_stats() 