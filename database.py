import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List, Any


class DatabaseManager:
    def __init__(self, db_path: str = "database.db"):
        self.db_path = db_path
        self.is_in_memory = db_path == ":memory:"
        self._connection = None
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Ensure the database file exists and create if it doesn't."""
        if not self.is_in_memory and not os.path.exists(self.db_path):
            # Create empty database file
            open(self.db_path, 'a').close()
    
    def get_connection(self):
        """Get a database connection."""
        if self.is_in_memory:
            # For in-memory databases, reuse the same connection
            if self._connection is None:
                self._connection = sqlite3.connect(self.db_path)
            return self._connection
        else:
            return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        conn = self.get_connection()
        if self.is_in_memory:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        else:
            with conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected row count."""
        conn = self.get_connection()
        if self.is_in_memory:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        else:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the new row ID."""
        conn = self.get_connection()
        if self.is_in_memory:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        else:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
    
    # User operations
    def create_user(self, name: str, email: str, gmail_label: str, notion_token: str, notion_database_id: str) -> int:
        """Create a new user and return the user ID. Gmail password is NOT stored for security."""
        query = """
        INSERT INTO users (name, email, gmail_label, notion_token, notion_database_id)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (name, email, gmail_label, notion_token, notion_database_id))
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their email address."""
        query = "SELECT * FROM users WHERE email = ?"
        results = self.execute_query(query, (email,))
        return results[0] if results else None
    
    def update_last_checked(self, user_id: int, timestamp: datetime) -> bool:
        """Update the last_checked timestamp for a user."""
        query = "UPDATE users SET last_checked = ? WHERE id = ?"
        return self.execute_update(query, (timestamp, user_id)) > 0
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users."""
        query = "SELECT * FROM users ORDER BY created_at"
        return self.execute_query(query)
    
    # Recruiter contact operations
    def create_recruiter_contact(self, user_id: int, gmail_message_id: str,
                               recruiter_name: str, recruiter_email: str, company: str, 
                               position: str, location: str, date_received: datetime, 
                               raw_email_data: str, status: str = "Recruiter Screen",
                               notion_page_id: str = None) -> int:
        """Create a new recruiter contact entry and return the contact ID."""
        query = """
        INSERT INTO recruiter_contacts 
        (user_id, gmail_message_id, recruiter_name, recruiter_email, company, position, location, 
         status, date_received, notion_page_id, raw_email_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (
            user_id, gmail_message_id, recruiter_name, recruiter_email, company, position, 
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
    
    def get_contact_by_gmail_message_id(self, gmail_message_id: str) -> Optional[Dict[str, Any]]:
        """Check if a Gmail message has already been processed."""
        query = "SELECT * FROM recruiter_contacts WHERE gmail_message_id = ?"
        results = self.execute_query(query, (gmail_message_id,))
        return results[0] if results else None
    
    def get_contact_by_company(self, user_id: int, company: str) -> Optional[Dict[str, Any]]:
        """Check if a company already exists for a user."""
        query = "SELECT * FROM recruiter_contacts WHERE user_id = ? AND company = ? ORDER BY date_received DESC LIMIT 1"
        results = self.execute_query(query, (user_id, company))
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
    
    def get_user_last_check(self, email: str) -> Optional[datetime]:
        """Get the last_checked timestamp for a user by email."""
        query = "SELECT last_checked FROM users WHERE email = ?"
        results = self.execute_query(query, (email,))
        if results and results[0]['last_checked']:
            # Convert string back to datetime if needed
            last_checked = results[0]['last_checked']
            if isinstance(last_checked, str):
                try:
                    return datetime.fromisoformat(last_checked)
                except ValueError:
                    return None
            return last_checked
        return None
    
    def update_user_last_check(self, email: str, timestamp: datetime) -> bool:
        """Update the last_checked timestamp for a user by email."""
        query = "UPDATE users SET last_checked = ? WHERE email = ?"
        return self.execute_update(query, (timestamp, email)) > 0
    
    def email_already_processed(self, gmail_message_id: str) -> bool:
        """Check if an email has already been processed."""
        contact = self.get_contact_by_gmail_message_id(gmail_message_id)
        return contact is not None
    
    def log_recruiter_contact(self, user_email: str, gmail_message_id: str, 
                            parsed_data: Dict[str, Any], notion_page_id: Optional[str] = None) -> int:
        """Log a recruiter contact with parsed data."""
        # Get user ID from email
        user = self.get_user_by_email(user_email)
        if not user:
            raise ValueError(f"User not found with email: {user_email}")
        
        # Create the contact entry
        return self.create_recruiter_contact(
            user_id=user['id'],
            gmail_message_id=gmail_message_id,
            recruiter_name=parsed_data.get('recruiter_name', 'Unknown'),
            recruiter_email=parsed_data.get('recruiter_email', 'unknown@example.com'),
            company=parsed_data.get('company', 'Unknown Company'),
            position=parsed_data.get('position', 'Unknown Position'),
            location=parsed_data.get('location', 'Unknown Location'),
            date_received=parsed_data.get('date_received', datetime.now()),
            raw_email_data=parsed_data.get('raw_email', ''),
            status=parsed_data.get('status', 'Applied'),
            notion_page_id=notion_page_id
        )
    
    def close(self):
        """Close the database connection if it's in-memory."""
        if self.is_in_memory and self._connection:
            self._connection.close()
            self._connection = None