# YouTube Downloader - Troubleshooting Guide

## Common Issues and Solutions

### 1. "Sign in to confirm you're not a bot" Error

**Problem**: YouTube is detecting automated requests and blocking them.

**Why it happens**:
- YouTube has advanced bot detection mechanisms
- High traffic from cloud hosting providers (like Render) triggers these protections
- Popular videos (like "Never Gonna Give You Up") are more heavily protected

**Solutions**:

#### Immediate workarounds:
1. **Try different videos**: Less popular videos are less likely to trigger bot detection
2. **Wait and retry**: YouTube's bot detection is temporary, try again in 15-30 minutes
3. **Use different URLs**: Try videos from different channels or time periods

#### Technical solutions implemented:
1. **Enhanced User-Agent spoofing**: Updated to latest Chrome headers
2. **Multiple fallback methods**: App tries 3 different extraction approaches
3. **Better error handling**: User-friendly error messages instead of technical errors

#### For developers:
```python
# The app now includes these anti-bot measures:
ydl_opts = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'http_headers': {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Sec-Fetch-Dest': 'document',
        # ... more headers
    },
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'hls'],
            'player_skip': ['configs', 'webpage']
        }
    }
}
```

### 2. Download Failures

**Common causes**:
- Video is private or age-restricted
- Video has been removed or made unavailable
- Geographic restrictions
- Copyright restrictions

**Solutions**:
- Check if the video is publicly accessible
- Try downloading in audio format instead of video
- Use videos from your own channel or creative commons videos

### 3. Slow Performance

**Causes**:
- Large video files
- Server limitations on free hosting (Render free tier)
- Network latency

**Solutions**:
- Choose lower quality formats
- Download audio instead of video for faster processing
- Consider upgrading to paid hosting for better performance

### 4. App Won't Start

**Check these files**:
1. `requirements.txt` - ensure all dependencies are listed
2. `render.yaml` - verify build and start commands
3. `main.py` - check if it imports app correctly

**Common fixes**:
```bash
# Locally test the app
python main.py

# Check for syntax errors
python -m py_compile *.py
```

## Testing the Application

### Local Testing
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python main.py

# 3. Test yt-dlp functionality
python -c "import yt_dlp; print(yt_dlp.version.__version__)"
```

### Production Testing
1. Visit: `https://your-app.onrender.com/test_ytdlp`
2. Check the response for yt-dlp status
3. Try downloading a simple, public video

## Best Practices for Users

### Choosing Videos to Download
✅ **Good choices**:
- Educational content
- Creative Commons videos
- Music videos from independent artists
- Your own uploaded videos

❌ **Avoid**:
- Highly popular viral videos
- Music from major labels
- Recently uploaded trending content

### Optimal Usage Times
- Try during off-peak hours (late night/early morning in your timezone)
- Avoid peak YouTube usage times (evening in major markets)

## API Endpoints for Testing

### Test yt-dlp functionality
```
GET /test_ytdlp
```
Returns yt-dlp version and basic functionality test.

### Get video information
```
POST /video_info
Content-Type: application/json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

### Download video
```
POST /download
Content-Type: application/json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "format": "mp4",
  "quality": "best"
}
```

## Deployment Notes

### Render Specific Issues
- Free tier has limited resources
- IP addresses may be flagged by YouTube
- Cold starts can cause timeouts

### Environment Variables
No special environment variables required for basic functionality.

## Getting Help

If you continue experiencing issues:

1. **Check the logs**: In Render dashboard, check the deployment logs
2. **Test locally**: Verify the issue exists locally vs. only in production
3. **Check YouTube status**: Sometimes YouTube's API has outages
4. **Try different videos**: Test with multiple different video URLs

## Legal Notice

This tool is for educational purposes and personal use only. Users are responsible for complying with YouTube's Terms of Service and applicable copyright laws. Only download content you have permission to download.
