import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')

# Email checking interval (minutes)
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL_MINUTES', '20'))

# Email lookback period (days) - how far back to check for emails on first run
EMAIL_LOOKBACK_DAYS = int(os.getenv('EMAIL_LOOKBACK_DAYS', '3'))

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = FLASK_ENV == 'development'
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5001'))

# Single user configuration from environment variables
# Gmail password is NOT stored in database for security
USER_CONFIG = {
    'name': os.getenv('USER_NAME', 'Your Name'),
    'email': os.getenv('GMAIL_EMAIL', 'your.personal@gmail.com'),
    'gmail_app_password': os.getenv('GMAIL_PASSWORD', 'abcd efgh ijkl mnop'),
    'gmail_label': os.getenv('GMAIL_LABEL', 'Recruiters'),
    'notion_token': os.getenv('NOTION_API_KEY', 'secret_token_placeholder_1'),
    'notion_database_id': os.getenv('DATABASE_ID', 'database_id_placeholder_1')
}

# Legacy USERS list for backwards compatibility
USERS = [USER_CONFIG]

# Validation function
def validate_config():
    """Validate that required configuration is present."""
    errors = []
    
    # Check that user has valid Gmail and Notion configuration
    user = USER_CONFIG
    if user['gmail_app_password'].startswith('abcd') or user['gmail_app_password'].startswith('efgh') or user['gmail_app_password'].startswith('ijkl'):
        errors.append(f"User ({user['name']}) needs a real Gmail app password")
    
    if user['notion_token'].startswith('secret_token_placeholder'):
        errors.append(f"User ({user['name']}) needs a real Notion token")
    
    if user['notion_database_id'].startswith('database_id_placeholder'):
        errors.append(f"User ({user['name']}) needs a real Notion database ID")
    
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
        'user_configured': USER_CONFIG['name'],
        'user_email': USER_CONFIG['email'],
        'config_errors': validate_config()
    }