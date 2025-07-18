#!/usr/bin/env python3
"""
Test script to verify Notion connection using credentials from .env file.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_api import NotionClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_notion_connection():
    """Test the Notion connection with credentials from .env file."""
    
    # Get credentials from environment
    notion_token = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('DATABASE_ID')
    
    if not notion_token:
        print("❌ NOTION_API_KEY not found in .env file")
        return False
    
    if not database_id:
        print("❌ DATABASE_ID not found in .env file")
        return False
    
    print(f"Using Notion token: {notion_token[:20]}...")
    print(f"Using database ID: {database_id}")
    
    try:
        # Initialize the client
        client = NotionClient(notion_token)
        
        # Test connection
        print("\n🔍 Testing connection to Notion workspace...")
        if not client.test_connection():
            print("❌ Failed to connect to Notion workspace")
            print("Please check:")
            print("1. Your NOTION_API_KEY is correct")
            print("2. The integration has access to your workspace")
            return False
        
        print("✅ Successfully connected to Notion workspace")
        
        # Test database access
        print(f"\n🔍 Testing database access...")
        db_info = client.get_database_info(database_id)
        if not db_info:
            print("❌ Failed to access database")
            print("Please check:")
            print("1. Your DATABASE_ID is correct")
            print("2. The database has been shared with your integration")
            print("3. The database exists and is accessible")
            return False
        
        db_title = "Unknown"
        if db_info.get('title') and len(db_info['title']) > 0:
            db_title = db_info['title'][0].get('plain_text', 'Unknown')
        
        print(f"✅ Successfully accessed database: '{db_title}'")
        
        # Show database properties
        print(f"\n📋 Database properties:")
        if 'properties' in db_info:
            for prop_name, prop_info in db_info['properties'].items():
                prop_type = prop_info.get('type', 'unknown')
                print(f"  - {prop_name}: {prop_type}")
        
        # Test creating a test entry
        print(f"\n🔍 Testing entry creation...")
        sample_data = {
            "recruiter_name": "Test Recruiter",
            "recruiter_email": "test@example.com",
            "company": "Test Company",
            "position": "Software Engineer",
            "location": "Remote",
            "status": "Recruiter Screen",
            "date_received": datetime.now()
        }
        
        page_id = client.create_recruiter_entry(database_id, sample_data)
        if not page_id:
            print("❌ Failed to create test entry")
            print("This might be due to:")
            print("1. Missing required properties in the database")
            print("2. Incorrect property types")
            print("3. Insufficient permissions")
            return False
        
        print(f"✅ Successfully created test entry with ID: {page_id}")
        
        print("\n🎉 All tests passed! Your Notion integration is working correctly.")
        print("\nYou can now proceed with the full email processing pipeline.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("NOTION CONNECTION TEST")
    print("=" * 50)
    
    success = test_notion_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ CONNECTION TEST PASSED")
    else:
        print("❌ CONNECTION TEST FAILED")
        print("\nTroubleshooting tips:")
        print("1. Verify your Notion integration token is correct")
        print("2. Make sure your database is shared with the integration")
        print("3. Check that your database has the required properties:")
        print("   - Recruiter Name (Title)")
        print("   - Company (Text)")
        print("   - Position (Text)")
        print("   - Location (Text)")
        print("   - Status (Select)")
        print("   - Email (Email)")
        print("   - Date Received (Date)")
    print("=" * 50)