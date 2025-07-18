#!/usr/bin/env python3
"""
Test script with custom schema matching your actual Notion database.
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

def create_custom_recruiter_entry(client, database_id, recruiter_data):
    """
    Create a recruiter entry using your actual database schema.
    
    Your database properties:
    - Company (title)
    - Recruiter Name (rich_text)
    - Job Title (rich_text)
    - Application Date (date)
    - Notes (rich_text)
    - Last Contact Date (date)
    - Stage (status)
    - Follow-up Needed (checkbox)
    """
    try:
        # Format data for your actual Notion database schema
        properties = {
            "Company": {
                "title": [
                    {
                        "text": {
                            "content": recruiter_data.get("company", "Unknown Company")
                        }
                    }
                ]
            },
            "Recruiter Name": {
                "rich_text": [
                    {
                        "text": {
                            "content": recruiter_data.get("recruiter_name", "Unknown")
                        }
                    }
                ]
            },
            "Job Title": {
                "rich_text": [
                    {
                        "text": {
                            "content": recruiter_data.get("position", "Unknown Position")
                        }
                    }
                ]
            },
            "Application Date": {
                "date": {
                    "start": recruiter_data.get("date_received", datetime.now()).strftime("%Y-%m-%d")
                }
            },
            "Notes": {
                "rich_text": [
                    {
                        "text": {
                            "content": f"Email: {recruiter_data.get('recruiter_email', 'Unknown')}\nLocation: {recruiter_data.get('location', 'Unknown')}"
                        }
                    }
                ]
            },
            "Stage": {
                "status": {
                    "name": recruiter_data.get("status", "Applied")
                }
            },
            "Follow-up Needed": {
                "checkbox": True
            }
        }
        
        # Create the page
        page = client.client.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        
        page_id = page["id"]
        logger.info(f"Created custom entry for {recruiter_data.get('recruiter_name', 'Unknown')} at {recruiter_data.get('company', 'Unknown')}")
        return page_id
        
    except Exception as e:
        logger.error(f"Failed to create custom entry: {e}")
        return None

def test_custom_schema():
    """Test with your actual database schema."""
    
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
        
        # Test database access
        print("🔍 Testing database access...")
        db_info = client.get_database_info(database_id)
        if not db_info:
            print("❌ Failed to access database")
            return False
        
        db_title = db_info.get('title', [{}])[0].get('plain_text', 'Unknown')
        print(f"✅ Accessed database: '{db_title}'")
        
        # Test creating entry with your schema
        print("🔍 Testing entry creation with your schema...")
        sample_data = {
            "company": "Test Tech Corp",
            "recruiter_name": "Jane Doe",
            "recruiter_email": "jane.doe@testtech.com",
            "position": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "status": "Applied",
            "date_received": datetime.now()
        }
        
        page_id = create_custom_recruiter_entry(client, database_id, sample_data)
        if not page_id:
            print("❌ Failed to create entry")
            return False
        
        print(f"✅ Successfully created entry with ID: {page_id}")
        print("\n🎉 All tests passed! Your Notion integration is working with your custom schema.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CUSTOM SCHEMA NOTION TEST")
    print("=" * 60)
    
    success = test_custom_schema()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ CUSTOM SCHEMA TEST PASSED")
        print("\nYour database schema:")
        print("- Company (title)")
        print("- Recruiter Name (rich_text)")
        print("- Job Title (rich_text)")
        print("- Application Date (date)")
        print("- Notes (rich_text)")
        print("- Last Contact Date (date)")
        print("- Stage (status)")
        print("- Follow-up Needed (checkbox)")
    else:
        print("❌ CUSTOM SCHEMA TEST FAILED")
    print("=" * 60)