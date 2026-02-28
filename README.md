# Share Server

A simple, modern file and note sharing server built with Flask. Features include file uploads with resumable downloads, Markdown note sharing, and optional password protection for both files and notes.

## Features

- **File Sharing**
  - Upload and share files up to 16GB
  - Resumable downloads with Range header support
  - Password protection for files
  - Download count tracking
  - Support for multiple file types (txt, pdf, images, documents, archives, media)

- **Note Sharing**
  - Create and share Markdown-formatted notes
  - Automatic Markdown to HTML conversion
  - Password protection for notes
  - Easy-to-use web interface

- **Security**
  - Password hashing with SHA-256
  - Password verification API
  - Secure file handling

- **Modern UI**
  - Clean, responsive web interface
  - Cyber-neon themed design
  - Easy navigation

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd share_server
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python -m share_server
```

The server will start on `http://localhost:5000`

## Usage

### File Sharing

1. Navigate to the upload page: `http://localhost:5000/upload`
2. Select a file to upload (max 16GB)
3. Optionally add a password for protection
4. Click upload to get a shareable link

### Note Sharing

1. Navigate to the notes page: `http://localhost:5000/notes`
2. Create a new note with title and Markdown content
3. Optionally add a password for protection
4. Share the note URL with others

### Password Protection

Files and notes can be protected with passwords. When accessing protected content, users will be prompted to enter the password.

## API Endpoints

### Files

- `POST /api/files` - Upload a file
  - Form data: `file` (required), `password` (optional)
  - Returns: File object with id, filename, size, upload_time, has_password

- `GET /api/files` - List all files
  - Returns: Array of file objects

- `GET /api/files/<id>` - Download a file
  - Query params: `password` (required for protected files)
  - Returns: File content or 401 if password invalid

- `DELETE /api/files/<id>` - Delete a file
  - Returns: Success message

### Notes

- `POST /api/notes` - Create a note
  - JSON body: `title` (required), `content` (required), `password` (optional)
  - Returns: Note object with id, title, content, created_time, has_password

- `GET /api/notes` - List all notes
  - Returns: Array of note objects

- `GET /api/notes/<id>` - Get a note
  - Query params: `password` (required for protected notes)
  - Returns: Note object with html_content or 401 if password invalid

- `DELETE /api/notes/<id>` - Delete a note
  - Returns: Success message

### Authentication

- `POST /api/verify-password` - Verify password for protected content
  - JSON body: `type` ('file' or 'note'), `id`, `password`
  - Returns: `{valid: true}` or `{valid: false}` with 401 status

## Testing

Run the comprehensive test suite:

```bash
python tests/test_app.py
```

Or run individual test modules:

```bash
python tests/test_files.py
python tests/test_notes.py
python tests/test_auth.py
```

## Project Structure

```
share_server/
├── share_server/
│   ├── __init__.py      # Flask app factory
│   ├── config.py        # Configuration settings
│   ├── models.py        # Database models
│   ├── routes/          # API routes
│   │   ├── auth.py      # Authentication endpoints
│   │   ├── files.py     # File endpoints
│   │   ├── notes.py     # Note endpoints
│   │   └── pages.py     # Page routes
│   ├── static/          # Static assets (CSS, JS)
│   └── templates/       # HTML templates
├── tests/               # Test suite
│   ├── test_app.py      # Comprehensive tests
│   ├── test_auth.py     # Auth tests
│   ├── test_files.py    # File tests
│   └── test_notes.py    # Note tests
├── data/                # Database directory
├── uploads/             # Uploaded files directory
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Configuration

Configuration is handled in `share_server/config.py`:

- `SECRET_KEY` - Flask secret key (defaults to 'cyber-neon-secret-key-2024')
- `SQLALCHEMY_DATABASE_URI` - SQLite database path
- `SQLALCHEMY_TRACK_MODIFICATIONS` - Disabled by default
- `UPLOAD_FOLDER` - Directory for uploaded files
- `MAX_CONTENT_LENGTH` - Maximum upload size (16GB)

To override settings, set environment variables:

```bash
export SECRET_KEY=your-secret-key
```

## Supported File Types

- Documents: txt, pdf, doc, docx, xls, xlsx
- Images: png, jpg, jpeg, gif
- Archives: zip, rar
- Media: mp4, mp3

## Security Notes

- Passwords are hashed using SHA-256 before storage
- All password verification is done server-side
- Files are stored with random UUIDs to prevent direct access
- Download requests increment a counter for analytics

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
