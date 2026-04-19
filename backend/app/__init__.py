"""Flask application factory."""
import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import Config
from app.extensions import mongo


def create_app(config_class=Config):
    """Create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['MONGO_URI'] = app.config['MONGO_URI']
    max_mb = float(app.config.get('MAX_UPLOAD_MB') or 16)
    app.config['MAX_CONTENT_LENGTH'] = int(max_mb * 1024 * 1024)
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)

    # Startup log: which MongoDB connection is being used
    uri = (app.config.get('MONGODB_URI') or '').strip()
    if uri.startswith('mongodb+srv'):
        print('Using MongoDB Atlas (Cloud)')
    elif uri.startswith('mongodb://mongodb'):
        print('Using Local Docker MongoDB')
    else:
        print('Using Custom MongoDB Configuration')

    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    mongo.init_app(app)
    JWTManager(app)

    # Register blueprints
    from app.api.auth import auth_bp
    from app.api.assessment import assessment_bp
    from app.api.portfolio import portfolio_bp
    from app.api.analytics import analytics_bp
    from app.api.tasks import tasks_bp
    from app.api.assignments import assignments_bp
    from app.api.submissions import submissions_bp
    from app.api.mentor import mentor_bp
    from app.api.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(assessment_bp, url_prefix='/api/assessment')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(assignments_bp, url_prefix='/api/assignments')
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
    app.register_blueprint(mentor_bp, url_prefix='/api/mentor')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    return app
