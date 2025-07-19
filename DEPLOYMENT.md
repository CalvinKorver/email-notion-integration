# Deployment Guide

## Railway Deployment

1. **Connect Repository**
   - Go to Railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Select this repository

2. **Set Environment Variables**
   - In Railway dashboard, go to Variables tab
   - Add all required variables (see list below)
   - **IMPORTANT**: Make sure `DATABASE_PATH="/data/database.db"` for persistent storage

3. **Add Volume for Database Persistence**
   - In Railway dashboard, go to Settings
   - Click "Volume" and add a new volume
   - Mount path: `/data`
   - This ensures your SQLite database persists across deployments

4. **Deploy**
   - Railway will automatically build and deploy using `nixpacks.toml`
   - Database tables will be created automatically on first deploy
   - Your app will be available at the generated URL

## Render Deployment

1. **Connect Repository**
   - Go to Render.com
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configuration**
   - Render will detect the `render.yaml` file
   - Set environment variables in the dashboard

3. **Deploy**
   - Render will build and deploy automatically
   - Your app will be available at the generated URL

## Environment Variables Required

### Railway-Specific Variables
- `DATABASE_PATH="/data/database.db"` (for persistent storage)
- `PYTHONUNBUFFERED="1"` (already set in railway.toml)

### Application Variables
Copy these from your local `.env` file:
- `FLASK_ENV="production"`
- `CHECK_INTERVAL_MINUTES="30"` (or your preferred interval)
- `EMAIL_LOOKBACK_DAYS="3"`
- `GMAIL_EMAIL` (your Gmail address)
- `GMAIL_PASSWORD` (Gmail app password)
- `GMAIL_LABEL` (e.g., "Recruiters")
- `USER_NAME` (your name)
- `NOTION_API_KEY` (your Notion integration token)
- `DATABASE_ID` (your Notion database ID)

### Notes
- `PORT` is automatically provided by Railway
- `FLASK_HOST` defaults to `0.0.0.0` (correct for Railway)
- Database will be automatically initialized on first deployment

## Testing Production Deploy

After deployment, test these endpoints:
- `GET /` - Basic status
- `GET /health` - Health check
- `POST /check-emails` - Manual email check
- `GET /scheduler/status` - Scheduler status

## Monitoring

- Check logs in your deployment platform
- Monitor the `/health` endpoint
- Set up alerts for failed email checks