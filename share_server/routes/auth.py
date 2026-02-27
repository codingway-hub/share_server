from flask import Blueprint, request, jsonify
from share_server.models import File, Note
import hashlib

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Hash a password using SHA-256.

    Args:
        password: Plain text password string.

    Returns:
        Hexadecimal hash string.
    """
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/verify-password', methods=['POST'])
def verify_password():
    """Verify password for a protected file or note.

    Expects JSON body with:
        - type: 'file' or 'note'
        - id: Item identifier (integer)
        - password: Password to verify

    Returns:
        JSON response with 'valid' boolean or 'error' message.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    item_type = data.get('type')  # 'file' or 'note'
    item_id = data.get('id')
    password = data.get('password')

    try:
        item_id = int(item_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid item id'}), 400

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
