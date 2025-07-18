#!/usr/bin/env python3
"""
Recruiter Email Tracker - Main Flask Application
Processes forwarded recruiter emails via Mailgun webhooks and creates Notion entries.
"""

from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime
import json

# Import our modules
import config
from database import DatabaseManager


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


def parse_email_simple(form_data, sender, subject):
    """
    Simple email parser that creates dummy data for testing.
    This replaces complex parsing logic for now.
    """
    # Extract recruiter email and basic info from sender
    recruiter_email = sender
    
    # Try to extract name from email (before @)
    if '@' in recruiter_email:
        name_part = recruiter_email.split('@')[0]
        # Convert dots/underscores to spaces and title case
        recruiter_name = name_part.replace('.', ' ').replace('_', ' ').title()
    else:
        recruiter_name = "Unknown Recruiter"
    
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
                'config_errors': len(config_summary['config_errors'])
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500


@app.route('/webhook/email', methods=['POST'])
def webhook_email():
    """Mailgun webhook endpoint for processing forwarded emails."""
    try:
        # Log the incoming request
        logger.info(f"Received webhook request from {request.remote_addr}")
        
        # Get request data
        form_data = request.form.to_dict()
        files_data = request.files.to_dict()
        
        # Log basic info about the email
        recipient = form_data.get('recipient', 'unknown')
        sender = form_data.get('sender', 'unknown')
        subject = form_data.get('subject', 'no subject')
        
        logger.info(f"Email from {sender} to {recipient}: {subject}")
        
        # Find the user based on recipient email
        user = config.get_user_by_mailgun_email(recipient)
        if not user:
            logger.warning(f"No user configured for recipient email: {recipient}")
            return jsonify({
                'status': 'error',
                'message': f'No user configured for recipient: {recipient}'
            }), 400
        
        logger.info(f"Processing email for user: {user['name']}")
        
        # Get or create user in database
        db_user = db.get_user_by_mailgun_email(recipient)
        if not db_user:
            logger.info(f"Creating new user in database: {user['name']}")
            user_id = db.create_user(
                name=user['name'],
                email=user['email'],
                notion_token=user['notion_token'],
                notion_database_id=user['notion_database_id'],
                mailgun_email=user['mailgun_email']
            )
            db_user = {'id': user_id}
        
        # Parse email with dummy data for now (skipping complex parsing)
        parsed_data = parse_email_simple(form_data, sender, subject)
        
        # Store in database
        contact_id = db.create_recruiter_contact(
            user_id=db_user['id'],
            recruiter_name=parsed_data['recruiter_name'],
            recruiter_email=parsed_data['recruiter_email'],
            company=parsed_data['company'],
            position=parsed_data['position'],
            location=parsed_data['location'],
            date_received=datetime.now(),
            raw_email_data=json.dumps(form_data),
            status="Recruiter Screen"
        )
        
        logger.info(f"Created database entry with ID: {contact_id}")
        
        # TODO: Send to Notion (placeholder)
        notion_page_id = create_notion_entry_placeholder(user, parsed_data)
        
        # Update database with Notion page ID
        if notion_page_id:
            db.update_notion_page_id(contact_id, notion_page_id)
            logger.info(f"Updated contact {contact_id} with Notion page ID: {notion_page_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Email processed and stored',
            'user': user['name'],
            'contact_id': contact_id,
            'notion_page_id': notion_page_id,
            'parsed_data': parsed_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
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
            'webhook': '/webhook/email'
        }
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