import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List, Any


class DatabaseManager:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure the database file exists and create if it doesn't."""
        if not os.path.exists(self.db_path):
            # Create empty database file
            open(self.db_path, 'a').close()
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected row count."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the new row ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    # User operations
    def create_user(self, name: str, email: str, notion_token: str, 
                   notion_database_id: str, mailgun_email: str) -> int:
        """Create a new user and return the user ID."""
        query = """
        INSERT INTO users (name, email, notion_token, notion_database_id, mailgun_email)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (name, email, notion_token, notion_database_id, mailgun_email))
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their email address."""
        query = "SELECT * FROM users WHERE email = ?"
        results = self.execute_query(query, (email,))
        return results[0] if results else None
    
    def get_user_by_mailgun_email(self, mailgun_email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their Mailgun forwarding email address."""
        query = "SELECT * FROM users WHERE mailgun_email = ?"
        results = self.execute_query(query, (mailgun_email,))
        return results[0] if results else None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        query = "SELECT * FROM users ORDER BY created_at"
        return self.execute_query(query)
    
    # Recruiter contact operations
    def create_recruiter_contact(self, user_id: int, recruiter_name: str, 
                               recruiter_email: str, company: str, position: str,
                               location: str, date_received: datetime, 
                               raw_email_data: str, status: str = "Recruiter Screen",
                               notion_page_id: str = None) -> int:
        """Create a new recruiter contact entry and return the contact ID."""
        query = """
        INSERT INTO recruiter_contacts 
        (user_id, recruiter_name, recruiter_email, company, position, location, 
         status, date_received, notion_page_id, raw_email_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (
            user_id, recruiter_name, recruiter_email, company, position, 
            location, status, date_received, notion_page_id, raw_email_data
        ))
    
    def get_contacts_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all recruiter contacts for a specific user."""
        query = """
        SELECT * FROM recruiter_contacts 
        WHERE user_id = ? 
        ORDER BY date_received DESC
        """
        return self.execute_query(query, (user_id,))
    
    def get_contact_by_recruiter_email(self, user_id: int, recruiter_email: str) -> Optional[Dict[str, Any]]:
        """Check if a recruiter contact already exists for a user."""
        query = """
        SELECT * FROM recruiter_contacts 
        WHERE user_id = ? AND recruiter_email = ?
        ORDER BY created_at DESC
        LIMIT 1
        """
        results = self.execute_query(query, (user_id, recruiter_email))
        return results[0] if results else None
    
    def update_notion_page_id(self, contact_id: int, notion_page_id: str) -> bool:
        """Update the Notion page ID for a recruiter contact."""
        query = "UPDATE recruiter_contacts SET notion_page_id = ? WHERE id = ?"
        return self.execute_update(query, (notion_page_id, contact_id)) > 0
    
    def get_contact_stats(self, user_id: int) -> Dict[str, int]:
        """Get statistics about recruiter contacts for a user."""
        query = """
        SELECT status, COUNT(*) as count
        FROM recruiter_contacts 
        WHERE user_id = ?
        GROUP BY status
        """
        results = self.execute_query(query, (user_id,))
        return {row['status']: row['count'] for row in results}