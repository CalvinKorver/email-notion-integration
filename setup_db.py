#!/usr/bin/env python3
"""
Database setup script for the Recruiter Email Tracker.
Creates the necessary tables and optionally seeds with initial data.
"""

import sqlite3
import os
from database import DatabaseManager


def create_tables(db_path: str = "database.db"):
    """Create the database tables."""
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        gmail_app_password TEXT,
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
    
    # Create index on user_id for faster lookups
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_recruiter_contacts_user_id 
    ON recruiter_contacts (user_id)
    """)
    
    # Create index on recruiter_email for duplicate detection
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_recruiter_contacts_email 
    ON recruiter_contacts (user_id, recruiter_email)
    """)
    
    # Create index on email for fast user lookup
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_users_email 
    ON users (email)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Database tables created successfully in {db_path}")


def seed_test_data(db_path: str = "database.db"):
    """Optionally seed the database with test data."""
    
    db = DatabaseManager(db_path)
    
    # Check if users already exist
    existing_users = db.get_all_users()
    if existing_users:
        print(f"Database already contains {len(existing_users)} users. Skipping seed data.")
        return
    
    # Add test users (with placeholder data)
    test_users = [
        {
            'name': 'Test User 1',
            'email': 'test1@gmail.com',
            'gmail_app_password': 'abcd efgh ijkl mnop',
            'gmail_label': 'Recruiters',
            'notion_token': 'secret_token_placeholder_1',
            'notion_database_id': 'database_id_placeholder_1'
        },
        {
            'name': 'Test User 2', 
            'email': 'test2@gmail.com',
            'gmail_app_password': 'efgh ijkl mnop qrst',
            'gmail_label': 'Recruiters',
            'notion_token': 'secret_token_placeholder_2',
            'notion_database_id': 'database_id_placeholder_2'
        }
    ]
    
    for user_data in test_users:
        user_id = db.create_user(**user_data)
        print(f"Created test user: {user_data['name']} (ID: {user_id})")
    
    print("Test data seeded successfully!")


def verify_database(db_path: str = "database.db"):
    """Verify that the database was created correctly."""
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database file {db_path} does not exist!")
        return False
    
    db = DatabaseManager(db_path)
    
    try:
        # Test basic operations
        users = db.get_all_users()
        print(f"Database verification successful!")
        print(f"- Found {len(users)} users in database")
        
        for user in users:
            contacts = db.get_contacts_by_user(user['id'])
            print(f"- User '{user['name']}' has {len(contacts)} recruiter contacts")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Database verification failed: {e}")
        return False


def main():
    """Main setup function."""
    
    print("=== Recruiter Email Tracker - Database Setup ===")
    
    db_path = os.getenv('DATABASE_PATH', 'database.db')
    print(f"Using database path: {db_path}")
    
    # Create tables
    create_tables(db_path)
    
    # Ask user if they want to seed test data
    while True:
        seed_choice = input("\nSeed database with test data? (y/n): ").lower().strip()
        if seed_choice in ['y', 'yes']:
            seed_test_data(db_path)
            break
        elif seed_choice in ['n', 'no']:
            print("Skipping test data seed.")
            break
        else:
            print("Please enter 'y' or 'n'")
    
    # Verify everything worked
    print("\n=== Verification ===")
    if verify_database(db_path):
        print("✅ Database setup completed successfully!")
    else:
        print("❌ Database setup failed!")


if __name__ == "__main__":
    main()