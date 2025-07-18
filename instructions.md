# Recruiter Email Tracker - Implementation Plan

## Project Overview
A simple Python Flask app that processes forwarded recruiter emails and creates entries in Notion databases. Hardcoded for a few users initially.

## Tech Stack
- **Backend**: Python/Flask
- **Database**: SQLite (local file)
- **Email**: Mailgun webhooks
- **Integration**: Notion API
- **Deployment**: Railway/Render (with persistent storage)

## Project Structure
```
recruiter-tracker/
├── app.py                 # Main Flask application
├── email_parser.py        # Email content parsing logic
├── notion_client.py       # Notion API wrapper
├── database.py           # SQLite operations
├── config.py             # Configuration and hardcoded users
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
      notion_token TEXT,
      notion_database_id TEXT,
      mailgun_email TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE recruiter_contacts (
      id INTEGER PRIMARY KEY,
      user_id INTEGER,
      recruiter_name TEXT,
      recruiter_email TEXT,
      company TEXT,
      position TEXT,
      location TEXT,
      status TEXT DEFAULT 'Recruiter Screen',
      date_received TIMESTAMP,
      notion_page_id TEXT,
      raw_email_data TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
          'email': 'your.personal@email.com',
          'notion_token': 'secret_token_here',
          'notion_database_id': 'database_id_here',
          'mailgun_email': 'user1@yourdomain.com'
      },
      # Add 2-3 more users as needed
  ]
  ```
- [ ] Set up environment variables for sensitive data
- [ ] Create `.env` file for local development

---

## Phase 2: Email Processing Core

### Checkpoint 2.1: Basic Flask App
- [ ] Create `app.py` with basic Flask setup
- [ ] Implement health check endpoint: `GET /health`
- [ ] Implement webhook endpoint: `POST /webhook/email`
- [ ] Add basic logging configuration
- [ ] Test local Flask server startup

### Checkpoint 2.2: Email Parser Implementation
- [ ] Create `email_parser.py` with basic text parsing:
  ```python
  class EmailParser:
      def parse_recruiter_email(self, email_data):
          # Extract recruiter name from sender
          # Extract company from email domain or content
          # Extract position from subject/body keywords
          # Extract location from common patterns
          # Return structured data
  ```
- [ ] Implement regex patterns for:
  - Company extraction from email domains
  - Job titles in subject lines
  - Location patterns (City, State format)
  - Name extraction from email addresses
- [ ] Test with sample email data

### Checkpoint 2.3: Mailgun Integration
- [ ] Set up Mailgun account and domain
- [ ] Configure webhook URL pointing to your app
- [ ] Implement webhook signature verification
- [ ] Test email forwarding to unique addresses
- [ ] Handle Mailgun webhook data format

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

### Checkpoint 3.3: End-to-End Integration
- [ ] Connect email parser → Notion client → database logging
- [ ] Implement error handling and retry logic
- [ ] Add duplicate detection (same recruiter email)
- [ ] Test complete flow with real forwarded emails

---

## Phase 4: Deployment and Testing

### Checkpoint 4.1: Local Testing
- [ ] Test complete email processing pipeline locally
- [ ] Use ngrok to expose local webhook for Mailgun testing
- [ ] Verify Notion entries are created correctly
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
- [ ] Update Mailgun webhook URL to production endpoint
- [ ] Test email forwarding to production system
- [ ] Verify Notion integration works in production
- [ ] Set up basic monitoring/logging
- [ ] Document email addresses for users

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
  - Getting Notion integration token
  - Finding Notion database ID
  - Setting up email forwarding
- [ ] Test onboarding process with second user

---

## Deployment Considerations

### Environment Variables Needed:
```
MAILGUN_API_KEY=your_mailgun_api_key
MAILGUN_WEBHOOK_SIGNING_KEY=webhook_signing_key
FLASK_ENV=production
DATABASE_PATH=/app/data/database.db
```

### Railway Deployment Steps:
1. Connect GitHub repo to Railway
2. Add environment variables in Railway dashboard
3. Configure start command: `python app.py`
4. Set up persistent volume for database storage
5. Deploy and get production URL
6. Update Mailgun webhook configuration

### Testing Checklist:
- [ ] Email forwarding works end-to-end
- [ ] Notion entries created with correct data
- [ ] Error handling works (malformed emails, API failures)
- [ ] Database logging captures all attempts
- [ ] Production webhook receives emails properly

---

## Success Criteria:
1. Forward recruiter email → Notion entry created automatically
2. Parsed data includes: recruiter name, company, position, location
3. All entries default to "Recruiter Screen" status
4. System handles 2-3 concurrent users
5. Deployed and accessible via web hook
6. Basic error handling and logging in place

---

## Future Enhancements (Post-MVP):
- Web interface for user management
- AI-powered parsing improvements  
- Email template detection
- Duplicate detection and merging
- Status update workflows
- Analytics and reporting