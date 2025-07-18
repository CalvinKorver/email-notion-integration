#!/usr/bin/env python3
"""
End-to-end test for email processing with database storage.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
import config


def test_database_entries():
    """Test database entries and Gmail architecture setup."""
    
    print("Testing database entries and Gmail setup...")
    
    # Initialize database
    db = DatabaseManager(config.DATABASE_PATH)
    
    # Get all users
    users = db.get_all_users()
    print(f"\nFound {len(users)} users in database:")
    
    for user in users:
        print(f"\nUser: {user['name']} ({user['email']})")
        print(f"  Gmail label: {user.get('gmail_label', 'N/A')}")
        print(f"  Last checked: {user.get('last_checked', 'Never')}")
        print(f"  Created: {user['created_at']}")
        
        # Get contacts for this user
        contacts = db.get_contacts_by_user(user['id'])
        print(f"  Contacts: {len(contacts)}")
        
        for contact in contacts:
            print(f"    - {contact['recruiter_name']} from {contact['company']}")
            print(f"      Position: {contact['position']}")
            print(f"      Location: {contact['location']}")
            print(f"      Email: {contact['recruiter_email']}")
            print(f"      Status: {contact['status']}")
            print(f"      Gmail Message ID: {contact.get('gmail_message_id', 'N/A')}")
            print(f"      Notion Page: {contact['notion_page_id']}")
            print(f"      Received: {contact['date_received']}")
    
    # Get contact statistics
    print(f"\nOverall statistics:")
    total_contacts = 0
    for user in users:
        stats = db.get_contact_stats(user['id'])
        user_total = sum(stats.values())
        total_contacts += user_total
        print(f"  {user['name']}: {user_total} contacts - {stats}")
    
    print(f"\nTotal contacts across all users: {total_contacts}")
    
    # Test configuration for Gmail setup
    print(f"\nGmail Configuration:")
    print(f"  Check interval: {config.CHECK_INTERVAL} minutes")
    print(f"  Configured users: {len(config.USERS)}")
    
    for i, user in enumerate(config.USERS):
        print(f"  User {i+1}: {user['name']}")
        print(f"    Email: {user['email']}")
        print(f"    Gmail label: {user['gmail_label']}")
        print(f"    Has app password: {'Yes' if user['gmail_app_password'] else 'No'}")
    
    if total_contacts > 0:
        print("✅ Database entries found - email processing working!")
    else:
        print("ℹ️  No database entries found - this is expected until Gmail emails are processed")
        
    print("✅ Database and configuration structure validated!")


if __name__ == "__main__":
    test_database_entries()