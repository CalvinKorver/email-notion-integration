#!/usr/bin/env python3
"""
Test script using real credentials to verify end-to-end functionality.
"""

import logging
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from config import USER_CONFIG, validate_config, get_config_summary
from email_checker import test_gmail_connection
from notion_api import NotionClient
from scheduler import get_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_real_credentials():
    """Test with real credentials."""
    print("=" * 60)
    print("REAL CREDENTIALS TEST")
    print("=" * 60)
    
    # Test 1: Configuration validation
    print("\n1. Testing Configuration...")
    config_summary = get_config_summary()
    print(f"   User configured: {config_summary['user_configured']}")
    print(f"   Configuration errors: {len(config_summary['config_errors'])}")
    
    if config_summary['config_errors']:
        print("   Errors:")
        for error in config_summary['config_errors']:
            print(f"     - {error}")
    
    # Get the user configuration
    user = USER_CONFIG
    print(f"\n   User: {user['name']}")
    print(f"   Email: {user['email']}")
    print(f"   Gmail Label: {user['gmail_label']}")
    print(f"   Has App Password: {'Yes' if user['gmail_app_password'] != 'abcd efgh ijkl mnop' else 'No'}")
    print(f"   Has Notion Token: {'Yes' if not user['notion_token'].startswith('secret_token_placeholder') else 'No'}")
    
    # Test 2: Gmail Connection
    print("\n2. Testing Gmail Connection...")
    try:
        gmail_success = test_gmail_connection(
            user['email'], 
            user['gmail_app_password'], 
            user['gmail_label']
        )
        if gmail_success:
            print("   ✅ Gmail connection successful")
        else:
            print("   ❌ Gmail connection failed")
            return False
    except Exception as e:
        print(f"   ❌ Gmail connection error: {e}")
        return False
    
    # Test 3: Notion Connection
    print("\n3. Testing Notion Connection...")
    try:
        notion_client = NotionClient(user['notion_token'])
        notion_success = notion_client.test_connection()
        if notion_success:
            print("   ✅ Notion connection successful")
            
            # Test database access
            db_info = notion_client.get_database_info(user['notion_database_id'])
            if db_info:
                db_title = db_info.get('title', [{}])[0].get('plain_text', 'Unknown')
                print(f"   ✅ Database access successful: '{db_title}'")
            else:
                print("   ❌ Database access failed")
                return False
        else:
            print("   ❌ Notion connection failed")
            return False
    except Exception as e:
        print(f"   ❌ Notion connection error: {e}")
        return False
    
    # Test 4: Manual Email Check
    print("\n4. Testing Manual Email Check...")
    try:
        scheduler = get_scheduler()
        result = scheduler.run_manual_check()
        
        if result['success']:
            print("   ✅ Manual email check successful")
            print(f"   Result: {result['message']}")
        else:
            print("   ❌ Manual email check failed")
            print(f"   Error: {result['message']}")
            return False
    except Exception as e:
        print(f"   ❌ Manual email check error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL REAL CREDENTIALS TESTS PASSED!")
    print("Your email-to-Notion integration is working correctly!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_real_credentials()
    
    if success:
        print("\n🚀 Ready to start the Flask app with automatic email checking!")
        print("Run: python app.py")
    else:
        print("\n❌ Please fix the issues above before running the app.")