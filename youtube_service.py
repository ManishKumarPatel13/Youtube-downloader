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
        """Get video information using yt-dlp with anti-bot measures"""
        try:
            # Primary method with comprehensive anti-detection measures
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                "user_id": os.environ.get("YOUTUBE_USER_ID"),
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                },
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls'],
                        'player_skip': ['configs', 'webpage']
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("No video information found")
                
                # Extract available formats
                formats = []
                if 'formats' in info:
                    for f in info['formats']:
                        if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                            format_info = {
                                'format_id': f.get('format_id', ''),
                                'ext': f.get('ext', ''),
                                'resolution': f.get('resolution', 'unknown'),
                                'filesize': f.get('filesize'),
                                'vcodec': f.get('vcodec', 'none'),
                                'acodec': f.get('acodec', 'none')
                            }
                            formats.append(format_info)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': formats[:10],  # Limit to first 10 formats
                    'uploader': info.get('uploader', 'Unknown')
                }
                
        except Exception as e:
            logging.error(f"Primary extraction failed: {str(e)}")
            
            # Fallback method 1: Use yt-dlp with cookies simulation
            try:
                fallback_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'extractor_args': {
                        'youtube': {
                            'skip': ['dash'],
                            'player_client': ['android', 'web']
                        }
                    }
                }
                
                with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        return {
                            'title': info.get('title', 'Unknown'),
                            'duration': info.get('duration', 0),
                            'thumbnail': info.get('thumbnail', ''),
                            'formats': [{'format_id': 'best', 'ext': 'mp4', 'resolution': 'best'}],
                            'uploader': info.get('uploader', 'Unknown')
                        }
            except Exception as fallback_error:
                logging.error(f"Fallback method 1 failed: {str(fallback_error)}")
            
            # Fallback method 2: Minimal extraction
            try:
                minimal_opts = {
                    'quiet': True,
                    'extract_flat': False,
                    'force_json': True,
                    'no_check_certificates': True
                }
                
                with yt_dlp.YoutubeDL(minimal_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if info:
                        return {
                            'title': info.get('title', 'Video'),
                            'duration': info.get('duration', 0),
                            'thumbnail': info.get('thumbnail', ''),
                            'formats': [{'format_id': 'best', 'ext': 'mp4', 'resolution': 'best'}],
                            'uploader': info.get('uploader', 'Unknown')
                        }
            except Exception as minimal_error:
                logging.error(f"Minimal extraction failed: {str(minimal_error)}")
            
            # If all methods fail, return a generic error
            if "Sign in to confirm you're not a bot" in str(e) or "bot" in str(e).lower():
                raise Exception("YouTube is blocking automated requests. Please try again later or use a different video.")
            else:
                raise Exception(f"Could not extract video information: {str(e)}")
    
    def download_video_direct(self, url, format_type='mp4', quality='best'):
        """Download video directly and return file path with anti-bot measures"""
        try:
            # Create temporary directory for downloads
            download_dir = tempfile.mkdtemp()
            
            # Configure download options with anti-detection measures
            ydl_opts = {
                'format': 'best[ext=mp4]/best' if format_type == 'mp4' else 'bestaudio[ext=m4a]/best[ext=m4a]/bestaudio',
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                },
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls'],
                        'player_skip': ['configs', 'webpage']
                    }
                }
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as primary_error:
                logging.error(f"Primary download failed: {str(primary_error)}")
                
                # Fallback download method
                fallback_opts = {
                    'format': 'worst[ext=mp4]/worst' if format_type == 'mp4' else 'worstaudio',
                    'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'extractor_args': {
                        'youtube': {
                            'skip': ['dash'],
                            'player_client': ['android', 'web']
                        }
                    }
                }
                
                with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                    ydl.download([url])
            
            # Find the downloaded file
            files = os.listdir(download_dir)
            if not files:
                raise Exception("No file was downloaded")
            
            downloaded_file = os.path.join(download_dir, files[0])
            
            if not os.path.exists(downloaded_file):
                raise Exception("Downloaded file not found")
            
            return downloaded_file
            
        except Exception as e:
            logging.error(f"Download error: {str(e)}")
            if "Sign in to confirm you're not a bot" in str(e) or "bot" in str(e).lower():
                raise Exception("YouTube is blocking automated requests. Please try again later.")
            else:
                raise Exception(f"Download failed: {str(e)}")

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

# Create a global instance for routes to use
youtube_service = YouTubeService()
