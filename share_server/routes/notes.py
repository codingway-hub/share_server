from flask import Blueprint, request, jsonify
from share_server.models import db, Note
import hashlib
import markdown
import logging

logger = logging.getLogger(__name__)

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('', methods=['POST'])
def create_note():
    """Create a new note with optional password protection."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

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

    try:
        db.session.add(new_note)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating note: {e}")
        return jsonify({'error': 'Database error'}), 500

    return jsonify({
        'id': new_note.id,
        'title': new_note.title,
        'content': new_note.content,
        'created_time': new_note.created_time.isoformat(),
        'has_password': bool(new_note.password)
    }), 201

@notes_bp.route('', methods=['GET'])
def list_notes():
    """List all notes ordered by creation time."""
    try:
        notes = Note.query.order_by(Note.created_time.desc()).all()
        return jsonify([note.to_dict() for note in notes])
    except Exception as e:
        logger.error(f"Error listing notes: {e}")
        return jsonify({'error': 'Database error'}), 500

@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note with Markdown-to-HTML conversion and password verification."""
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    try:
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
    except Exception as e:
        logger.error(f"Error processing note {note_id}: {e}")
        return jsonify({'error': 'Database error'}), 500

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note."""
    note = Note.query.get(note_id)
    if not note:
        return jsonify({'error': 'Note not found'}), 404

    try:
        db.session.delete(note)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting note {note_id}: {e}")
        return jsonify({'error': 'Database error'}), 500

    return jsonify({'message': 'Note deleted successfully'})
