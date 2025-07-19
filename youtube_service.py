import os
import yt_dlp
import re
from datetime import datetime
from app import db
from models import Download
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
                            # Use basic info to avoid timeouts
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
                
                # Get available formats - enhanced to show more options
                video_formats = []
                audio_formats = []
                
                if 'formats' in info:
                    seen_video_heights = set()
                    seen_audio_bitrates = set()
                    
                    for fmt in info['formats']:
                        # Video formats (with or without audio)
                        if fmt.get('vcodec') != 'none' and fmt.get('height'):
                            height = fmt.get('height')
                            if height not in seen_video_heights:
                                video_formats.append({
                                    'format_id': fmt['format_id'],
                                    'ext': fmt.get('ext', 'mp4'),
                                    'quality': f"{height}p",
                                    'type': 'video',
                                    'filesize': fmt.get('filesize'),
                                    'fps': fmt.get('fps'),
                                    'vcodec': fmt.get('vcodec', 'unknown')
                                })
                                seen_video_heights.add(height)
                        
                        # Audio only formats
                        elif fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                            abr = fmt.get('abr')
                            if abr and abr not in seen_audio_bitrates:
                                audio_formats.append({
                                    'format_id': fmt['format_id'],
                                    'ext': fmt.get('ext', 'mp3'),
                                    'quality': f"{int(abr)}kbps",
                                    'type': 'audio',
                                    'filesize': fmt.get('filesize'),
                                    'acodec': fmt.get('acodec', 'unknown')
                                })
                                seen_audio_bitrates.add(abr)
                
                # Sort formats by quality (highest first) and take more options
                video_formats = sorted(video_formats, key=lambda x: int(x['quality'][:-1]), reverse=True)
                audio_formats = sorted(audio_formats, key=lambda x: int(x['quality'][:-4]), reverse=True)
                
                # Add standard quality options if not present
                standard_qualities = [2160, 1440, 1080, 720, 480, 360, 240, 144]
                for quality in standard_qualities:
                    if not any(f['quality'] == f'{quality}p' for f in video_formats):
                        video_formats.append({
                            'format_id': f'best[height<={quality}]',
                            'ext': 'mp4',
                            'quality': f'{quality}p',
                            'type': 'video',
                            'filesize': None
                        })
                
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
                    'video_formats': video_formats[:10],  # Top 10 video qualities
                    'audio_formats': audio_formats[:5]    # Top 5 audio qualities
                }
        except Exception as e:
            logging.error(f"Video info error: {str(e)}")
            return None
    
    def download_video(self, download_id, url, format_type='video', quality='best'):
        """Download a YouTube video with progress tracking"""
        from app import app
        with app.app_context():
            download = Download.query.get(download_id)
            if not download:
                return
        
            try:
                download.status = 'downloading'
                db.session.commit()
            
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        try:
                            downloaded = d.get('downloaded_bytes', 0)
                            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                            
                            if total > 0:
                                progress = int((downloaded / total) * 100)
                                download.progress = progress
                                db.session.commit()
                        except Exception as e:
                            logging.error(f"Progress hook error: {str(e)}")
                    
                    elif d['status'] == 'finished':
                        download.file_path = d['filename']
                        download.status = 'completed'
                        download.progress = 100
                        download.completed_at = datetime.utcnow()
                        db.session.commit()
                
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
    
    def _format_duration(self, duration):
        """Format duration from seconds to MM:SS or HH:MM:SS"""
        if not duration:
            return "Unknown"
        
        try:
            # Convert to int if it's a float
            duration = int(float(duration))
            
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        except (ValueError, TypeError):
            return "Unknown"
