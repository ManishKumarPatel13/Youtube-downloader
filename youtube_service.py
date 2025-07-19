import os
import yt_dlp
import re
from datetime import datetime
from app import db, socketio
from models import Download
from flask_socketio import emit
import logging

class YouTubeService:
    def __init__(self):
        self.downloads_dir = "downloads"
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    def search_videos(self, query, max_results=20):
        """Search for YouTube videos"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(
                    f"ytsearch{max_results}:{query}",
                    download=False
                )
                
                results = []
                if search_results and 'entries' in search_results:
                    for entry in search_results['entries']:
                        if entry:
                            # Get more detailed info for each video
                            try:
                                video_info = self.get_video_info(f"https://www.youtube.com/watch?v={entry['id']}")
                                if video_info:
                                    results.append(video_info)
                            except:
                                # Fallback to basic info
                                results.append({
                                    'id': entry.get('id'),
                                    'title': entry.get('title', 'Unknown Title'),
                                    'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                                    'thumbnail': entry.get('thumbnails', [{}])[-1].get('url', ''),
                                    'duration': self._format_duration(entry.get('duration')),
                                    'uploader': entry.get('uploader', 'Unknown'),
                                    'view_count': entry.get('view_count', 0)
                                })
                
                return results[:max_results]
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            return []
    
    def get_video_info(self, url):
        """Get detailed information about a YouTube video"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return None
                
                # Get available formats
                formats = []
                if 'formats' in info:
                    seen_formats = set()
                    for fmt in info['formats']:
                        if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                            # Video + Audio formats
                            height = fmt.get('height')
                            if height and height not in seen_formats:
                                formats.append({
                                    'format_id': fmt['format_id'],
                                    'ext': fmt.get('ext', 'mp4'),
                                    'quality': f"{height}p",
                                    'type': 'video',
                                    'filesize': fmt.get('filesize')
                                })
                                seen_formats.add(height)
                        elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                            # Audio only formats
                            abr = fmt.get('abr')
                            if abr:
                                formats.append({
                                    'format_id': fmt['format_id'],
                                    'ext': fmt.get('ext', 'mp3'),
                                    'quality': f"{int(abr)}kbps",
                                    'type': 'audio',
                                    'filesize': fmt.get('filesize')
                                })
                
                # Sort formats by quality (highest first)
                video_formats = sorted([f for f in formats if f['type'] == 'video'], 
                                     key=lambda x: int(x['quality'][:-1]), reverse=True)
                audio_formats = sorted([f for f in formats if f['type'] == 'audio'], 
                                     key=lambda x: int(x['quality'][:-4]), reverse=True)
                
                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'url': url,
                    'thumbnail': info.get('thumbnail'),
                    'duration': self._format_duration(info.get('duration')),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', '')[:500] + '...' if info.get('description') and len(info.get('description', '')) > 500 else info.get('description', ''),
                    'video_formats': video_formats[:5],  # Top 5 video qualities
                    'audio_formats': audio_formats[:3]   # Top 3 audio qualities
                }
        except Exception as e:
            logging.error(f"Video info error: {str(e)}")
            return None
    
    def download_video(self, download_id, url, format_type='video', quality='best'):
        """Download a YouTube video with progress tracking"""
        download = Download.query.get(download_id)
        if not download:
            return
        
        try:
            download.status = 'downloading'
            db.session.commit()
            
            # Emit initial status
            socketio.emit('download_progress', {
                'download_id': download_id,
                'status': 'downloading',
                'progress': 0
            })
            
            def progress_hook(d):
                if d['status'] == 'downloading':
                    try:
                        downloaded = d.get('downloaded_bytes', 0)
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        
                        if total > 0:
                            progress = int((downloaded / total) * 100)
                            download.progress = progress
                            db.session.commit()
                            
                            socketio.emit('download_progress', {
                                'download_id': download_id,
                                'status': 'downloading',
                                'progress': progress,
                                'downloaded': downloaded,
                                'total': total,
                                'speed': d.get('speed', 0)
                            })
                    except Exception as e:
                        logging.error(f"Progress hook error: {str(e)}")
                
                elif d['status'] == 'finished':
                    download.file_path = d['filename']
                    download.status = 'completed'
                    download.progress = 100
                    download.completed_at = datetime.utcnow()
                    db.session.commit()
                    
                    socketio.emit('download_progress', {
                        'download_id': download_id,
                        'status': 'completed',
                        'progress': 100,
                        'file_path': d['filename']
                    })
            
            # Set up download options
            if format_type == 'audio':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.downloads_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                # Video format
                if quality == 'best':
                    format_selector = 'best[height<=720]'
                elif quality.endswith('p'):
                    height = quality[:-1]
                    format_selector = f'best[height<={height}]'
                else:
                    format_selector = 'best'
                
                ydl_opts = {
                    'format': format_selector,
                    'outtmpl': os.path.join(self.downloads_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                }
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            download.status = 'failed'
            download.error_message = str(e)
            db.session.commit()
            
            socketio.emit('download_progress', {
                'download_id': download_id,
                'status': 'failed',
                'error': str(e)
            })
    
    def _format_duration(self, duration):
        """Format duration from seconds to MM:SS or HH:MM:SS"""
        if not duration:
            return "Unknown"
        
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
