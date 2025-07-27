import streamlit as st
import os
import json
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
from rag.vector_store import query_all, get_vector_store_stats
from parsers.reconciliation_engine import ReconciliationEngine
from utils.file_parsers import get_file_parser

logger = logging.getLogger(__name__)

class IMReconciliationChat:
    def __init__(self):
        self.reconciliation_engine = ReconciliationEngine()
        self.chat_history = []
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state for chat."""
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        if 'reconciliation_engine' not in st.session_state:
            st.session_state.reconciliation_engine = self.reconciliation_engine
        
        if 'vector_store_stats' not in st.session_state:
            st.session_state.vector_store_stats = get_vector_store_stats()
    
    def display_header(self):
        """Display the chat interface header."""
        st.title("🧠 Intelligent IM Reconciliation Tool")
        st.markdown("Ask questions about your trade reconciliation status, file processing, and error reports.")
        
        # Display vector store stats
        stats = get_vector_store_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Reconciliation Results", stats.get('reconciliation_results', 0))
        with col2:
            st.metric("File Data", stats.get('file_data', 0))
        with col3:
            st.metric("Error Reports", stats.get('errors', 0))
        with col4:
            st.metric("Total Documents", stats.get('total_documents', 0))
    
    def display_chat_messages(self):
        """Display chat message history."""
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display additional data if available
                if "data" in message:
                    st.json(message["data"])
    
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Process user query and return response.
        
        Args:
            user_query: User's question
            
        Returns:
            Response dictionary with answer and data
        """
        query_lower = user_query.lower()
        
        # Handle specific query types
        if "how many trades failed today" in query_lower or "trades failed today" in query_lower:
            return self.handle_failed_trades_query(user_query)
        
        elif "missing trade confirmations" in query_lower or "missing acks" in query_lower:
            return self.handle_missing_confirmations_query(user_query)
        
        elif "total trade count" in query_lower or "ack vs outgoing" in query_lower:
            return self.handle_trade_count_comparison_query(user_query)
        
        elif "reconciliation status" in query_lower or "latest status" in query_lower:
            return self.handle_reconciliation_status_query(user_query)
        
        elif "transform errors" in query_lower or "transformation failures" in query_lower:
            return self.handle_transform_errors_query(user_query)
        
        elif "ore errors" in query_lower or "reconciliation errors" in query_lower:
            return self.handle_ore_errors_query(user_query)
        
        else:
            # Generic RAG query
            return self.handle_generic_query(user_query)
    
    def handle_failed_trades_query(self, query: str) -> Dict[str, Any]:
        """Handle queries about failed trades."""
        try:
            # Query vector store for recent reconciliation results
            results = query_all("failed trades today reconciliation status", n_results=3)
            
            response = "Based on the latest reconciliation data:\n\n"
            data = []
            
            for result_type, result_list in results.items():
                for result in result_list:
                    if "FAILED" in result['document'] or "ERROR" in result['document']:
                        response += f"**{result_type.replace('_', ' ').title()}:**\n"
                        response += result['document'] + "\n\n"
                        data.append({
                            'type': result_type,
                            'content': result['document'],
                            'metadata': result['metadata']
                        })
            
            if not data:
                response = "No failed trades found in recent data. All reconciliations appear to be successful."
            
            return {
                'answer': response,
                'data': data,
                'query_type': 'failed_trades'
            }
        
        except Exception as e:
            logger.error(f"Error handling failed trades query: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'data': [],
                'query_type': 'error'
            }
    
    def handle_missing_confirmations_query(self, query: str) -> Dict[str, Any]:
        """Handle queries about missing trade confirmations."""
        try:
            # Query for missing acknowledgments
            results = query_all("missing acknowledgments trade confirmations", n_results=5)
            
            response = "Missing trade confirmations:\n\n"
            data = []
            
            for result_type, result_list in results.items():
                for result in result_list:
                    if "missing" in result['document'].lower():
                        response += f"**{result_type.replace('_', ' ').title()}:**\n"
                        response += result['document'] + "\n\n"
                        data.append({
                            'type': result_type,
                            'content': result['document'],
                            'metadata': result['metadata']
                        })
            
            if not data:
                response = "No missing trade confirmations found. All trades appear to be acknowledged."
            
            return {
                'answer': response,
                'data': data,
                'query_type': 'missing_confirmations'
            }
        
        except Exception as e:
            logger.error(f"Error handling missing confirmations query: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'data': [],
                'query_type': 'error'
            }
    
    def handle_trade_count_comparison_query(self, query: str) -> Dict[str, Any]:
        """Handle queries about trade count comparisons."""
        try:
            # Query for trade count information
            results = query_all("total trades sent acknowledgments count comparison", n_results=5)
            
            response = "Trade Count Comparison:\n\n"
            data = []
            
            for result_type, result_list in results.items():
                for result in result_list:
                    if any(keyword in result['document'].lower() for keyword in ['total', 'count', 'trades', 'ack']):
                        response += f"**{result_type.replace('_', ' ').title()}:**\n"
                        response += result['document'] + "\n\n"
                        data.append({
                            'type': result_type,
                            'content': result['document'],
                            'metadata': result['metadata']
                        })
            
            if not data:
                response = "No trade count data available. Please ensure files have been processed."
            
            return {
                'answer': response,
                'data': data,
                'query_type': 'trade_count_comparison'
            }
        
        except Exception as e:
            logger.error(f"Error handling trade count query: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'data': [],
                'query_type': 'error'
            }
    
    def handle_reconciliation_status_query(self, query: str) -> Dict[str, Any]:
        """Handle queries about reconciliation status."""
        try:
            # Query for latest reconciliation status
            results = query_all("reconciliation status latest", n_results=3)
            
            response = "Latest Reconciliation Status:\n\n"
            data = []
            
            for result_type, result_list in results.items():
                for result in result_list:
                    if "reconciliation" in result['document'].lower():
                        response += f"**{result_type.replace('_', ' ').title()}:**\n"
                        response += result['document'] + "\n\n"
                        data.append({
                            'type': result_type,
                            'content': result['document'],
                            'metadata': result['metadata']
                        })
            
            if not data:
                response = "No recent reconciliation data available. Please ensure files have been processed."
            
            return {
                'answer': response,
                'data': data,
                'query_type': 'reconciliation_status'
            }
        
        except Exception as e:
            logger.error(f"Error handling reconciliation status query: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'data': [],
                'query_type': 'error'
            }
    
    def handle_transform_errors_query(self, query: str) -> Dict[str, Any]:
        """Handle queries about transform errors."""
        try:
            # Query for transform errors
            results = query_all("transform failure errors", n_results=5)
            
            response = "Transform Errors:\n\n"
            data = []
            
            for result_type, result_list in results.items():
                for result in result_list:
                    if "transform" in result['document'].lower():
                        response += f"**{result_type.replace('_', ' ').title()}:**\n"
                        response += result['document'] + "\n\n"
                        data.append({
                            'type': result_type,
                            'content': result['document'],
                            'metadata': result['metadata']
                        })
            
            if not data:
                response = "No transform errors found. All files appear to have been processed successfully."
            
            return {
                'answer': response,
                'data': data,
                'query_type': 'transform_errors'
            }
        
        except Exception as e:
            logger.error(f"Error handling transform errors query: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'data': [],
                'query_type': 'error'
            }
    
    def handle_ore_errors_query(self, query: str) -> Dict[str, Any]:
        """Handle queries about ORE errors."""
        try:
            # Query for ORE errors
            results = query_all("ore error reconciliation issues", n_results=5)
            
            response = "ORE Errors:\n\n"
            data = []
            
            for result_type, result_list in results.items():
                for result in result_list:
                    if "ore" in result['document'].lower():
                        response += f"**{result_type.replace('_', ' ').title()}:**\n"
                        response += result['document'] + "\n\n"
                        data.append({
                            'type': result_type,
                            'content': result['document'],
                            'metadata': result['metadata']
                        })
            
            if not data:
                response = "No ORE errors found. All reconciliations appear to be successful."
            
            return {
                'answer': response,
                'data': data,
                'query_type': 'ore_errors'
            }
        
        except Exception as e:
            logger.error(f"Error handling ORE errors query: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'data': [],
                'query_type': 'error'
            }
    
    def handle_generic_query(self, query: str) -> Dict[str, Any]:
        """Handle generic queries using RAG."""
        try:
            # Query all collections
            results = query_all(query, n_results=3)
            
            response = f"Results for: '{query}'\n\n"
            data = []
            
            for result_type, result_list in results.items():
                if result_list:
                    response += f"**{result_type.replace('_', ' ').title()}:**\n"
                    for result in result_list:
                        response += result['document'] + "\n\n"
                        data.append({
                            'type': result_type,
                            'content': result['document'],
                            'metadata': result['metadata']
                        })
            
            if not data:
                response = f"No relevant information found for: '{query}'. Try asking about specific reconciliation topics like failed trades, missing confirmations, or error reports."
            
            return {
                'answer': response,
                'data': data,
                'query_type': 'generic'
            }
        
        except Exception as e:
            logger.error(f"Error handling generic query: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'data': [],
                'query_type': 'error'
            }
    
    def add_message(self, role: str, content: str, data: List[Dict] = None):
        """Add a message to the chat history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if data:
            message["data"] = data
        
        st.session_state.chat_messages.append(message)
    
    def run(self):
        """Run the chat interface."""
        self.display_header()
        
        # Display chat messages
        self.display_chat_messages()
        
        # Chat input
        if prompt := st.chat_input("Ask about your reconciliation status..."):
            # Add user message
            self.add_message("user", prompt)
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process query and get response
            with st.chat_message("assistant"):
                with st.spinner("Processing your query..."):
                    response = self.process_query(prompt)
                    
                    # Display response
                    st.markdown(response['answer'])
                    
                    # Display data if available
                    if response.get('data'):
                        with st.expander("View detailed data"):
                            st.json(response['data'])
                
                # Add assistant message to history
                self.add_message("assistant", response['answer'], response.get('data'))
        
        # Sidebar with helpful queries
        with st.sidebar:
            st.header("💡 Example Queries")
            st.markdown("Try these questions:")
            
            example_queries = [
                "How many trades failed today?",
                "Show missing trade confirmations from yesterday",
                "What's the total trade count from ACK file vs outgoing?",
                "What's the latest reconciliation status?",
                "List trades with transform errors",
                "Show ORE reconciliation errors"
            ]
            
            for query in example_queries:
                if st.button(query, key=f"example_{query}"):
                    st.session_state.example_query = query
                    st.rerun()
            
            # File processing status
            st.header("📁 File Processing")
            monitored_folders = ["outgoing/", "incoming/out/", "incoming/error/"]
            
            for folder in monitored_folders:
                if os.path.exists(folder):
                    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
                    st.metric(folder, len(files))
                else:
                    st.metric(folder, "Not found")

def main():
    """Main function to run the chat interface."""
    chat = IMReconciliationChat()
    chat.run()

if __name__ == "__main__":
    main() 