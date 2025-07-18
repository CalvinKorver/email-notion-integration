"""
Quick test script to verify database operations work correctly.
"""

import sys
import os
import pytest

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from datetime import datetime


def test_database_operations():
    """Test basic database operations."""
    
    # Use in-memory database for testing
    test_db_path = ":memory:"
    
    # Initialize database manager
    db = DatabaseManager(test_db_path)
    
    # Create tables using the database manager's connection
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        gmail_label TEXT DEFAULT 'Recruiters',
        notion_token TEXT,
        notion_database_id TEXT,
        last_checked TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create recruiter_contacts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recruiter_contacts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        gmail_message_id TEXT UNIQUE,
        recruiter_name TEXT,
        recruiter_email TEXT,
        company TEXT,
        position TEXT,
        location TEXT,
        status TEXT DEFAULT 'Recruiter Screen',
        date_received TIMESTAMP,
        notion_page_id TEXT,
        raw_email_data TEXT,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)
    
    conn.commit()
    
    # Test 1: Create a user
    user_id = db.create_user(
        name="Test User",
        email="test@gmail.com", 
        gmail_label="Recruiters",
        notion_token="test_token_123",
        notion_database_id="test_db_123"
    )
    assert user_id is not None
    
    # Test 2: Retrieve user by email
    user = db.get_user_by_email("test@gmail.com")
    assert user is not None
    assert user['name'] == "Test User"
    assert user['email'] == "test@gmail.com"
    
    # Test 3: Test last_checked update
    success = db.update_last_checked(user_id, datetime.now())
    assert success is True
    
    # Test 4: Create a recruiter contact
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
    assert contact_id is not None
    
    # Test 5: Retrieve contacts for user
    contacts = db.get_contacts_by_user(user_id)
    assert len(contacts) == 1
    contact = contacts[0]
    assert contact['recruiter_name'] == "Jane Recruiter"
    assert contact['company'] == "TechCorp Inc"
    
    # Test 6: Check for duplicate Gmail message ID
    existing_contact = db.get_contact_by_gmail_message_id("<test_message_123@gmail.com>")
    assert existing_contact is not None
    
    # Test 7: Update Notion page ID
    success = db.update_notion_page_id(contact_id, "notion_page_123")
    assert success is True
    
    # Test 8: Get contact statistics
    stats = db.get_contact_stats(user_id)
    assert isinstance(stats, dict)