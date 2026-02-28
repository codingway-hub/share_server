from flask import Blueprint, render_template

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')


@pages_bp.route('/upload')
def upload():
    """Render the upload page."""
    return render_template('upload.html')


@pages_bp.route('/files')
def files():
    """Render the files page."""
    return render_template('files.html')


@pages_bp.route('/notes')
def notes():
    """Render the notes page."""
    return render_template('notes.html')
