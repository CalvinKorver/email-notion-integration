# Recruiter Email Tracker - Implementation Plan

## Project Overview
A simple Python Flask app that periodically checks Gmail inboxes for recruiter emails and creates entries in Notion databases. Hardcoded for a few users initially.

## Tech Stack
- **Backend**: Python/Flask
- **Database**: SQLite (local file)
- **Email**: Gmail IMAP (with App Passwords)
- **Integration**: Notion API
- **Deployment**: Railway/Render (with persistent storage)
- **Scheduling**: APScheduler for periodic email checking

## Project Structure
```
recruiter-tracker/
├── app.py                 # Main Flask application
├── email_checker.py      # Gmail IMAP email checking
├── email_parser.py        # Email content parsing logic
├── notion_client.py       # Notion API wrapper
├── database.py           # SQLite operations
├── config.py             # Configuration and hardcoded users
├── scheduler.py          # Background task scheduling
├── requirements.txt      # Python dependencies
├── database.db          # SQLite database file
├── setup_db.py          # Database initialization script
└── README.md            # Setup and deployment instructions
```

---

## Phase 1: Core Infrastructure Setup

### Checkpoint 1.1: Project Setup
- [ ] Create new Python project directory
- [ ] Set up virtual environment
- [ ] Create `requirements.txt` with dependencies:
  ```
  Flask==2.3.3
  requests==2.31.0
  python-dotenv==1.0.0
  APScheduler==3.10.4
  secure-smtplib==0.1.1
  ```
- [ ] Initialize git repository
- [ ] Create basic project structure

### Checkpoint 1.2: Database Setup
- [ ] Create `database.py` with SQLite operations
- [ ] Create `setup_db.py` script to initialize tables:
  ```sql
  CREATE TABLE users (
      id INTEGER PRIMARY KEY,
      name TEXT,
      email TEXT UNIQUE,
      gmail_app_password TEXT,
      gmail_label TEXT DEFAULT 'Recruiters',
      notion_token TEXT,
      notion_database_id TEXT,
      last_checked TIMESTAMP,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE recruiter_contacts (
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
  );
  ```
- [ ] Test database creation and basic operations

### Checkpoint 1.3: Configuration Setup
- [ ] Create `config.py` with hardcoded user data:
  ```python
  USERS = [
      {
          'name': 'Your Name',
          'email': 'your.personal@gmail.com',
          'gmail_app_password': 'abcd efgh ijkl mnop',  # Gmail app password
          'gmail_label': 'Recruiters',  # Gmail label to monitor
          'notion_token': 'secret_token_here',
          'notion_database_id': 'database_id_here'
      },
      # Add 2-3 more users as needed
  ]
  
  # Email checking interval (minutes)
  CHECK_INTERVAL = 5
  ```
- [ ] Set up environment variables for sensitive data
- [ ] Create `.env` file for local development

---

## Phase 2: Email Processing Core

### Checkpoint 2.1: Gmail IMAP Client
- [ ] Create `email_checker.py` with Gmail IMAP connection:
  ```python
  import imaplib
  import email
  from email.header import decode_header
  
  class GmailChecker:
      def __init__(self, email_address, app_password):
          self.email = email_address
          self.password = app_password
          
      def check_new_emails(self, label='Recruiters', since_date=None):
          # Connect to Gmail IMAP
          # Search for emails in specified label
          # Return list of new email data
  ```
- [ ] Implement IMAP connection and authentication
- [ ] Add email search and retrieval functionality
- [ ] Handle connection errors and retries

### Checkpoint 2.2: Basic Flask App
- [ ] Create `app.py` with basic Flask setup
- [ ] Implement health check endpoint: `GET /health`
- [ ] Implement manual trigger endpoint: `POST /check-emails` (for testing)
- [ ] Add basic logging configuration
- [ ] Test local Flask server startup

### Checkpoint 2.3: Email Parser Implementation
- [ ] Create `email_parser.py` with email parsing:
  ```python
  class EmailParser:
      def parse_recruiter_email(self, email_message):
          # Extract recruiter name from sender
          # Extract company from email domain or signature
          # Extract position from subject/body keywords
          # Extract location from common patterns
          # Return structured data
  ```
- [ ] Implement parsing for Gmail message objects
- [ ] Add regex patterns for:
  - Company extraction from domains and signatures
  - Job titles in subject lines and content
  - Location patterns (City, State format)
  - Name extraction from email headers
- [ ] Test with sample Gmail messages

---

## Phase 3: Notion Integration

### Checkpoint 3.1: Notion API Client
- [ ] Create `notion_client.py` with Notion API wrapper
- [ ] Implement authentication with integration tokens
- [ ] Create method to add database entries:
  ```python
  def create_recruiter_entry(self, database_id, recruiter_data):
      # Format data for Notion API
      # Create new page in database
      # Return page ID for tracking
  ```
- [ ] Test connection to Notion workspace

