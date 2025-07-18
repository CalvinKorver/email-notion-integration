import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')

# Mailgun configuration
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_WEBHOOK_SIGNING_KEY = os.getenv('MAILGUN_WEBHOOK_SIGNING_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN', 'yourdomain.com')

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = FLASK_ENV == 'development'
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))

# Hardcoded user configuration
# In production, these would be loaded from the database
# For initial setup, we define the users here for easy configuration
USERS = [
    {
        'name': 'User One',
        'email': 'user1@example.com',
        'notion_token': os.getenv('USER1_NOTION_TOKEN', 'secret_token_placeholder_1'),
        'notion_database_id': os.getenv('USER1_NOTION_DATABASE_ID', 'database_id_placeholder_1'),
        'mailgun_email': f"user1@{MAILGUN_DOMAIN}"
    },
    {
        'name': 'User Two',
        'email': 'user2@example.com', 
        'notion_token': os.getenv('USER2_NOTION_TOKEN', 'secret_token_placeholder_2'),
        'notion_database_id': os.getenv('USER2_NOTION_DATABASE_ID', 'database_id_placeholder_2'),
        'mailgun_email': f"user2@{MAILGUN_DOMAIN}"
    },
    {
        'name': 'User Three',
        'email': 'user3@example.com',
        'notion_token': os.getenv('USER3_NOTION_TOKEN', 'secret_token_placeholder_3'),
        'notion_database_id': os.getenv('USER3_NOTION_DATABASE_ID', 'database_id_placeholder_3'),
        'mailgun_email': f"user3@{MAILGUN_DOMAIN}"
    }
]

# Validation function
def validate_config():
    """Validate that required configuration is present."""
    errors = []
    
    # Check required Mailgun settings
    if not MAILGUN_API_KEY:
        errors.append("MAILGUN_API_KEY environment variable is required")
    
    if not MAILGUN_WEBHOOK_SIGNING_KEY:
        errors.append("MAILGUN_WEBHOOK_SIGNING_KEY environment variable is required")
    
    # Check that users have valid Notion configuration
    for i, user in enumerate(USERS):
        if user['notion_token'].startswith('secret_token_placeholder'):
            errors.append(f"User {i+1} ({user['name']}) needs a real Notion token")
        
        if user['notion_database_id'].startswith('database_id_placeholder'):
            errors.append(f"User {i+1} ({user['name']}) needs a real Notion database ID")
    
    return errors

def get_user_by_mailgun_email(mailgun_email: str):
    """Get user configuration by their Mailgun email address."""
    for user in USERS:
        if user['mailgun_email'] == mailgun_email:
            return user
    return None

def get_user_by_email(email: str):
    """Get user configuration by their regular email address."""
    for user in USERS:
        if user['email'] == email:
            return user
    return None

# Configuration summary for debugging
def get_config_summary():
    """Get a summary of the current configuration (without sensitive data)."""
    return {
        'database_path': DATABASE_PATH,
        'flask_env': FLASK_ENV,
        'flask_host': FLASK_HOST,
        'flask_port': FLASK_PORT,
        'mailgun_domain': MAILGUN_DOMAIN,
        'users_configured': len(USERS),
        'user_mailgun_emails': [user['mailgun_email'] for user in USERS],
        'config_errors': validate_config()
    }