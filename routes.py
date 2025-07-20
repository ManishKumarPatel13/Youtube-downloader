import os
import tempfile
from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app
from youtube_service import YouTubeService
import logging

youtube_service = YouTubeService()

@app.route('/')
def index():
    # No database - no download history to show
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_videos():
    try:
        query = request.json.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        results = youtube_service.search_videos(query)
        return jsonify({'results': results})
    except Exception as e:
        logging.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Failed to search videos. Please try again.'}), 500

@app.route('/video_info', methods=['POST'])
def get_video_info():
    try:
        url = request.json.get('url', '').strip()
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate YouTube URL format
        if 'youtube.com/watch' not in url and 'youtu.be/' not in url:
            return jsonify({'error': 'Please enter a valid YouTube URL'}), 400
        
        info = youtube_service.get_video_info(url)
        if not info:
            return jsonify({'error': 'Could not extract video information. Please check the URL or try again later.'}), 400
        
        return jsonify(info)
    except Exception as e:
        logging.error(f"Video info error: {str(e)}")
        return jsonify({'error': 'Failed to get video information. The video may be private, unavailable, or blocked.'}), 500

@app.route('/download', methods=['POST'])
def download_video():
    """Direct download without database tracking"""
    try:
        data = request.json
        url = data.get('url', '').strip()
        format_type = data.get('format', 'video')  # 'video' or 'audio'
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Download directly and return file
        file_path = youtube_service.download_video_direct(url, format_type, quality)
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'Download failed'}), 500
        
        # Return the file directly
        filename = os.path.basename(file_path)
        
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception:
                pass
            return response
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
        except Exception as e:
        logging.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed. Please try again.'}), 500

@app.route('/test_ytdlp', methods=['GET'])
def test_ytdlp():
    """Test endpoint to check yt-dlp functionality"""
    try:
        import yt_dlp
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - always available
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            
        return jsonify({
            'status': 'success',
            'yt_dlp_version': yt_dlp.version.__version__,
            'test_video_title': info.get('title', 'Unknown') if info else 'Failed to extract'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'yt_dlp_version': 'unknown'
        })