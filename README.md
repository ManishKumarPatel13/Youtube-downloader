# YouTube Downloader - Render Deployment Guide

## Features
- Search and download YouTube videos
- Download in multiple formats (MP4, MP3)
- Multiple quality options
- Download files directly to your local desktop
- Real-time progress tracking
- Download history

## Deployment on Render

### Prerequisites
1. GitHub account
2. Render account (free tier available)

### Step 1: Push to GitHub
1. Create a new repository on GitHub
2. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/youtube-downloader.git
   git push -u origin main
   ```

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Use these settings:
   - **Name**: `youtube-downloader`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
   - **Instance Type**: Free tier is sufficient for testing

### Step 3: Add Database (Optional - for production)
1. Create a PostgreSQL database on Render
2. Add the `DATABASE_URL` environment variable to your web service
3. The app will automatically use PostgreSQL in production

### Step 4: Environment Variables
Add these environment variables in Render:
- `SESSION_SECRET`: Generate a random secret key
- `DATABASE_URL`: (automatically set if using Render's PostgreSQL)

## How Downloads Work

### Local Desktop Downloads
1. **Search**: Use the search box to find YouTube videos
2. **Select Format**: Choose video (MP4) or audio (MP3)
3. **Choose Quality**: Select from available quality options
4. **Download**: Click the download button
5. **Save to Desktop**: The file will be downloaded directly to your browser's download folder

### Download Process
1. The app processes the YouTube URL
2. Extracts video/audio in the selected format
3. Serves the file directly to your browser
4. Browser downloads the file to your local machine (usually Downloads folder)

### File Storage
- On Render's free tier, files are temporarily stored on the server
- Files are automatically cleaned up after serving
- No persistent storage is used to keep within free tier limits

## Local Development

### Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

Visit `http://localhost:5000` in your browser.

## Production Notes

### Render Free Tier Limitations
- 512MB RAM
- Sleeps after 15 minutes of inactivity
- Limited monthly hours
- Ephemeral file system

### For Heavy Usage
Consider upgrading to a paid plan or using:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS/GCP/Azure

## Troubleshooting

### Common Issues
1. **App sleeps**: Free tier apps sleep after inactivity
2. **Download fails**: Check YouTube URL format
3. **Large files**: May timeout on free tier

### Solutions
- Use shorter videos for testing
- Consider paid hosting for production use
- Monitor logs in Render dashboard
