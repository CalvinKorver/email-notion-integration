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
    """Test that our webhook calls actually created database entries."""
    
    print("Testing database entries after webhook calls...")
    
    # Initialize database
    db = DatabaseManager(config.DATABASE_PATH)
    
    # Get all users
    users = db.get_all_users()
    print(f"\nFound {len(users)} users in database:")
    
    for user in users:
        print(f"\nUser: {user['name']} ({user['email']})")
        print(f"  Mailgun email: {user['mailgun_email']}")
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
    
    if total_contacts > 0:
        print("✅ Database entries found - webhook processing working!")
    else:
        print("❌ No database entries found - webhook may not be working")


if __name__ == "__main__":
    test_database_entries()