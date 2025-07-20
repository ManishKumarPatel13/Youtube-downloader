#!/bin/bash

# YouTube Downloader - Deployment Script
echo "🚀 YouTube Downloader - Deploying Bot Detection Fixes"
echo "======================================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "   Initialize git first: git init"
    exit 1
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "📝 Found changes to commit..."
    
    # Add all changes
    git add .
    
    # Commit with a descriptive message
    git commit -m "🔧 Fix YouTube bot detection issues

- Enhanced yt-dlp configuration with latest Chrome headers
- Added multiple fallback extraction methods
- Improved error handling with user-friendly messages
- Fixed syntax errors in routes.py and youtube_service.py
- Added comprehensive anti-bot measures
- Created troubleshooting guide and verification tools

Resolves video extraction errors in production environment."
    
    echo "✅ Changes committed successfully"
else
    echo "ℹ️  No changes to commit"
fi

# Push to remote
echo "📤 Pushing to GitHub..."
if git push origin main; then
    echo "✅ Successfully pushed to GitHub"
    echo ""
    echo "🎯 Deployment Status:"
    echo "   - Code pushed to GitHub ✅"
    echo "   - Render will auto-deploy ⏳"
    echo "   - Check deployment: https://dashboard.render.com"
    echo ""
    echo "🧪 Testing Steps:"
    echo "   1. Wait for Render deployment to complete"
    echo "   2. Test: https://youtube-downloader-ds68.onrender.com/test_ytdlp"
    echo "   3. Try the main app with less popular YouTube videos"
    echo "   4. Check improved error messages"
    echo ""
    echo "📚 Resources:"
    echo "   - Troubleshooting: Read TROUBLESHOOTING.md"
    echo "   - Verification: Run 'python verify_deployment.py'"
else
    echo "❌ Failed to push to GitHub"
    echo "   Check your git remote configuration"
    exit 1
fi
