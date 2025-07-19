import os
import json
import threading
from datetime import datetime
from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app, db
from models import Download
from youtube_service import YouTubeService
import logging

youtube_service = YouTubeService()

@app.route('/')
def index():
    recent_downloads = Download.query.order_by(Download.created_at.desc()).limit(10).all()
    return render_template('index.html', recent_downloads=recent_downloads)

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
        
        info = youtube_service.get_video_info(url)
        if not info:
            return jsonify({'error': 'Could not extract video information'}), 400
        
        return jsonify(info)
    except Exception as e:
        logging.error(f"Video info error: {str(e)}")
        return jsonify({'error': 'Failed to get video information. Please check the URL.'}), 500

@app.route('/download', methods=['POST'])
def start_download():
    try:
        data = request.json
        url = data.get('url', '').strip()
        format_type = data.get('format', 'video')  # 'video' or 'audio'
        quality = data.get('quality', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Get video info first
        video_info = youtube_service.get_video_info(url)
        if not video_info:
            return jsonify({'error': 'Could not extract video information'}), 400
        
        # Create download record
        download = Download(
            video_id=video_info['id'],
            title=video_info['title'],
            url=url,
            format_selected=format_type,
            quality=quality,
            status='pending'
        )
        db.session.add(download)
        db.session.commit()
        
        # Start download in background thread
        thread = threading.Thread(
            target=youtube_service.download_video,
            args=(download.id, url, format_type, quality)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'download_id': download.id,
            'message': 'Download started successfully'
        })
        
    except Exception as e:
        logging.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Failed to start download. Please try again.'}), 500

@app.route('/download_status/<int:download_id>')
def download_status(download_id):
    download = Download.query.get_or_404(download_id)
    return jsonify(download.to_dict())

@app.route('/downloads')
def download_history():
    downloads = Download.query.order_by(Download.created_at.desc()).all()
    return jsonify([d.to_dict() for d in downloads])

@app.route('/download_file/<int:download_id>')
def download_file(download_id):
    download = Download.query.get_or_404(download_id)
    
    if download.status != 'completed' or not download.file_path:
        flash('File not available for download', 'error')
        return redirect(url_for('index'))
    
    if not os.path.exists(download.file_path):
        flash('File not found', 'error')
        return redirect(url_for('index'))
    
    return send_file(
        download.file_path,
        as_attachment=True,
        download_name=os.path.basename(download.file_path)
    )

# Progress polling endpoint for real-time updates
@app.route('/poll_progress/<int:download_id>')
def poll_progress(download_id):
    download = Download.query.get_or_404(download_id)
    return jsonify({
        'download_id': download_id,
        'status': download.status,
        'progress': download.progress,
        'error': download.error_message
    })
