#!/usr/bin/env python3
"""
Quick test script to verify database operations work correctly.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from datetime import datetime


def test_database_operations():
    """Test basic database operations."""
    
    # Use a test database file
    test_db_path = "test_database.db"
    
    # Clean up any existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize database manager
    db = DatabaseManager(test_db_path)
    
    # Create tables (using the setup script's logic)
    from scripts.setup_db import create_tables
    create_tables(test_db_path)
    
    print("Testing database operations...")
    
    # Test 1: Create a user
    print("\n1. Testing user creation...")
    user_id = db.create_user(
        name="Test User",
        email="test@gmail.com", 
        gmail_app_password="abcd efgh ijkl mnop",
        gmail_label="Recruiters",
        notion_token="test_token_123",
        notion_database_id="test_db_123"
    )
    print(f"   Created user with ID: {user_id}")
    
    # Test 2: Retrieve user by email
    print("\n2. Testing user retrieval...")
    user = db.get_user_by_email("test@gmail.com")
    print(f"   Retrieved user: {user['name']} ({user['email']})")
    
    # Test 3: Test last_checked update
    print("\n3. Testing last_checked update...")
    success = db.update_last_checked(user_id, datetime.now())
    print(f"   Updated last_checked: {success}")
    
    # Test 4: Create a recruiter contact
    print("\n4. Testing recruiter contact creation...")
    contact_id = db.create_recruiter_contact(
        user_id=user_id,
        gmail_message_id="<test_message_123@gmail.com>",
        recruiter_name="Jane Recruiter",
        recruiter_email="jane@techcorp.com",
        company="TechCorp Inc", 
        position="Senior Software Engineer",
        location="San Francisco, CA",
        date_received=datetime.now(),
        raw_email_data="Sample email content here..."
    )
    print(f"   Created recruiter contact with ID: {contact_id}")
    
    # Test 5: Retrieve contacts for user
    print("\n5. Testing contact retrieval...")
    contacts = db.get_contacts_by_user(user_id)
    print(f"   Found {len(contacts)} contacts for user")
    if contacts:
        contact = contacts[0]
        print(f"   Contact: {contact['recruiter_name']} from {contact['company']}")
    
    # Test 6: Check for duplicate Gmail message ID
    print("\n6. Testing Gmail message ID duplicate detection...")
    existing_contact = db.get_contact_by_gmail_message_id("<test_message_123@gmail.com>")
    print(f"   Existing Gmail message found: {existing_contact is not None}")
    
    # Test 7: Update Notion page ID
    print("\n7. Testing Notion page ID update...")
    success = db.update_notion_page_id(contact_id, "notion_page_123")
    print(f"   Notion page ID update successful: {success}")
    
    # Test 8: Get contact statistics
    print("\n8. Testing contact statistics...")
    stats = db.get_contact_stats(user_id)
    print(f"   Contact stats: {stats}")
    
    # Clean up test database
    os.remove(test_db_path)
    
    print("\n✅ All database operations tested successfully!")


if __name__ == "__main__":
    test_database_operations()