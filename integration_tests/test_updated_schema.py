#!/usr/bin/env python3
"""
Test script to verify the updated schema mapping works correctly.
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

def test_updated_schema():
    """Test the updated schema mapping."""
    
    # Get credentials from environment
    notion_token = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('DATABASE_ID')
    
    if not notion_token or not database_id:
        print("❌ Missing credentials in .env file")
        return False
    
    try:
        # Initialize the client
        client = NotionClient(notion_token)
        
        # Test connection
        print("🔍 Testing connection...")
        if not client.test_connection():
            print("❌ Failed to connect")
            return False
        print("✅ Connected successfully")
        
        # Test creating entry with minimal data (using placeholders)
        print("🔍 Testing entry creation with placeholders...")
        minimal_data = {
            "date_received": datetime.now()
        }
        
        page_id = client.create_recruiter_entry(database_id, minimal_data)
        if not page_id:
            print("❌ Failed to create entry with placeholders")
            return False
        
        print(f"✅ Created entry with placeholders: {page_id}")
        
        # Test creating entry with full data
        print("🔍 Testing entry creation with full data...")
        full_data = {
            "company": "TechCorp Inc",
            "recruiter_name": "Sarah Johnson",
            "position": "Senior Python Developer",
            "status": "Applied",
            "date_received": datetime(2024, 1, 15, 10, 30)
        }
        
        page_id_full = client.create_recruiter_entry(database_id, full_data)
        if not page_id_full:
            print("❌ Failed to create entry with full data")
            return False
        
        print(f"✅ Created entry with full data: {page_id_full}")
        
        # Test updating the entry
        print("🔍 Testing entry update...")
        updates = {
            "status": "Phone Screen",
            "recruiter_name": "Sarah Johnson (Updated)",
            "position": "Senior Python Developer (Remote)"
        }
        
        if client.update_recruiter_entry(page_id_full, updates):
            print("✅ Successfully updated entry")
        else:
            print("❌ Failed to update entry")
            return False
        
        print("\n🎉 All tests passed! The updated schema mapping is working correctly.")
        print("\n📋 Schema mapping:")
        print("- Company → Company (title)")
        print("- Recruiter Name → Recruiter Name (rich_text)")
        print("- Position → Job Title (rich_text)")
        print("- Status → Stage (status)")
        print("- Date Received → Application Date (date) - set once on creation")
        print("- Current Date → Last Contact Date (date) - updated on every create/update")
        print("- Notes and Follow-up Needed are never modified via API")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("UPDATED SCHEMA TEST")
    print("=" * 60)
    
    success = test_updated_schema()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ UPDATED SCHEMA TEST PASSED")
    else:
        print("❌ UPDATED SCHEMA TEST FAILED")
    print("=" * 60)