### Checkpoint 3.2: Database Schema Mapping
- [ ] Define Notion database properties:
  - Recruiter Name (Title)
  - Company (Text)
  - Position (Text) 
  - Location (Text)
  - Status (Select: "Recruiter Screen", "Phone Screen", "Interview", "Rejected", "Offer")
  - Date Received (Date)
  - Email (Email)
- [ ] Create Notion database template
- [ ] Test property mapping and data insertion

### Checkpoint 3.3: Background Scheduler
- [ ] Create `scheduler.py` with APScheduler:
  ```python
  from apscheduler.schedulers.background import BackgroundScheduler
  
  def setup_email_checker():
      scheduler = BackgroundScheduler()
      scheduler.add_job(
          func=check_all_users_emails,
          trigger="interval",
          minutes=5,  # Check every 5 minutes
          id='email_checker'
      )
      scheduler.start()
  ```
- [ ] Implement periodic email checking for all users
- [ ] Add job logging and error handling
- [ ] Test scheduler with Flask app

### Checkpoint 3.4: End-to-End Integration
- [ ] Connect Gmail checker → email parser → Notion client → database logging
- [ ] Implement duplicate prevention using Gmail message IDs
- [ ] Add comprehensive error handling and retry logic
- [ ] Test complete flow with real Gmail labels and emails

---

## Phase 4: Deployment and Testing

### Checkpoint 4.1: Local Testing
- [ ] Test Gmail IMAP connection with app passwords
- [ ] Create test Gmail labels and emails
- [ ] Test complete email processing pipeline locally
- [ ] Verify Notion entries are created correctly
- [ ] Test scheduler and periodic checking
- [ ] Test error scenarios and logging

### Checkpoint 4.2: Production Deployment
**Option A: Railway**
- [ ] Create Railway account
- [ ] Connect GitHub repository
- [ ] Configure environment variables
- [ ] Set up persistent volume for SQLite database
- [ ] Deploy and test webhook URL

**Option B: Render**
- [ ] Create Render account
- [ ] Connect GitHub repository  
- [ ] Configure environment variables
- [ ] Set up persistent disk for database
- [ ] Deploy and verify webhook accessibility

### Checkpoint 4.3: Final Configuration
- [ ] Test Gmail connections work in production environment
- [ ] Verify Notion integration works in production
- [ ] Test scheduled email checking in production
- [ ] Set up basic monitoring/logging
- [ ] Document Gmail setup process for users

---

## Phase 5: Monitoring and Maintenance

### Checkpoint 5.1: Logging and Debugging
- [ ] Implement comprehensive logging
- [ ] Add email processing metrics
- [ ] Create simple status endpoint for health checks
- [ ] Set up log rotation

### Checkpoint 5.2: User Onboarding
- [ ] Document setup process for new users
- [ ] Create instructions for:
  - Setting up Gmail App Passwords (with 2FA)
  - Creating Gmail labels for recruiting emails
  - Setting up Gmail filters to auto-label recruiting emails
  - Getting Notion integration token
  - Finding Notion database ID
- [ ] Test onboarding process with second user

---

## Deployment Considerations

### Environment Variables Needed:
```
FLASK_ENV=production
DATABASE_PATH=/app/data/database.db
CHECK_INTERVAL_MINUTES=5
```

### Railway Deployment Steps:
1. Connect GitHub repo to Railway
2. Add environment variables in Railway dashboard
3. Configure start command: `python app.py`
4. Set up persistent volume for database storage
5. Deploy and test production environment
6. Verify scheduled email checking works

### Testing Checklist:
- [ ] Gmail IMAP connections work with app passwords
- [ ] Email parsing extracts correct recruiter data
- [ ] Notion entries created with correct data
- [ ] Scheduled checking runs every 5 minutes
- [ ] Duplicate prevention using Gmail message IDs
- [ ] Error handling works (Gmail timeouts, API failures)
- [ ] Database logging captures all attempts and errors

---

## Success Criteria:
1. Label recruiting emails in Gmail → Notion entry created automatically within 5 minutes
2. Parsed data includes: recruiter name, company, position, location
3. All entries default to "Recruiter Screen" status
4. System handles 2-3 concurrent users with separate Gmail accounts
5. Deployed with persistent scheduling and data storage
6. Comprehensive error handling and logging
7. No duplicate entries using Gmail message ID tracking

## User Workflow:
1. **Setup Gmail**: Enable 2FA, create app password, create "Recruiters" label
2. **Setup Filters**: Auto-label recruiting emails (keywords: "opportunity", "role", "position")
3. **Configure App**: Add Gmail credentials and Notion tokens to config
4. **Deploy**: System automatically checks Gmail every 5 minutes
5. **Monitor**: Check Notion database for new recruiter entries

---

## Future Enhancements (Post-MVP):
- Web interface for user management
- AI-powered parsing improvements  
- Email template detection
- Duplicate detection and merging
- Status update workflows
- Analytics and reporting