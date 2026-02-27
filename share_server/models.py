from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os

db = SQLAlchemy()

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    upload_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    downloads_count = db.Column(db.Integer, default=0)
    mime_type = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'upload_time': self.upload_time.isoformat() if self.upload_time else None,
            'downloads_count': self.downloads_count,
            'has_password': bool(self.password)
        }

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    created_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'has_password': bool(self.password)
        }
