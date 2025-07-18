#!/usr/bin/env python3
"""
Recruiter Email Tracker - Main Flask Application
Periodically checks Gmail inboxes for recruiter emails and creates Notion entries.
"""

from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime
import json

# Import our modules
import config
from database import DatabaseManager
from email_checker import GmailChecker

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize database
db = DatabaseManager(config.DATABASE_PATH)


def parse_recruiter_email_simple(email_data):
    """
    Simple email parser that extracts recruiter data from Gmail message.
    This is a basic implementation that can be enhanced later.
    """
    # Extract recruiter email and basic info from sender
    sender = email_data.get('sender', '')
    subject = email_data.get('subject', '')
    
    # Try to extract recruiter email from sender
    if '<' in sender and '>' in sender:
        # Format: "Name <email@domain.com>"
        recruiter_email = sender.split('<')[1].split('>')[0]
        recruiter_name = sender.split('<')[0].strip().strip('"')
    else:
        # Format: "email@domain.com" or just plain text
        recruiter_email = sender
        recruiter_name = sender.split('@')[0] if '@' in sender else "Unknown Recruiter"
    
    # Extract company from email domain (simple heuristic)
    if '@' in recruiter_email:
        domain = recruiter_email.split('@')[1]
        company = domain.split('.')[0].title()
        # Clean up common domain patterns
        if company.lower() in ['gmail', 'yahoo', 'hotmail', 'outlook']:
            company = "Unknown Company"
    else:
        company = "Unknown Company"
    
    # Extract position from subject (look for common job title keywords)
    position = "Software Position"  # Default
    subject_lower = subject.lower()
    
    job_keywords = [
        'engineer', 'developer', 'manager', 'director', 'analyst', 
        'specialist', 'coordinator', 'lead', 'senior', 'junior',
        'architect', 'consultant', 'designer', 'scientist'
    ]
    
    for keyword in job_keywords:
        if keyword in subject_lower:
            # Try to extract a more specific title
            words = subject.split()
            for i, word in enumerate(words):
                if keyword in word.lower():
                    # Take the keyword and a few surrounding words
                    start = max(0, i-1)
                    end = min(len(words), i+3)
                    position = ' '.join(words[start:end])
                    break
            break
    
    # Default location (would normally parse from email body)
    location = "Remote / San Francisco, CA"
    
    return {
        'recruiter_name': recruiter_name,
        'recruiter_email': recruiter_email,
        'company': company,
        'position': position,
        'location': location
    }


def create_notion_entry_placeholder(user, parsed_data):
    """
    Placeholder function for Notion integration.
    Returns a fake page ID for testing.
    """
    logger.info(f"[PLACEHOLDER] Would create Notion entry for {user['name']}")
    logger.info(f"[PLACEHOLDER] Data: {json.dumps(parsed_data, indent=2)}")
    logger.info(f"[PLACEHOLDER] Database ID: {user['notion_database_id']}")
    
    # Return a fake Notion page ID for testing
    fake_page_id = f"notion_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"[PLACEHOLDER] Generated fake page ID: {fake_page_id}")
    
    return fake_page_id


