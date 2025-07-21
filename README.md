# Recruiter Email Tracker

A Python Flask application that monitors Gmail inboxes for recruiter emails and automatically creates entries in Notion databases. The system is designed to streamline job search tracking by parsing recruiter outreach and organizing it in a structured format.

## Features

- **Automated Email Monitoring**: Periodically checks Gmail inboxes for new recruiter emails
- **Smart Email Parsing**: Extracts recruiter information, company details, and job positions
- **Notion Integration**: Automatically creates structured entries in your Notion database
- **Multi-user Support**: Supports multiple users with individual configurations
- **Database Logging**: Tracks all processed emails and Notion entries
- **Flexible Scheduling**: Configurable check intervals with manual trigger options

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Email**: Gmail SMTP with App Passwords
- **Integration**: Notion API
- **Deployment**: Railway/Render compatible
- **Scheduling**: APScheduler

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd email-notion-integration
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root (see `.env.example` for reference):

```bash
cp .env.example .env
```

Edit the `.env` file with your credentials:

```env
# Flask Configuration
FLASK_ENV=development
DATABASE_PATH=database.db

# Gmail Configuration
GMAIL_EMAIL=your.email@gmail.com
GMAIL_PASSWORD=your_gmail_app_password
GMAIL_LABEL=Recruiters

# Notion API
NOTION_API_KEY=your_notion_integration_token
DATABASE_ID=your_notion_database_id

# Check Configuration
CHECK_INTERVAL_MINUTES=20
EMAIL_LOOKBACK_DAYS=3

# User Configuration
USER_NAME=Your Name
```

### 5. Database Setup

Initialize the database:

```bash
python scripts/setup_db.py
```

### 6. User Configuration

Seed your user data:

```bash
python scripts/seed_user.py
```

You'll be prompted to enter:
- Your name
- Gmail address
- Notion database ID
- Check interval (in minutes)

### 7. Gmail App Password Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Go to [Google Account Settings](https://myaccount.google.com/security)
3. Under "Signing in to Google", click "App passwords"
4. Generate a new app password for "Mail"
5. Copy the 16-character password and add it to your `.env` as `GMAIL_PASSWORD`
6. Create a Gmail label called "Recruiters" (or update `GMAIL_LABEL` in `.env`)

### 8. Notion Setup

1. Create a [Notion integration](https://www.notion.so/my-integrations)
2. Copy the Internal Integration Token
3. Add it to your `.env` as `NOTION_API_KEY`
4. Create or select a database in Notion
5. Share the database with your integration
6. Copy the database ID from the URL

### 9. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## API Endpoints

- `GET /` - Health check and status
- `GET /status` - Scheduler and system status
- `POST /start` - Start email monitoring
- `POST /stop` - Stop email monitoring
- `POST /check` - Trigger manual email check
- `GET /logs` - View recent application logs

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Run integration tests:

```bash
python -m pytest integration_tests/
```

## Deployment

The application is configured for deployment on Railway or Render:

### Railway
```bash
railway login
railway link
railway deploy
```

### Render
Connect your GitHub repository to Render and it will automatically deploy using the `render.yaml` configuration.

## Database Migrations

Manage database schema changes:

```bash
# Check migration status
python migrate.py status

# Run pending migrations
python migrate.py migrate

# Create new migration
python migrate.py create --name add_new_feature
```

## Configuration

User configurations are stored in the database. Each user has:
- Name and email
- Notion database ID and API token
- Gmail credentials
- Check interval preferences

## Troubleshooting

### Common Issues

1. **Gmail Authentication**: Ensure OAuth consent screen is configured and credentials are valid
2. **Notion Permissions**: Verify the integration has access to your database
3. **Database Errors**: Check file permissions and disk space
4. **Scheduling Issues**: Verify APScheduler configuration and check logs

### Logs

Application logs are written to `app.log` and console. Check logs for detailed error information:

```bash
tail -f app.log
```
