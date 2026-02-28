from flask import Blueprint, request, jsonify, send_file, abort, current_app
from share_server.models import db, File
import os
import uuid
import hashlib
import logging
from werkzeug.utils import secure_filename
from datetime import datetime

logger = logging.getLogger(__name__)

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
    if not original_filename or '.' not in original_filename:
        return jsonify({'error': 'Invalid filename'}), 400
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"

    # Save file
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, unique_filename)

    try:
        file.save(file_path)
        file_size = os.path.getsize(file_path)
    except OSError as e:
        logger.error(f'File save failed for {original_filename}: {str(e)}')
        return jsonify({'error': f'File save failed: {str(e)}'}), 500

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

    try:
        db.session.add(new_file)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f'Database error saving file {original_filename}: {str(e)}')
        # Clean up saved file if db commit failed
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
        return jsonify({'error': 'Database error'}), 500

    return jsonify({
        'id': new_file.id,
        'filename': new_file.filename,
        'file_size': new_file.file_size,
        'upload_time': new_file.upload_time.isoformat(),
        'has_password': bool(new_file.password)
    }), 201

@files_bp.route('', methods=['GET'])
def list_files():
    try:
        files = File.query.order_by(File.upload_time.desc()).all()
        return jsonify([file.to_dict() for file in files])
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': 'Database error'}), 500

@files_bp.route('/<int:file_id>', methods=['GET'])
def download_file(file_id):
    """Download a file with password verification and resumable download support."""
    file_record = File.query.get(file_id)
    if not file_record:
        return jsonify({'error': 'File not found'}), 404

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
            try:
                with open(file_record.stored_path, 'rb') as f:
                    f.seek(start)
                    remaining = chunk_size
                    while remaining > 0:
                        data = f.read(min(8192, remaining))
                        if not data:
                            break
                        remaining -= len(data)
                        yield data
            except OSError as e:
                logger.error(f"Error reading file {file_record.stored_path}: {e}")
                raise

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
        try:
            file_record.downloads_count += 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f'Database error updating download count for file {file_id}: {str(e)}')

        return response

    # Normal download
    response = send_file(file_record.stored_path, as_attachment=True, download_name=file_record.filename)
    response.headers.add('Accept-Ranges', 'bytes')

    # Increment download count
    try:
        file_record.downloads_count += 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f'Database error updating download count for file {file_id}: {str(e)}')

    return response

@files_bp.route('/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file and its stored file."""
    file_record = File.query.get(file_id)
    if not file_record:
        return jsonify({'error': 'File not found'}), 404

    # Delete from database first
    try:
        db.session.delete(file_record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f'Database error deleting file {file_id}: {str(e)}')
        return jsonify({'error': 'Database error'}), 500

    # Then delete from filesystem
    try:
        os.remove(file_record.stored_path)
    except OSError:
        pass  # File already deleted or doesn't exist

    return jsonify({'message': 'File deleted successfully'})
