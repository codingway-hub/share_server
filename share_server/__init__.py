from flask import Flask
from share_server.models import db
from share_server.config import Config, BASE_DIR
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Ensure upload and data directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)

    with app.app_context():
        db.create_all()

    # Register blueprints (will be implemented in later tasks)
    try:
        from share_server.routes.files import files_bp
        app.register_blueprint(files_bp, url_prefix='/api/files')
    except ImportError:
        logger.warning('Blueprint files not found - will be available in later tasks')

    try:
        from share_server.routes.notes import notes_bp
        app.register_blueprint(notes_bp, url_prefix='/api/notes')
    except ImportError:
        logger.warning('Blueprint notes not found - will be available in later tasks')

    try:
        from share_server.routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api')
    except ImportError:
        logger.warning('Blueprint auth not found - will be available in later tasks')

    try:
        from share_server.routes.pages import pages_bp
        app.register_blueprint(pages_bp)
    except ImportError:
        logger.warning('Blueprint pages not found - will be available in later tasks')

    return app
