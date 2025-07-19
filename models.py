from app import db
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text, Boolean

class Download(db.Model):
    id = db.Column(Integer, primary_key=True)
    video_id = db.Column(String(20), nullable=False)
    title = db.Column(String(255), nullable=False)
    url = db.Column(Text, nullable=False)
    format_selected = db.Column(String(50), nullable=False)
    quality = db.Column(String(20), nullable=False)
    status = db.Column(String(20), default='pending')  # pending, downloading, completed, failed
    progress = db.Column(Integer, default=0)
    file_path = db.Column(String(255))
    created_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)
    error_message = db.Column(Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'title': self.title,
            'url': self.url,
            'format_selected': self.format_selected,
            'quality': self.quality,
            'status': self.status,
            'progress': self.progress,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }
