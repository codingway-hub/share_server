# Share Server Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a cyberpunk-themed file and text sharing server for LAN use with resumable downloads, file uploads, and password-protected notes.

**Architecture:** Flask-based REST API with SQLite for data persistence, file storage in local filesystem, neon cyberpunk UI with CSS animations.

**Tech Stack:** Python 3, Flask, SQLite, HTML5, CSS3, JavaScript (vanilla)

---

## Task 1: Project Setup and Database Initialization

**Files:**
- Create: `share_server/models.py`
- Create: `share_server/__init__.py`
- Create: `share_server/config.py`
- Create: `requirements.txt`

**Step 1: Create requirements.txt**

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
markdown==3.5.1
```

**Step 2: Create config.py**

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cyber-neon-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/cyber_share.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 * 1024  # 16GB max file size
```

**Step 3: Create models.py with database models**

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
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
    created_time = db.Column(db.DateTime, default=datetime.utcnow)
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
```

**Step 4: Create Flask app initialization**

```python
from flask import Flask
from models import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Ensure upload and data directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('data', exist_ok=True)

    with app.app_context():
        db.create_all()

    # Register blueprints
    from routes.files import files_bp
    from routes.notes import notes_bp
    from routes.auth import auth_bp
    from routes.pages import pages_bp

    app.register_blueprint(files_bp, url_prefix='/api/files')
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(pages_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Step 5: Initialize routes module**

```python
# routes/__init__.py
```

**Step 6: Install dependencies**

Run: `pip3 install -r requirements.txt`
Expected: Flask and dependencies installed successfully

**Step 7: Test database initialization**

Run: `python3 -c "from share_server import create_app; app = create_app(); print('Database initialized')"`
Expected: "Database initialized" with no errors

**Step 8: Commit**

```bash
git add share_server/ requirements.txt
git commit -m "feat: initialize project structure and database models"
```

---

## Task 2: Authentication Routes

**Files:**
- Create: `share_server/routes/auth.py`
- Test: `tests/test_auth.py`

**Step 1: Create auth routes**

```python
from flask import Blueprint, request, jsonify
from models import File, Note
import hashlib

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/verify-password', methods=['POST'])
def verify_password():
    data = request.get_json()
    item_type = data.get('type')  # 'file' or 'note'
    item_id = data.get('id')
    password = data.get('password')

    if not all([item_type, item_id, password]):
        return jsonify({'error': 'Missing required fields'}), 400

    if item_type == 'file':
        item = File.query.get(item_id)
    elif item_type == 'note':
        item = Note.query.get(item_id)
    else:
        return jsonify({'error': 'Invalid item type'}), 400

    if not item:
        return jsonify({'error': 'Item not found'}), 404

    if item.password and item.password != hash_password(password):
        return jsonify({'valid': False}), 401

    return jsonify({'valid': True})
```

**Step 2: Create test file**

```python
import sys
sys.path.insert(0, '..')
from share_server import create_app
import json

def test_verify_password():
    app = create_app()
    client = app.test_client()

    # Test missing fields
    response = client.post('/api/verify-password',
                          json={'type': 'file'})
    assert response.status_code == 400

    # Test invalid item type
    response = client.post('/api/verify-password',
                          json={'type': 'invalid', 'id': 1, 'password': 'test'})
    assert response.status_code == 400

    print("All auth tests passed!")
```

**Step 3: Run tests**

Run: `cd tests && python3 test_auth.py`
Expected: "All auth tests passed!"

**Step 4: Commit**

```bash
git add share_server/routes/auth.py tests/test_auth.py
git commit -m "feat: implement password verification API"
```

---

## Task 3: File Upload and Management Routes

**Files:**
- Create: `share_server/routes/files.py`
- Test: `tests/test_files.py`

**Step 1: Create file routes**

```python
from flask import Blueprint, request, jsonify, send_file, abort
from models import db, File
import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime

files_bp = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'zip', 'rar', 'doc', 'docx', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route('', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    password = request.form.get('password', '')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

    # Save file
    upload_folder = 'uploads'
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    # Get file size
    file_size = os.path.getsize(file_path)

    # Hash password if provided
    password_hash = None
    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Save to database
    new_file = File(
        filename=original_filename,
        stored_path=file_path,
        file_size=file_size,
        password=password_hash,
        mime_type=file.content_type
    )

    db.session.add(new_file)
    db.session.commit()

    return jsonify({
        'id': new_file.id,
        'filename': new_file.filename,
        'file_size': new_file.file_size,
        'upload_time': new_file.upload_time.isoformat(),
        'has_password': bool(new_file.password)
    }), 201

@files_bp.route('', methods=['GET'])
def list_files():
    files = File.query.order_by(File.upload_time.desc()).all()
    return jsonify([file.to_dict() for file in files])

@files_bp.route('/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file_record = File.query.get_or_404(file_id)

    # Check password if set
    if file_record.password:
        password = request.args.get('password', '')
        if hashlib.sha256(password.encode()).hexdigest() != file_record.password:
            return jsonify({'error': 'Invalid password'}), 401

    # Handle Range requests for resumable downloads
    range_header = request.headers.get('Range')

    if range_header:
        # Parse Range header: "bytes=start-end"
        try:
            byte_range = range_header.replace('bytes=', '').split('-')
            start = int(byte_range[0])
            end = int(byte_range[1]) if byte_range[1] else file_record.file_size - 1
        except (ValueError, IndexError):
            abort(400, description="Invalid Range header")

        # Validate range
        if start >= file_record.file_size or end >= file_record.file_size or start > end:
            abort(416, description="Requested Range Not Satisfiable")

        chunk_size = end - start + 1

        # Send partial content
        def generate():
            with open(file_record.stored_path, 'rb') as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    data = f.read(min(8192, remaining))
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        response = app.response_class(
            generate(),
            mimetype=file_record.mime_type or 'application/octet-stream',
            direct_passthrough=True
        )
        response.headers.add('Content-Range', f'bytes {start}-{end}/{file_record.file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', str(chunk_size))
        response.status_code = 206

        # Increment download count
        file_record.downloads_count += 1
        db.session.commit()

        return response

    # Normal download
    response = send_file(file_record.stored_path, as_attachment=True, download_name=file_record.filename)
    response.headers.add('Accept-Ranges', 'bytes')

    # Increment download count
    file_record.downloads_count += 1
    db.session.commit()

    return response

@files_bp.route('/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    file_record = File.query.get_or_404(file_id)

    # Delete file from filesystem
    if os.path.exists(file_record.stored_path):
        os.remove(file_record.stored_path)

    # Delete from database
    db.session.delete(file_record)
    db.session.commit()

    return jsonify({'message': 'File deleted successfully'})
```

**Step 2: Create file tests**

```python
import sys
sys.path.insert(0, '..')
from share_server import create_app
import io

def test_file_upload():
    app = create_app()
    client = app.test_client()

    # Create a test file
    data = {
        'file': (io.BytesIO(b'test content'), 'test.txt'),
    }

    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    result = response.get_json()
    assert 'id' in result
    assert result['filename'] == 'test.txt'

    # Test list files
    response = client.get('/api/files')
    assert response.status_code == 200
    files = response.get_json()
    assert len(files) > 0

    print("File upload tests passed!")
```

**Step 3: Run tests**

Run: `cd tests && python3 test_files.py`
Expected: "File upload tests passed!"

**Step 4: Commit**

```bash
git add share_server/routes/files.py tests/test_files.py
git commit -m "feat: implement file upload, download, and management APIs"
```

---

## Task 4: Notes Management Routes

**Files:**
- Create: `share_server/routes/notes.py`
- Test: `tests/test_notes.py`

**Step 1: Create notes routes**

```python
from flask import Blueprint, request, jsonify
from models import db, Note
import hashlib
import markdown

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('', methods=['POST'])
def create_note():
    data = request.get_json()

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    password = data.get('password', '')

    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400

    # Hash password if provided
    password_hash = None
    if password:
        password_hash = hashlib.sha256(password.encode()).hexdigest()

    new_note = Note(
        title=title,
        content=content,
        password=password_hash
    )

    db.session.add(new_note)
    db.session.commit()

    return jsonify({
        'id': new_note.id,
        'title': new_note.title,
        'content': new_note.content,
        'created_time': new_note.created_time.isoformat(),
        'has_password': bool(new_note.password)
    }), 201

@notes_bp.route('', methods=['GET'])
def list_notes():
    notes = Note.query.order_by(Note.created_time.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    note = Note.query.get_or_404(note_id)

    # Check password if set
    if note.password:
        password = request.args.get('password', '')
        if hashlib.sha256(password.encode()).hexdigest() != note.password:
            return jsonify({'error': 'Invalid password'}), 401

    # Convert markdown to HTML
    html_content = markdown.markdown(note.content)

    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'html_content': html_content,
        'created_time': note.created_time.isoformat()
    })

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)

    db.session.delete(note)
    db.session.commit()

    return jsonify({'message': 'Note deleted successfully'})
```

**Step 2: Create notes tests**

```python
import sys
sys.path.insert(0, '..')
from share_server import create_app

def test_notes():
    app = create_app()
    client = app.test_client()

    # Create note
    response = client.post('/api/notes',
                          json={'title': 'Test Note', 'content': '# Hello\nThis is a test'})
    assert response.status_code == 201
    result = response.get_json()
    assert result['title'] == 'Test Note'

    note_id = result['id']

    # Get note
    response = client.get(f'/api/notes/{note_id}')
    assert response.status_code == 200
    result = response.get_json()
    assert 'html_content' in result

    # List notes
    response = client.get('/api/notes')
    assert response.status_code == 200

    # Delete note
    response = client.delete(f'/api/notes/{note_id}')
    assert response.status_code == 200

    print("Notes tests passed!")
```

**Step 3: Run tests**

Run: `cd tests && python3 test_notes.py`
Expected: "Notes tests passed!"

**Step 4: Commit**

```bash
git add share_server/routes/notes.py tests/test_notes.py
git commit -m "feat: implement notes management APIs with Markdown support"
```

---

## Task 5: Page Routes

**Files:**
- Create: `share_server/routes/pages.py`

**Step 1: Create page routes**

```python
from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/')
def index():
    return render_template('index.html')

@pages_bp.route('/upload')
def upload():
    return render_template('upload.html')

@pages_bp.route('/files')
def files():
    return render_template('files.html')

@pages_bp.route('/notes')
def notes():
    return render_template('notes.html')
```

**Step 2: Commit**

```bash
git add share_server/routes/pages.py
git commit -m "feat: add page routes for UI"
```

---

## Task 6: Cyberpunk CSS Styles

**Files:**
- Create: `share_server/static/css/style.css`

**Step 1: Create cyberpunk styles**

```css
/* Cyberpunk Neon Theme */
:root {
    --neon-cyan: #00f3ff;
    --neon-magenta: #ff00ff;
    --neon-purple: #bd00ff;
    --bg-dark: #0a0a12;
    --bg-card: #12121a;
    --text-primary: #ffffff;
    --text-secondary: #a0a0b0;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Courier New', monospace;
    background: var(--bg-dark);
    color: var(--text-primary);
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}

/* Scanline effect */
body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.1),
        rgba(0, 0, 0, 0.1) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
    z-index: 1000;
}

/* Container */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Header */
header {
    text-align: center;
    padding: 3rem 0;
    border-bottom: 2px solid var(--neon-cyan);
    margin-bottom: 2rem;
}

.logo {
    font-size: 3rem;
    font-weight: bold;
    color: var(--neon-cyan);
    text-shadow: 0 0 10px var(--neon-cyan), 0 0 20px var(--neon-cyan), 0 0 40px var(--neon-cyan);
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from {
        text-shadow: 0 0 10px var(--neon-cyan), 0 0 20px var(--neon-cyan);
    }
    to {
        text-shadow: 0 0 20px var(--neon-cyan), 0 0 30px var(--neon-cyan), 0 0 40px var(--neon-magenta);
    }
}

/* Cards */
.card {
    background: var(--bg-card);
    border: 1px solid var(--neon-cyan);
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.5);
    transform: translateY(-2px);
}

/* Buttons */
.btn {
    display: inline-block;
    padding: 0.75rem 2rem;
    background: transparent;
    border: 2px solid var(--neon-cyan);
    color: var(--neon-cyan);
    font-family: inherit;
    font-size: 1rem;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.3s ease;
    text-decoration: none;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.btn:hover {
    background: var(--neon-cyan);
    color: var(--bg-dark);
    box-shadow: 0 0 20px var(--neon-cyan);
}

.btn:active {
    transform: scale(0.98);
}

.btn-primary {
    border-color: var(--neon-magenta);
    color: var(--neon-magenta);
}

.btn-primary:hover {
    background: var(--neon-magenta);
    box-shadow: 0 0 20px var(--neon-magenta);
}

.btn-danger {
    border-color: #ff3333;
    color: #ff3333;
}

.btn-danger:hover {
    background: #ff3333;
    box-shadow: 0 0 20px #ff3333;
}

/* Inputs */
input[type="text"],
input[type="password"],
input[type="file"],
textarea {
    width: 100%;
    padding: 0.75rem;
    background: var(--bg-dark);
    border: 1px solid var(--neon-cyan);
    border-radius: 4px;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 1rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

input:focus,
textarea:focus {
    outline: none;
    box-shadow: 0 0 10px var(--neon-cyan);
}

/* Forms */
.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--neon-cyan);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Grid */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

/* Navigation */
nav {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid rgba(0, 243, 255, 0.3);
}

th {
    color: var(--neon-cyan);
    text-transform: uppercase;
    letter-spacing: 1px;
}

tr:hover {
    background: rgba(0, 243, 255, 0.1);
}

/* Upload Area */
.upload-area {
    border: 2px dashed var(--neon-cyan);
    border-radius: 8px;
    padding: 3rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.upload-area:hover {
    background: rgba(0, 243, 255, 0.1);
    box-shadow: 0 0 20px var(--neon-cyan);
}

.upload-area.dragover {
    background: rgba(0, 243, 255, 0.2);
    border-color: var(--neon-magenta);
}

/* Progress Bar */
.progress-bar {
    width: 100%;
    height: 4px;
    background: rgba(0, 243, 255, 0.2);
    border-radius: 2px;
    overflow: hidden;
    margin-top: 1rem;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--neon-cyan), var(--neon-magenta));
    transition: width 0.3s ease;
}

/* Password Modal */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    z-index: 2000;
    justify-content: center;
    align-items: center;
}

.modal.active {
    display: flex;
}

.modal-content {
    background: var(--bg-card);
    border: 2px solid var(--neon-cyan);
    border-radius: 8px;
    padding: 2rem;
    max-width: 400px;
    width: 90%;
    box-shadow: 0 0 30px var(--neon-cyan);
}

/* Utility */
.text-neon-cyan {
    color: var(--neon-cyan);
}

.text-neon-magenta {
    color: var(--neon-magenta);
}

.text-secondary {
    color: var(--text-secondary);
}

.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 1.5rem; }

.flex {
    display: flex;
}

.items-center {
    align-items: center;
}

.justify-between {
    justify-content: space-between;
}

.gap-2 {
    gap: 0.5rem;
}

.gap-4 {
    gap: 1rem;
}
```

**Step 2: Commit**

```bash
git add share_server/static/css/style.css
git commit -m "feat: add cyberpunk neon theme styles"
```

---

## Task 7: Index Page Template

**Files:**
- Create: `share_server/templates/index.html`

**Step 1: Create index page**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Share Server - 赛博朋克文件共享</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">CYBER SHARE</div>
            <p class="text-secondary mt-2">局域网文件与文字共享服务器</p>
        </header>

        <nav>
            <a href="/upload" class="btn">上传文件</a>
            <a href="/files" class="btn btn-primary">文件列表</a>
            <a href="/notes" class="btn">便签列表</a>
        </nav>

        <div class="grid">
            <div class="card">
                <h2 class="text-neon-cyan mb-2">文件传输</h2>
                <p class="text-secondary mb-3">支持断点续传的大文件传输，快速在设备间分享文件</p>
                <a href="/upload" class="btn">立即上传</a>
            </div>

            <div class="card">
                <h2 class="text-neon-magenta mb-2">文字便签</h2>
                <p class="text-secondary mb-3">支持 Markdown 的临时便签，快速分享文字内容</p>
                <a href="/notes" class="btn btn-primary">创建便签</a>
            </div>

            <div class="card">
                <h2 style="color: var(--neon-purple)" class="mb-2">安全保护</h2>
                <p class="text-secondary mb-3">为文件和便签设置访问密码，保护您的隐私</p>
                <a href="/files" class="btn">查看详情</a>
            </div>
        </div>

        <div class="card" style="margin-top: 2rem; text-align: center;">
            <p class="text-secondary">
                霓虹发光风格 | 支持断点续传 | 局域网快速传输
            </p>
        </div>
    </div>
</body>
</html>
```

**Step 2: Commit**

```bash
git add share_server/templates/index.html
git commit -m "feat: add index page template"
```

---

## Task 8: Upload Page Template

**Files:**
- Create: `share_server/templates/upload.html`

**Step 1: Create upload page**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>上传文件 - Share Server</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <a href="/" style="text-decoration: none;">
                <div class="logo">CYBER SHARE</div>
            </a>
            <p class="text-secondary">上传文件进行共享</p>
        </header>

        <div class="card">
            <div class="upload-area" id="uploadArea">
                <h2 class="text-neon-cyan mb-2">拖拽文件到此处</h2>
                <p class="text-secondary mb-3">或者点击选择文件</p>
                <input type="file" id="fileInput" style="display: none;">
                <button class="btn" onclick="document.getElementById('fileInput').click()">选择文件</button>
            </div>

            <div class="form-group" style="margin-top: 2rem;">
                <label for="password">访问密码（可选）</label>
                <input type="password" id="password" placeholder="输入密码以保护此文件">
            </div>

            <div id="progressContainer" style="display: none;">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
                <p class="text-secondary mt-2" id="progressText">上传中...</p>
            </div>

            <button class="btn btn-primary" id="uploadBtn" style="margin-top: 1rem;">开始上传</button>
        </div>

        <nav>
            <a href="/" class="btn">返回首页</a>
            <a href="/files" class="btn btn-primary">查看文件</a>
        </nav>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const uploadBtn = document.getElementById('uploadBtn');
        const passwordInput = document.getElementById('password');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        let selectedFile = null;

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                selectedFile = files[0];
                uploadArea.querySelector('h2').textContent = selectedFile.name;
                uploadArea.querySelector('p').textContent = `大小: ${formatFileSize(selectedFile.size)}`;
            }
        });

        // File input
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                selectedFile = e.target.files[0];
                uploadArea.querySelector('h2').textContent = selectedFile.name;
                uploadArea.querySelector('p').textContent = `大小: ${formatFileSize(selectedFile.size)}`;
            }
        });

        // Upload
        uploadBtn.addEventListener('click', () => {
            if (!selectedFile) {
                alert('请先选择文件');
                return;
            }

            const formData = new FormData();
            formData.append('file', selectedFile);
            if (passwordInput.value) {
                formData.append('password', passwordInput.value);
            }

            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = (e.loaded / e.total) * 100;
                    progressFill.style.width = percent + '%';
                    progressText.textContent = `上传中: ${Math.round(percent)}%`;
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 201) {
                    progressText.textContent = '上传成功！';
                    setTimeout(() => {
                        window.location.href = '/files';
                    }, 1000);
                } else {
                    progressText.textContent = '上传失败';
                    alert('上传失败: ' + xhr.responseText);
                }
            });

            xhr.addEventListener('error', () => {
                progressText.textContent = '上传失败';
                alert('网络错误');
            });

            progressContainer.style.display = 'block';
            xhr.open('POST', '/api/files');
            xhr.send(formData);
        });

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }
    </script>
</body>
</html>
```

**Step 2: Commit**

```bash
git add share_server/templates/upload.html
git commit -m "feat: add upload page template with drag-drop support"
```

---

## Task 9: Files List Page Template

**Files:**
- Create: `share_server/templates/files.html`

**Step 1: Create files list page**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件列表 - Share Server</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <a href="/" style="text-decoration: none;">
                <div class="logo">FILES</div>
            </a>
            <p class="text-secondary">共享文件列表</p>
        </header>

        <nav>
            <a href="/" class="btn">返回首页</a>
            <a href="/upload" class="btn">上传文件</a>
        </nav>

        <div class="card">
            <div id="filesList" class="grid">
                <p class="text-secondary">加载中...</p>
            </div>
        </div>
    </div>

    <!-- Password Modal -->
    <div class="modal" id="passwordModal">
        <div class="modal-content">
            <h2 class="text-neon-cyan mb-2">输入密码</h2>
            <input type="password" id="modalPassword" placeholder="访问密码">
            <div class="flex gap-2 mt-3">
                <button class="btn" onclick="closeModal()">取消</button>
                <button class="btn btn-primary" id="confirmDownload">确认</button>
            </div>
        </div>
    </div>

    <script>
        let currentFileId = null;

        async function loadFiles() {
            const response = await fetch('/api/files');
            const files = await response.json();

            const container = document.getElementById('filesList');

            if (files.length === 0) {
                container.innerHTML = '<p class="text-secondary">暂无文件</p>';
                return;
            }

            container.innerHTML = files.map(file => `
                <div class="card" style="margin-bottom: 0;">
                    <h3 class="text-neon-cyan mb-1">${escapeHtml(file.filename)}</h3>
                    <p class="text-secondary mb-1">大小: ${formatFileSize(file.file_size)}</p>
                    <p class="text-secondary mb-2">上传时间: ${formatDate(file.upload_time)}</p>
                    <p class="text-secondary mb-3">下载次数: ${file.downloads_count}</p>
                    <div class="flex gap-2">
                        <button class="btn" onclick="downloadFile(${file.id}, ${file.has_password})">
                            下载
                        </button>
                        <button class="btn btn-danger" onclick="deleteFile(${file.id})">
                            删除
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function downloadFile(fileId, hasPassword) {
            if (hasPassword) {
                currentFileId = fileId;
                document.getElementById('passwordModal').classList.add('active');
                document.getElementById('modalPassword').focus();
            } else {
                window.location.href = `/api/files/${fileId}`;
            }
        }

        function closeModal() {
            document.getElementById('passwordModal').classList.remove('active');
            document.getElementById('modalPassword').value = '';
            currentFileId = null;
        }

        document.getElementById('confirmDownload').addEventListener('click', async () => {
            const password = document.getElementById('modalPassword').value;
            if (!password) {
                alert('请输入密码');
                return;
            }

            window.location.href = `/api/files/${currentFileId}?password=${encodeURIComponent(password)}`;
            closeModal();
        });

        async function deleteFile(fileId) {
            if (!confirm('确定要删除这个文件吗？')) return;

            const response = await fetch(`/api/files/${fileId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadFiles();
            } else {
                alert('删除失败');
            }
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }

        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Load files on page load
        loadFiles();
        // Refresh every 30 seconds
        setInterval(loadFiles, 30000);
    </script>
</body>
</html>
```

**Step 2: Commit**

```bash
git add share_server/templates/files.html
git commit -m "feat: add files list page template"
```

---

## Task 10: Notes List Page Template

**Files:**
- Create: `share_server/templates/notes.html`

**Step 1: Create notes list page**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>便签列表 - Share Server</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <style>
        .markdown-preview {
            max-height: 200px;
            overflow-y: auto;
            color: var(--text-secondary);
        }
        .markdown-preview h1, .markdown-preview h2, .markdown-preview h3 {
            color: var(--neon-cyan);
        }
        .markdown-preview code {
            background: rgba(0, 243, 255, 0.1);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
        }
        .markdown-preview pre {
            background: rgba(0, 243, 255, 0.1);
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="/" style="text-decoration: none;">
                <div class="logo">NOTES</div>
            </a>
            <p class="text-secondary">文字便签列表</p>
        </header>

        <nav>
            <a href="/" class="btn">返回首页</a>
            <button class="btn btn-primary" id="createNoteBtn">创建便签</button>
        </nav>

        <div class="card" id="notesList" style="display: none;">
            <div class="grid" id="notesGrid"></div>
        </div>

        <div class="card" id="loading">
            <p class="text-secondary">加载中...</p>
        </div>
    </div>

    <!-- Create Note Modal -->
    <div class="modal" id="createModal">
        <div class="modal-content">
            <h2 class="text-neon-cyan mb-2">创建便签</h2>
            <div class="form-group">
                <label for="noteTitle">标题</label>
                <input type="text" id="noteTitle" placeholder="便签标题">
            </div>
            <div class="form-group">
                <label for="noteContent">内容 (支持 Markdown)</label>
                <textarea id="noteContent" rows="8" placeholder="输入便签内容..."></textarea>
            </div>
            <div class="form-group">
                <label for="notePassword">访问密码（可选）</label>
                <input type="password" id="notePassword" placeholder="输入密码以保护此便签">
            </div>
            <div class="flex gap-2">
                <button class="btn" onclick="closeCreateModal()">取消</button>
                <button class="btn btn-primary" id="confirmCreate">创建</button>
            </div>
        </div>
    </div>

    <!-- Password Modal -->
    <div class="modal" id="passwordModal">
        <div class="modal-content">
            <h2 class="text-neon-cyan mb-2">输入密码</h2>
            <input type="password" id="viewPassword" placeholder="访问密码">
            <div class="flex gap-2 mt-3">
                <button class="btn" onclick="closePasswordModal()">取消</button>
                <button class="btn btn-primary" id="confirmView">确认</button>
            </div>
        </div>
    </div>

    <!-- View Note Modal -->
    <div class="modal" id="viewModal">
        <div class="modal-content" style="max-width: 600px;">
            <h2 class="text-neon-cyan mb-2" id="viewTitle"></h2>
            <div class="markdown-preview" id="viewContent"></div>
            <div class="flex gap-2 mt-3">
                <button class="btn" onclick="closeViewModal()">关闭</button>
            </div>
        </div>
    </div>

    <script>
        let currentNoteId = null;

        async function loadNotes() {
            const response = await fetch('/api/notes');
            const notes = await response.json();

            const loading = document.getElementById('loading');
            const container = document.getElementById('notesList');
            const grid = document.getElementById('notesGrid');

            loading.style.display = 'none';
            container.style.display = 'block';

            if (notes.length === 0) {
                grid.innerHTML = '<p class="text-secondary">暂无便签</p>';
                return;
            }

            grid.innerHTML = notes.map(note => `
                <div class="card" style="margin-bottom: 0;">
                    <h3 class="text-neon-magenta mb-1">${escapeHtml(note.title)}</h3>
                    <p class="text-secondary mb-1">创建时间: ${formatDate(note.created_time)}</p>
                    <div class="markdown-preview mb-2">
                        ${truncateContent(note.content, 100)}
                    </div>
                    <div class="flex gap-2">
                        <button class="btn" onclick="viewNote(${note.id}, ${note.has_password})">
                            查看
                        </button>
                        <button class="btn btn-danger" onclick="deleteNote(${note.id})">
                            删除
                        </button>
                    </div>
                </div>
            `).join('');
        }

        function viewNote(noteId, hasPassword) {
            if (hasPassword) {
                currentNoteId = noteId;
                document.getElementById('passwordModal').classList.add('active');
                document.getElementById('viewPassword').focus();
            } else {
                loadNoteContent(noteId);
            }
        }

        async function loadNoteContent(noteId, password = '') {
            let url = `/api/notes/${noteId}`;
            if (password) {
                url += `?password=${encodeURIComponent(password)}`;
            }

            const response = await fetch(url);
            if (response.status === 401) {
                alert('密码错误');
                return;
            }

            const note = await response.json();
            document.getElementById('viewTitle').textContent = note.title;
            document.getElementById('viewContent').innerHTML = note.html_content;
            document.getElementById('viewModal').classList.add('active');
        }

        function closeViewModal() {
            document.getElementById('viewModal').classList.remove('active');
        }

        function closePasswordModal() {
            document.getElementById('passwordModal').classList.remove('active');
            document.getElementById('viewPassword').value = '';
            currentNoteId = null;
        }

        document.getElementById('confirmView').addEventListener('click', () => {
            const password = document.getElementById('viewPassword').value;
            if (!password) {
                alert('请输入密码');
                return;
            }
            loadNoteContent(currentNoteId, password);
            closePasswordModal();
        });

        async function deleteNote(noteId) {
            if (!confirm('确定要删除这个便签吗？')) return;

            const response = await fetch(`/api/notes/${noteId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadNotes();
            } else {
                alert('删除失败');
            }
        }

        // Create note
        document.getElementById('createNoteBtn').addEventListener('click', () => {
            document.getElementById('createModal').classList.add('active');
            document.getElementById('noteTitle').focus();
        });

        function closeCreateModal() {
            document.getElementById('createModal').classList.remove('active');
            document.getElementById('noteTitle').value = '';
            document.getElementById('noteContent').value = '';
            document.getElementById('notePassword').value = '';
        }

        document.getElementById('confirmCreate').addEventListener('click', async () => {
            const title = document.getElementById('noteTitle').value.trim();
            const content = document.getElementById('noteContent').value.trim();
            const password = document.getElementById('notePassword').value;

            if (!title || !content) {
                alert('标题和内容不能为空');
                return;
            }

            const data = { title, content };
            if (password) {
                data.password = password;
            }

            const response = await fetch('/api/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                closeCreateModal();
                loadNotes();
            } else {
                alert('创建失败');
            }
        });

        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('zh-CN');
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function truncateContent(content, maxLength) {
            const escaped = escapeHtml(content);
            if (escaped.length <= maxLength) return escaped;
            return escaped.substring(0, maxLength) + '...';
        }

        // Load notes on page load
        loadNotes();
        // Refresh every 30 seconds
        setInterval(loadNotes, 30000);
    </script>
</body>
</html>
```

**Step 2: Commit**

```bash
git add share_server/templates/notes.html
git commit -m "feat: add notes list page template with Markdown preview"
```

---

## Task 11: Fix File Routes Import Issue

**Files:**
- Modify: `share_server/routes/files.py`

**Step 1: Fix missing app import in file routes**

The file routes need access to the Flask app for response_class. Modify the download_file function:

```python
from flask import Blueprint, request, jsonify, send_file, abort, current_app
from models import db, File
import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime

files_bp = Blueprint('files', __name__)

# ... [rest of code remains the same until download_file function]

@files_bp.route('/<int:file_id>', methods=['GET'])
def download_file(file_id):
    file_record = File.query.get_or_404(file_id)

    # Check password if set
    if file_record.password:
        password = request.args.get('password', '')
        if hashlib.sha256(password.encode()).hexdigest() != file_record.password:
            return jsonify({'error': 'Invalid password'}), 401

    # Handle Range requests for resumable downloads
    range_header = request.headers.get('Range')

    if range_header:
        # Parse Range header: "bytes=start-end"
        try:
            byte_range = range_header.replace('bytes=', '').split('-')
            start = int(byte_range[0])
            end = int(byte_range[1]) if byte_range[1] else file_record.file_size - 1
        except (ValueError, IndexError):
            abort(400, description="Invalid Range header")

        # Validate range
        if start >= file_record.file_size or end >= file_record.file_size or start > end:
            abort(416, description="Requested Range Not Satisfiable")

        chunk_size = end - start + 1

        # Send partial content
        def generate():
            with open(file_record.stored_path, 'rb') as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    data = f.read(min(8192, remaining))
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        response = current_app.response_class(
            generate(),
            mimetype=file_record.mime_type or 'application/octet-stream',
            direct_passthrough=True
        )
        response.headers.add('Content-Range', f'bytes {start}-{end}/{file_record.file_size}')
        response.headers.add('Accept-Ranges', 'bytes')
        response.headers.add('Content-Length', str(chunk_size))
        response.status_code = 206

        # Increment download count
        file_record.downloads_count += 1
        db.session.commit()

        return response

    # Normal download
    response = send_file(file_record.stored_path, as_attachment=True, download_name=file_record.filename)
    response.headers.add('Accept-Ranges', 'bytes')

    # Increment download count
    file_record.downloads_count += 1
    db.session.commit()

    return response
```

**Step 2: Test the application**

Run: `python3 share_server/__init__.py`
Expected: Server starts on http://0.0.0.0:5000

**Step 3: Commit**

```bash
git add share_server/routes/files.py
git commit -m "fix: use current_app instead of app in file download route"
```

---

## Task 12: Final Testing and README

**Files:**
- Create: `README.md`
- Create: `tests/test_app.py`

**Step 1: Create comprehensive test file**

```python
import sys
sys.path.insert(0, '..')
from share_server import create_app
import io

def test_app_initialization():
    app = create_app()
    assert app is not None
    print("✓ App initialization test passed")

def test_page_routes():
    app = create_app()
    client = app.test_client()

    response = client.get('/')
    assert response.status_code == 200
    assert b'CYBER SHARE' in response.data

    response = client.get('/upload')
    assert response.status_code == 200

    response = client.get('/files')
    assert response.status_code == 200

    response = client.get('/notes')
    assert response.status_code == 200

    print("✓ Page routes test passed")

def test_file_upload_and_download():
    app = create_app()
    client = app.test_client()

    # Upload file
    data = {
        'file': (io.BytesIO(b'test content for upload'), 'test.txt'),
    }

    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    file_data = response.get_json()
    file_id = file_data['id']

    # List files
    response = client.get('/api/files')
    assert response.status_code == 200
    files = response.get_json()
    assert len(files) > 0
    assert files[0]['id'] == file_id

    # Download file
    response = client.get(f'/api/files/{file_id}')
    assert response.status_code == 200
    assert b'test content for upload' in response.data

    # Check resumable download headers
    assert b'Accept-Ranges' in response.data or 'accept-ranges' in response.headers

    # Delete file
    response = client.delete(f'/api/files/{file_id}')
    assert response.status_code == 200

    print("✓ File operations test passed")

def test_notes_operations():
    app = create_app()
    client = app.test_client()

    # Create note
    response = client.post('/api/notes', json={
        'title': 'Test Note',
        'content': '# Heading\n\nThis is a test note with **bold** text.'
    })
    assert response.status_code == 201
    note_data = response.get_json()
    note_id = note_data['id']

    # List notes
    response = client.get('/api/notes')
    assert response.status_code == 200
    notes = response.get_json()
    assert len(notes) > 0

    # Get note
    response = client.get(f'/api/notes/{note_id}')
    assert response.status_code == 200
    note = response.get_json()
    assert note['title'] == 'Test Note'
    assert 'html_content' in note

    # Delete note
    response = client.delete(f'/api/notes/{note_id}')
    assert response.status_code == 200

    print("✓ Notes operations test passed")

def test_password_protection():
    app = create_app()
    client = app.test_client()

    # Upload file with password
    data = {
        'file': (io.BytesIO(b'protected content'), 'protected.txt'),
        'password': 'test123'
    }

    response = client.post('/api/files', data=data, content_type='multipart/form-data')
    assert response.status_code == 201
    file_data = response.get_json()
    file_id = file_data['id']

    # Try to download without password
    response = client.get(f'/api/files/{file_id}')
    assert response.status_code == 401

    # Download with correct password
    response = client.get(f'/api/files/{file_id}?password=test123')
    assert response.status_code == 200
    assert b'protected content' in response.data

    # Clean up
    client.delete(f'/api/files/{file_id}')

    print("✓ Password protection test passed")

if __name__ == '__main__':
    test_app_initialization()
    test_page_routes()
    test_file_upload_and_download()
    test_notes_operations()
    test_password_protection()
    print("\n✅ All tests passed!")
```

**Step 2: Run all tests**

Run: `cd tests && python3 test_app.py`
Expected: All tests pass with checkmarks

**Step 3: Create README.md**

```markdown
# Share Server - 赛博朋克文件共享服务器

局域网内的快速文件和文字共享服务器，采用赛博朋克霓虹发光风格，支持断点续传。

## 功能特点

- 🚀 快速文件传输：支持拖拽上传，断点续传
- 📝 文字便签：支持 Markdown 编辑和预览
- 🔒 密码保护：为文件和便签设置访问密码
- 🎨 赛博朋克风格：霓虹发光 UI，科技感十足
- 🌐 局域网共享：在局域网内设备间快速分享

## 安装

```bash
# 安装依赖
pip3 install -r requirements.txt
```

## 运行

```bash
# 启动服务器
python3 share_server/__init__.py
```

服务器将在 `http://0.0.0.0:5000` 启动。

## 使用说明

### 上传文件
1. 访问首页或点击"上传文件"
2. 拖拽文件到上传区域或点击选择文件
3. 可选：设置访问密码
4. 点击"开始上传"

### 下载文件
1. 访问"文件列表"
2. 找到需要下载的文件
3. 如果有密码，输入密码后下载

### 创建便签
1. 访问"便签列表"
2. 点击"创建便签"
3. 输入标题和内容（支持 Markdown）
4. 可选：设置访问密码
5. 点击"创建"

## API 端点

### 文件
- `POST /api/files` - 上传文件
- `GET /api/files` - 获取文件列表
- `GET /api/files/<id>` - 下载文件
- `DELETE /api/files/<id>` - 删除文件

### 便签
- `POST /api/notes` - 创建便签
- `GET /api/notes` - 获取便签列表
- `GET /api/notes/<id>` - 获取便签内容
- `DELETE /api/notes/<id>` - 删除便签

### 认证
- `POST /api/verify-password` - 验证访问密码

## 技术栈

- Python 3
- Flask
- SQLite
- HTML5 + CSS3 + JavaScript

## 项目结构

```
share_server/
├── share_server/
│   ├── __init__.py       # 应用入口
│   ├── models.py         # 数据库模型
│   ├── config.py         # 配置
│   ├── routes/           # 路由
│   ├── static/           # 静态文件
│   └── templates/        # 模板
├── uploads/              # 文件存储
├── data/                 # 数据库
├── tests/                # 测试
└── requirements.txt      # 依赖
```

## 测试

```bash
# 运行测试
cd tests
python3 test_app.py
```

## 注意事项

- 文件和便签数据存储在本地，服务器重启后数据会丢失
- 默认最大上传文件大小为 16GB
- 建议在局域网内使用，如需公网访问请配置防火墙和 HTTPS

## 开发

赛博朋克风格色彩：
- 主色：#00f3ff（青色）
- 辅助色：#ff00ff（洋红）、#bd00ff（紫色）
- 背景：#0a0a12（深色）

## 许可证

MIT License
```

**Step 4: Create .gitignore**

```text
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Database
*.db
*.sqlite
*.sqlite3

# Uploads
uploads/*
!uploads/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
```

**Step 5: Create empty uploads directory marker**

Run: `touch share_server/uploads/.gitkeep`

**Step 6: Final commit**

```bash
git add README.md .gitignore share_server/uploads/.gitkeep tests/test_app.py
git commit -m "docs: add README and comprehensive tests"
```

---

## Completion Checklist

- [x] Project structure created
- [x] Database models implemented
- [x] Authentication routes added
- [x] File upload/download with resumable support
- [x] Notes management with Markdown
- [x] Cyberpunk UI styles
- [x] All page templates
- [x] Comprehensive tests
- [x] README documentation

## How to Run

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the server
python3 share_server/__init__.py

# Access in browser
# Local: http://localhost:5000
# LAN: http://<your-ip>:5000
```
