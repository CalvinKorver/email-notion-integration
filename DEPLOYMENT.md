# Deployment Guide

## Railway Deployment

1. **Connect Repository**
   - Go to Railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Select this repository

2. **Set Environment Variables**
   - In Railway dashboard, go to Variables tab
   - Add all variables from `.env.production`

3. **Deploy**
   - Railway will automatically build and deploy
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

Copy these from `.env.production`:
- `DATABASE_PATH`
- `FLASK_ENV`
- `FLASK_HOST`
- `FLASK_PORT`
- `EMAIL_LOOKBACK_DAYS`
- `CHECK_INTERVAL_MINUTES`
- `GMAIL_EMAIL`
- `GMAIL_PASSWORD`
- `GMAIL_LABEL`
- `USER_NAME`
- `NOTION_API_KEY`
- `DATABASE_ID`

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