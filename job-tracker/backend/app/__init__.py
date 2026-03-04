from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.db import init_db
from app.scheduler import start_scheduler


def create_app():
    """Application factory — creates and configures the Flask app."""
    app = Flask(__name__)

    # Load config onto the app
    app.secret_key = Config.SECRET_KEY

    # Allow requests from the React frontend
    CORS(app)

    # Validate required env vars — raises ValueError early if anything is missing
    Config.validate()

    # Create the database and tables if they don't exist yet
    init_db(Config.DATABASE_PATH)

    # Register API routes
    from app.routes import bp
    app.register_blueprint(bp)

    # Start the background scheduler (runs check_all_repos every N minutes)
    start_scheduler(app)

    return app
