# YouTube Downloader Application

## Overview

This is a Flask-based YouTube downloader application that allows users to search for YouTube videos and download them in various formats and qualities. The application features a modern web interface with real-time progress updates via polling and stores download history in a database.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (2025-07-19)

✓ Fixed SocketIO compatibility issues with Gunicorn by switching to polling-based progress updates
✓ Enhanced video format extraction to provide up to 10 video quality options (144p to 4K)
✓ Expanded audio format options to 5 different bitrate choices (57kbps to 129kbps)
✓ Fixed application context issues in background download threads
✓ Improved YouTube search functionality to work reliably without timeouts

## System Architecture

The application follows a traditional Flask web application architecture with the following key characteristics:

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Real-time Communication**: Flask-SocketIO for WebSocket connections
- **Database**: SQLite (default) with support for PostgreSQL via DATABASE_URL environment variable
- **Video Processing**: yt-dlp library for YouTube video extraction and downloading

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5 for responsive design
- **Icons**: Font Awesome for iconography
- **JavaScript**: Vanilla JavaScript with Socket.IO client for real-time updates
- **Styling**: Custom CSS with CSS custom properties for theming

## Key Components

### 1. Application Core (`app.py`)
- Flask application factory pattern
- Database configuration with connection pooling
- SocketIO initialization with CORS support
- Proxy fix middleware for deployment behind reverse proxies

### 2. Database Models (`models.py`)
- **Download Model**: Tracks video download requests with fields for:
  - Video metadata (ID, title, URL)
  - Download configuration (format, quality)
  - Status tracking (pending, downloading, completed, failed)
  - Progress monitoring and error handling
  - Timestamp tracking for created and completed dates

### 3. YouTube Service (`youtube_service.py`)
- **Video Search**: YouTube video search functionality using yt-dlp
- **Video Information Extraction**: Retrieves video metadata, available formats, and qualities
- **Download Management**: Handles video downloading with progress tracking
- **Real-time Updates**: Emits progress updates via SocketIO

### 4. Web Routes (`routes.py`)
- **Home Route**: Displays recent downloads and main interface
- **Search Endpoint**: Handles video search requests
- **Video Info Endpoint**: Extracts information from YouTube URLs
- **Download Endpoint**: Initiates video downloads (implementation appears incomplete)

### 5. Frontend Interface
- **Search Interface**: Video search with thumbnail previews
- **Direct URL Input**: Manual URL entry for video downloads
- **Format Selection**: Choose between video/audio formats and quality levels
- **Progress Tracking**: Real-time download progress display
- **Download History**: Recent downloads display

## Data Flow

1. **Video Search**: User searches → Backend queries YouTube → Results displayed with thumbnails
2. **Direct URL**: User pastes URL → Backend extracts video info → Format options presented
3. **Download Process**: User selects format/quality → Download initiated → Progress updates via WebSocket → File stored in downloads directory
4. **History Tracking**: All downloads logged to database with status and metadata

## External Dependencies

### Python Libraries
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: Database ORM
- **Flask-SocketIO**: WebSocket support
- **yt-dlp**: YouTube video downloading and extraction
- **Werkzeug**: WSGI utilities and proxy handling

### Frontend Dependencies
- **Bootstrap 5**: UI framework (CDN)
- **Font Awesome**: Icon library (CDN)
- **Socket.IO Client**: Real-time communication (implied)

### System Requirements
- **File System**: Downloads directory for storing video files
- **Database**: SQLite (default) or PostgreSQL support

## Deployment Strategy

### Environment Configuration
- **SESSION_SECRET**: Flask session security (defaults to development key)
- **DATABASE_URL**: Database connection string (defaults to SQLite)
- **Host/Port**: Configurable via main.py (defaults to 0.0.0.0:5000)

### Production Considerations
- Proxy fix middleware configured for reverse proxy deployment
- Database connection pooling with health checks
- CORS enabled for SocketIO connections
- Debug mode configurable
- Logging configured at DEBUG level

### File Structure
- **Static Assets**: CSS and JavaScript in static directory
- **Templates**: HTML templates in templates directory
- **Downloads**: Video files stored in downloads directory
- **Database**: SQLite file in application root (if using SQLite)

## Notes for Development

The application appears to have an incomplete download route implementation in `routes.py`. The YouTube service class also appears to have a truncated `search_videos` method. These would need to be completed for full functionality.

The architecture supports both SQLite for development and PostgreSQL for production through environment configuration, making it flexible for different deployment scenarios.