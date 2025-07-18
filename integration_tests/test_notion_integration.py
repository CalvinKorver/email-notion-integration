#!/usr/bin/env python3
"""
Integration test script for Notion API client.

This script can be used to test the actual connection to a Notion workspace.
You'll need to provide real Notion credentials to run this test.

Usage:
    python test_notion_integration.py
"""

import logging
import os
import sys
from datetime import datetime

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notion_api import NotionClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_notion_integration():
    """Test the Notion integration with sample data."""
    
    # TODO: Replace with actual Notion integration token
    # Get this from: https://www.notion.so/my-integrations
    notion_token = "your_notion_integration_token_here"
    
    # TODO: Replace with actual database ID
    # Get this from your Notion database URL
    database_id = "your_database_id_here"
    
    if notion_token == "your_notion_integration_token_here":
        print("Please update the script with your actual Notion token and database ID")
        print("1. Go to https://www.notion.so/my-integrations to create an integration")
        print("2. Copy the integration token")
        print("3. Create a database in Notion with the following properties:")
        print("   - Recruiter Name (Title)")
        print("   - Company (Text)")
        print("   - Position (Text)")
        print("   - Location (Text)")
        print("   - Status (Select with options: Recruiter Screen, Phone Screen, Interview, Rejected, Offer)")
        print("   - Email (Email)")
        print("   - Date Received (Date)")
        print("4. Share the database with your integration")
        print("5. Copy the database ID from the URL")
        return False
    
    try:
        # Initialize the client
        client = NotionClient(notion_token)
        
        # Test connection
        print("Testing connection to Notion...")
        if not client.test_connection():
            print("❌ Failed to connect to Notion workspace")
            return False
        
        print("✅ Successfully connected to Notion workspace")
        
        # Test database access
        print(f"Testing database access for ID: {database_id}")
        db_info = client.get_database_info(database_id)
        if not db_info:
            print("❌ Failed to access database")
            return False
        
        print(f"✅ Successfully accessed database: {db_info.get('title', [{}])[0].get('plain_text', 'Unknown')}")
        
        # Test creating an entry
        print("Testing entry creation...")
        sample_data = {
            "recruiter_name": "Jane Smith",
            "recruiter_email": "jane.smith@testcompany.com",
            "company": "Test Company",
            "position": "Senior Software Engineer",
            "location": "Remote",
            "status": "Recruiter Screen",
            "date_received": datetime.now()
        }
        
        page_id = client.create_recruiter_entry(database_id, sample_data)
        if not page_id:
            print("❌ Failed to create entry")
            return False
        
        print(f"✅ Successfully created entry with ID: {page_id}")
        
        # Test updating the entry
        print("Testing entry update...")
        updates = {
            "status": "Phone Screen",
            "notes": "Great initial conversation"
        }
        
        if client.update_recruiter_entry(page_id, updates):
            print("✅ Successfully updated entry")
        else:
            print("❌ Failed to update entry")
            return False
        
        # Test searching entries
        print("Testing entry search...")
        results = client.search_entries(database_id, "Jane Smith")
        if results:
            print(f"✅ Successfully found {len(results)} entries matching 'Jane Smith'")
        else:
            print("⚠️  No entries found (this might be expected)")
        
        print("\n🎉 All tests passed! The Notion integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_notion_integration()
    if success:
        print("\nYou can now proceed to integrate this with your email processing pipeline.")
    else:
        print("\nPlease fix the issues above before proceeding.")