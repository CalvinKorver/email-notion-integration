# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Recruiter Email Tracker project - a Python Flask application that processes forwarded recruiter emails via Mailgun webhooks and automatically creates entries in Notion databases. The system is designed to be hardcoded for a few users initially.

## Tech Stack & Architecture

- **Backend**: Python/Flask web application
- **Database**: SQLite (local file storage)
- **Email Processing**: Mailgun webhooks for receiving forwarded emails
- **Integration**: Notion API for creating database entries
- **Deployment**: Railway or Render with persistent storage

## Core Components

Based on the implementation plan, the main application components are:

- `app.py` - Main Flask application with webhook endpoints
- `email_parser.py` - Email content parsing logic to extract recruiter data
- `notion_client.py` - Notion API wrapper for database operations
- `database.py` - SQLite operations and data persistence
- `config.py` - Configuration with hardcoded user data
- `setup_db.py` - Database initialization script

## Database Schema

Two main tables:
- `users` - Stores user configuration (name, email, Notion tokens, database IDs)
- `recruiter_contacts` - Stores parsed recruiter data and tracks Notion entries

## Key Workflows

1. **Email Processing Pipeline**: Mailgun webhook → Flask endpoint → Email parser → Notion API → SQLite logging
2. **Data Extraction**: Parse recruiter name, company, position, location from email content
3. **Notion Integration**: Create structured entries with status defaulting to "Recruiter Screen"

## Development Commands

Since this is a Python Flask project without existing package configuration:

```bash
# Set up development environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run Flask development server
python app.py

# Initialize database
python setup_db.py
```

## Environment Variables

Required for deployment:
- `MAILGUN_API_KEY` - Mailgun API authentication
- `MAILGUN_WEBHOOK_SIGNING_KEY` - Webhook signature verification
- `FLASK_ENV` - Environment setting
- `DATABASE_PATH` - SQLite database file location

## Testing Approach

- Use ngrok for local webhook testing with Mailgun
- Test complete email processing pipeline end-to-end
- Verify Notion integration creates proper database entries
- Test error scenarios and logging functionality
- Every single new file should have testing to accompany it. The testing should result in unit tests or integration tests that are put in tests