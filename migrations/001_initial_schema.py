"""
Initial database schema migration.
Creates the users and recruiter_contacts tables.
"""

def up(cursor):
    """Apply the migration."""
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            gmail_label TEXT NOT NULL,
            notion_token TEXT NOT NULL,
            notion_database_id TEXT NOT NULL,
            last_checked TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create recruiter_contacts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recruiter_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            gmail_message_id TEXT UNIQUE NOT NULL,
            recruiter_name TEXT NOT NULL,
            recruiter_email TEXT NOT NULL,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'Recruiter Screen',
            date_received TIMESTAMP NOT NULL,
            notion_page_id TEXT,
            raw_email_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recruiter_contacts_user_id 
        ON recruiter_contacts (user_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recruiter_contacts_gmail_message_id 
        ON recruiter_contacts (gmail_message_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_email 
        ON users (email)
    """)


def down(cursor):
    """Rollback the migration."""
    cursor.execute("DROP INDEX IF EXISTS idx_users_email")
    cursor.execute("DROP INDEX IF EXISTS idx_recruiter_contacts_gmail_message_id")
    cursor.execute("DROP INDEX IF EXISTS idx_recruiter_contacts_user_id")
    cursor.execute("DROP TABLE IF EXISTS recruiter_contacts")
    cursor.execute("DROP TABLE IF EXISTS users")