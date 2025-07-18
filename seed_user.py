#!/usr/bin/env python3
"""
Seed script to create the default user from config.py in the database.
"""

from config import USER_CONFIG
from database import DatabaseManager
import logging

def seed_default_user():
    """Create the default user from config.py in the database."""
    db = DatabaseManager()
    
    # Check if user already exists
    existing_user = db.get_user_by_email(USER_CONFIG['email'])
    if existing_user:
        print(f"User {USER_CONFIG['name']} ({USER_CONFIG['email']}) already exists in database")
        return existing_user['id']
    
    # Create the user
    user_id = db.create_user(
        name=USER_CONFIG['name'],
        email=USER_CONFIG['email'],
        gmail_label=USER_CONFIG['gmail_label'],
        notion_token=USER_CONFIG['notion_token'],
        notion_database_id=USER_CONFIG['notion_database_id']
    )
    
    print(f"Created user: {USER_CONFIG['name']} ({USER_CONFIG['email']}) with ID: {user_id}")
    return user_id

if __name__ == "__main__":
    print("Seeding default user from config...")
    user_id = seed_default_user()
    print(f"User seeded successfully with ID: {user_id}")