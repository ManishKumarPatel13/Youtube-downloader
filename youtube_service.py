import os
import yt_dlp
import re
import tempfile
import logging

class YouTubeService:
    def __init__(self):
        self.downloads_dir = tempfile.mkdtemp()  # Temporary directory
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
            # Enhanced options for better compatibility
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    logging.error(f"No video info extracted for URL: {url}")
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
            logging.error(f"Video info error for URL {url}: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Try fallback with minimal options
            try:
                logging.info("Trying fallback method...")
                fallback_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'format': 'best'
                }
                
                with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                    basic_info = ydl.extract_info(url, download=False)
                    if basic_info:
                        return {
                            'id': basic_info.get('id', 'unknown'),
                            'title': basic_info.get('title', 'Unknown Title'),
                            'thumbnail': basic_info.get('thumbnail', ''),
                            'duration': self._format_duration(basic_info.get('duration')),
                            'uploader': basic_info.get('uploader', 'Unknown'),
                            'view_count': basic_info.get('view_count', 0),
                            'video_formats': [{'format_id': 'best', 'quality': 'best', 'ext': 'mp4', 'filesize': None}],
                            'audio_formats': [{'format_id': 'bestaudio', 'quality': '128kbps', 'ext': 'mp3', 'filesize': None}]
                        }
            except Exception as fallback_error:
                logging.error(f"Fallback method also failed: {fallback_error}")
            
            return None
    
    def download_video_direct(self, url, format_type='video', quality='best'):
        """Download video directly and return file path"""
        try:
            # Set up download options
            if format_type == 'audio':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.downloads_dir, '%(title)s.%(ext)s'),
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
                }
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # For audio conversion, the filename might change
                if format_type == 'audio':
                    base_name = os.path.splitext(filename)[0]
                    filename = f"{base_name}.mp3"
                
                if os.path.exists(filename):
                    return filename
                    
                return None
                
        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            return None
    
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
