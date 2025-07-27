#!/usr/bin/env python3
"""
Test script for IM Reconciliation Tool
Validates all components and provides a quick system check.
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from watchers.folder_monitor import monitor_folders
        print("  ✅ Folder monitor imported")
    except ImportError as e:
        print(f"  ❌ Folder monitor import failed: {e}")
        return False
    
    try:
        from utils.file_parsers import get_file_parser, parse_trade_extract
        print("  ✅ File parsers imported")
    except ImportError as e:
        print(f"  ❌ File parsers import failed: {e}")
        return False
    
    try:
        from parsers.reconciliation_engine import ReconciliationEngine
        print("  ✅ Reconciliation engine imported")
    except ImportError as e:
        print(f"  ❌ Reconciliation engine import failed: {e}")
        return False
    
    try:
        from rag.vector_store import IMReconciliationVectorStore
        print("  ✅ Vector store imported")
    except ImportError as e:
        print(f"  ❌ Vector store import failed: {e}")
        return False
    
    try:
        from chat.chat_interface import IMReconciliationChat
        print("  ✅ Chat interface imported")
    except ImportError as e:
        print(f"  ❌ Chat interface import failed: {e}")
        return False
    
    return True

def test_file_parsers():
    """Test file parsing functionality."""
    print("\n📄 Testing file parsers...")
    
    from utils.file_parsers import parse_trade_extract, parse_acknowledgment, parse_partial_transform_failure, parse_partial_ore
    
    # Test trade extract parsing
    try:
        sample_trade_data = """TradeID,Notional,Currency,Counterparty
T001,1000000,USD,ABC_BANK
T002,2500000,EUR,DEF_BANK"""
        
        with open('test_trade.csv', 'w') as f:
            f.write(sample_trade_data)
        
        result = parse_trade_extract('test_trade.csv')
        if result.get('trade_count') == 2:
            print("  ✅ Trade extract parsing works")
        else:
            print(f"  ❌ Trade extract parsing failed: {result}")
            return False
        
        os.remove('test_trade.csv')
        
    except Exception as e:
        print(f"  ❌ Trade extract parsing error: {e}")
        return False
    
    # Test acknowledgment parsing
    try:
        sample_ack_data = """TradeID,Status
T001,ACK
T002,NACK"""
        
        with open('test_ack.csv', 'w') as f:
            f.write(sample_ack_data)
        
        result = parse_acknowledgment('test_ack.csv')
        if result.get('ack_count') == 2:
            print("  ✅ Acknowledgment parsing works")
        else:
            print(f"  ❌ Acknowledgment parsing failed: {result}")
            return False
        
        os.remove('test_ack.csv')
        
    except Exception as e:
        print(f"  ❌ Acknowledgment parsing error: {e}")
        return False
    
    return True

def test_reconciliation_engine():
    """Test reconciliation engine functionality."""
    print("\n🔧 Testing reconciliation engine...")
    
    from parsers.reconciliation_engine import ReconciliationEngine
    
    try:
        engine = ReconciliationEngine()
        
        # Add some test data
        trade_data = {
            'file_type': 'trade_extract',
            'file_path': 'test_trade.csv',
            'trade_count': 2,
            'trades': [
                {'TradeID': 'T001', 'Notional': 1000000, 'Currency': 'USD', 'Counterparty': 'ABC_BANK'},
                {'TradeID': 'T002', 'Notional': 2500000, 'Currency': 'EUR', 'Counterparty': 'DEF_BANK'}
            ]
        }
        
        ack_data = {
            'file_type': 'acknowledgment',
            'file_path': 'test_ack.csv',
            'ack_count': 2,
            'acknowledgments': [
                {'TradeID': 'T001', 'Status': 'ACK'},
                {'TradeID': 'T002', 'Status': 'NACK'}
            ]
        }
        
        engine.add_file_data(trade_data)
        engine.add_file_data(ack_data)
        
        result = engine.reconcile_all()
        
        if result.get('summary', {}).get('total_trades_sent') == 2:
            print("  ✅ Reconciliation engine works")
        else:
            print(f"  ❌ Reconciliation engine failed: {result}")
            return False
        
    except Exception as e:
        print(f"  ❌ Reconciliation engine error: {e}")
        return False
    
    return True

def test_vector_store():
    """Test vector store functionality."""
    print("\n🗄️ Testing vector store...")
    
    try:
        from rag.vector_store import IMReconciliationVectorStore
        
        # Initialize vector store
        vector_store = IMReconciliationVectorStore(persist_directory="test_chroma_db")
        
        # Test adding data
        test_data = {
            'file_type': 'trade_extract',
            'file_path': 'test.csv',
            'trade_count': 1,
            'trades': [{'TradeID': 'T001'}]
        }
        
        doc_id = vector_store.add_file_data(test_data)
        if doc_id:
            print("  ✅ Vector store data addition works")
        else:
            print("  ❌ Vector store data addition failed")
            return False
        
        # Test querying
        results = vector_store.query_file_data("trade extract")
        if results:
            print("  ✅ Vector store querying works")
        else:
            print("  ❌ Vector store querying failed")
            return False
        
        # Clean up
        import shutil
        if os.path.exists("test_chroma_db"):
            shutil.rmtree("test_chroma_db")
        
    except Exception as e:
        print(f"  ❌ Vector store error: {e}")
        return False
    
    return True

def test_sample_data():
    """Test with sample data files."""
    print("\n📊 Testing with sample data...")
    
    try:
        # Check if sample data exists
        sample_files = [
            'sample_data/TRADE_EXTRACT_20250720.csv',
            'sample_data/ACK_20250720.csv',
            'sample_data/NACK_20250720.csv',
            'sample_data/PARTIAL_TRANSFORM_FAILURE_20250720.json',
            'sample_data/PARTIAL_ORE_20250720.csv'
        ]
        
        for file_path in sample_files:
            if os.path.exists(file_path):
                print(f"  ✅ {file_path} exists")
            else:
                print(f"  ❌ {file_path} missing")
                return False
        
        # Test parsing sample files
        from utils.file_parsers import get_file_parser
        
        for file_path in sample_files:
            parser = get_file_parser(file_path)
            if parser:
                try:
                    result = parser(file_path)
                    print(f"  ✅ {os.path.basename(file_path)} parsed successfully")
                except Exception as e:
                    print(f"  ❌ {os.path.basename(file_path)} parsing failed: {e}")
                    return False
            else:
                print(f"  ❌ No parser found for {file_path}")
                return False
        
    except Exception as e:
        print(f"  ❌ Sample data test error: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration system."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import Config
        
        # Test configuration validation
        errors = Config.validate_config()
        if not errors:
            print("  ✅ Configuration is valid")
        else:
            print(f"  ❌ Configuration errors: {errors}")
            return False
        
        # Test folder creation
        folders = Config.get_monitored_folders()
        for folder in folders:
            if os.path.exists(folder):
                print(f"  ✅ Folder {folder} exists")
            else:
                print(f"  ❌ Folder {folder} missing")
                return False
        
    except Exception as e:
        print(f"  ❌ Configuration test error: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧠 IM Reconciliation Tool - System Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Imports", test_imports),
        ("File Parsers", test_file_parsers),
        ("Reconciliation Engine", test_reconciliation_engine),
        ("Vector Store", test_vector_store),
        ("Sample Data", test_sample_data),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run main.py")
        print("2. Copy sample files to monitored folders")
        print("3. Start asking questions in the chat interface")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 