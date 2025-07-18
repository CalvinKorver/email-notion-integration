import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')

# Email checking interval (minutes)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL_MINUTES', '5'))

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
        'name': 'Your Name',
        'email': 'your.personal@gmail.com',
        'gmail_app_password': os.getenv('USER1_GMAIL_APP_PASSWORD', 'abcd efgh ijkl mnop'),
        'gmail_label': os.getenv('USER1_GMAIL_LABEL', 'Recruiters'),
        'notion_token': os.getenv('USER1_NOTION_TOKEN', 'secret_token_placeholder_1'),
        'notion_database_id': os.getenv('USER1_NOTION_DATABASE_ID', 'database_id_placeholder_1')
    },
    {
        'name': 'User Two',
        'email': 'user2@gmail.com', 
        'gmail_app_password': os.getenv('USER2_GMAIL_APP_PASSWORD', 'efgh ijkl mnop qrst'),
        'gmail_label': os.getenv('USER2_GMAIL_LABEL', 'Recruiters'),
        'notion_token': os.getenv('USER2_NOTION_TOKEN', 'secret_token_placeholder_2'),
        'notion_database_id': os.getenv('USER2_NOTION_DATABASE_ID', 'database_id_placeholder_2')
    },
    {
        'name': 'User Three',
        'email': 'user3@gmail.com',
        'gmail_app_password': os.getenv('USER3_GMAIL_APP_PASSWORD', 'ijkl mnop qrst uvwx'),
        'gmail_label': os.getenv('USER3_GMAIL_LABEL', 'Recruiters'),
        'notion_token': os.getenv('USER3_NOTION_TOKEN', 'secret_token_placeholder_3'),
        'notion_database_id': os.getenv('USER3_NOTION_DATABASE_ID', 'database_id_placeholder_3')
    }
]

# Validation function
def validate_config():
    """Validate that required configuration is present."""
    errors = []
    
    # Check that users have valid Gmail and Notion configuration
    for i, user in enumerate(USERS):
        if user['gmail_app_password'].startswith('abcd') or user['gmail_app_password'].startswith('efgh') or user['gmail_app_password'].startswith('ijkl'):
            errors.append(f"User {i+1} ({user['name']}) needs a real Gmail app password")
        
        if user['notion_token'].startswith('secret_token_placeholder'):
            errors.append(f"User {i+1} ({user['name']}) needs a real Notion token")
        
        if user['notion_database_id'].startswith('database_id_placeholder'):
            errors.append(f"User {i+1} ({user['name']}) needs a real Notion database ID")
    
    return errors


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
        'check_interval_minutes': CHECK_INTERVAL,
        'users_configured': len(USERS),
        'user_emails': [user['email'] for user in USERS],
        'config_errors': validate_config()
    }