def check_user_emails(user):
    """Check emails for a single user and process any new recruiter emails."""
    logger.info(f"Checking emails for user: {user['name']} ({user['email']})")
    
    try:
        # Get or create user in database
        db_user = db.get_user_by_email(user['email'])
        if not db_user:
            logger.info(f"Creating new user in database: {user['name']}")
            user_id = db.create_user(
                name=user['name'],
                email=user['email'],
                gmail_app_password=user['gmail_app_password'],
                gmail_label=user['gmail_label'],
                notion_token=user['notion_token'],
                notion_database_id=user['notion_database_id']
            )
            db_user = {'id': user_id, 'last_checked': None}
        
        # Initialize Gmail checker
        gmail_checker = GmailChecker(user['email'], user['gmail_app_password'])
        
        # Determine since_date based on last_checked
        since_date = db_user.get('last_checked')
        if since_date:
            logger.info(f"Checking emails since last check: {since_date}")
        else:
            logger.info("First time checking emails for this user")
        
        # Check for new emails
        emails = gmail_checker.check_new_emails(
            label=user['gmail_label'],
            since_date=since_date
        )
        
        processed_count = 0
        for email_data in emails:
            # Check if we've already processed this email
            if db.get_contact_by_gmail_message_id(email_data['message_id']):
                logger.debug(f"Skipping already processed email: {email_data['message_id']}")
                continue
            
            # Parse email data
            parsed_data = parse_recruiter_email_simple(email_data)
            
            # Store in database
            contact_id = db.create_recruiter_contact(
                user_id=db_user['id'],
                gmail_message_id=email_data['message_id'],
                recruiter_name=parsed_data['recruiter_name'],
                recruiter_email=parsed_data['recruiter_email'],
                company=parsed_data['company'],
                position=parsed_data['position'],
                location=parsed_data['location'],
                date_received=email_data['date_received'],
                raw_email_data=email_data['raw_email'],
                status="Recruiter Screen"
            )
            
            logger.info(f"Created database entry with ID: {contact_id}")
            
            # Create Notion entry (placeholder)
            notion_page_id = create_notion_entry_placeholder(user, parsed_data)
            
            # Update database with Notion page ID
            if notion_page_id:
                db.update_notion_page_id(contact_id, notion_page_id)
                logger.info(f"Updated contact {contact_id} with Notion page ID: {notion_page_id}")
            
            processed_count += 1
        
        # Update last_checked timestamp
        db.update_last_checked(db_user['id'], datetime.now())
        
        logger.info(f"Processed {processed_count} new emails for {user['name']}")
        return processed_count
        
    except Exception as e:
        logger.error(f"Error checking emails for {user['name']}: {str(e)}")
        return 0
    finally:
        if 'gmail_checker' in locals():
            gmail_checker.disconnect()


def check_all_users_emails():
    """Check emails for all configured users."""
    logger.info("Starting email check for all users")
    
    total_processed = 0
    for user in config.USERS:
        try:
            count = check_user_emails(user)
            total_processed += count
        except Exception as e:
            logger.error(f"Failed to check emails for {user['name']}: {str(e)}")
    
    logger.info(f"Email check completed. Total new emails processed: {total_processed}")
    return total_processed


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        users = db.get_all_users()
        
        # Get configuration summary
        config_summary = config.get_config_summary()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': {
                'status': 'connected',
                'path': config.DATABASE_PATH,
                'users_count': len(users)
            },
            'configuration': {
                'flask_env': config.FLASK_ENV,
                'users_configured': config_summary['users_configured'],
                'config_errors': len(config_summary['config_errors']),
                'check_interval_minutes': config.CHECK_INTERVAL
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500


@app.route('/check-emails', methods=['POST'])
def manual_email_check():
    """Manual trigger endpoint for checking emails (for testing)."""
    try:
        logger.info("Manual email check triggered")
        
        # Check emails for all users
        processed_count = check_all_users_emails()
        
        return jsonify({
            'status': 'success',
            'message': 'Email check completed',
            'emails_processed': processed_count,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Manual email check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Email check failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/', methods=['GET'])
def index():
    """Basic index route."""
    return jsonify({
        'service': 'Recruiter Email Tracker',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/health',
            'check_emails': '/check-emails (POST)'
        },
        'configured_users': len(config.USERS),
        'check_interval_minutes': config.CHECK_INTERVAL
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    logger.info("Starting Recruiter Email Tracker Flask application")
    
    # Validate configuration on startup
    config_errors = config.validate_config()
    if config_errors:
        logger.warning("Configuration issues detected:")
        for error in config_errors:
            logger.warning(f"  - {error}")
        logger.warning("Application will start but may not function properly with placeholder values")
    
    # Log configuration summary
    summary = config.get_config_summary()
    logger.info(f"Configuration: {json.dumps(summary, indent=2)}")
    
    # Start Flask app
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )