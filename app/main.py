"""
Hadith API - A bilingual (Arabic/English) API for authentic hadith.

This API provides access to the six major hadith collections (Kutub al-Sittah):
- Sahih al-Bukhari
- Sahih Muslim
- Sunan Abu Dawud
- Jami at-Tirmidhi
- Sunan an-Nasai
- Sunan Ibn Majah
"""

from flask import Flask, jsonify
from flask_cors import CORS

from app.config import get_settings
from app.database import init_db, db_session
from app.routers import (
    books_bp, chapters_bp, hadiths_bp, search_bp,
    topics_bp, auth_bp, children_bp, progress_bp
)
from app.services.search_service import get_search_service

settings = get_settings()


def create_app():
    """Application factory."""
    app = Flask(__name__)

    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize database on first request
    with app.app_context():
        print("Starting Hadith API...")
        init_db()
        print("Database initialized.")

        # Connect to Meilisearch
        search_service = get_search_service()
        if search_service.connect():
            print("Connected to Meilisearch.")
        else:
            print("Warning: Could not connect to Meilisearch. Search features will be limited.")

    # Register blueprints with API prefix
    app.register_blueprint(books_bp, url_prefix=f"{settings.api_prefix}/books")
    app.register_blueprint(chapters_bp, url_prefix=f"{settings.api_prefix}/chapters")
    app.register_blueprint(hadiths_bp, url_prefix=f"{settings.api_prefix}/hadiths")
    app.register_blueprint(search_bp, url_prefix=f"{settings.api_prefix}/search")
    app.register_blueprint(topics_bp, url_prefix=f"{settings.api_prefix}/topics")
    app.register_blueprint(auth_bp, url_prefix=f"{settings.api_prefix}/auth")
    app.register_blueprint(children_bp, url_prefix=f"{settings.api_prefix}/children")
    app.register_blueprint(progress_bp, url_prefix=f"{settings.api_prefix}/children")

    # Root endpoint
    @app.route("/")
    def root():
        """Root endpoint with API information."""
        return jsonify({
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "Bilingual Hadith API (Arabic/English)",
            "endpoints": {
                "books": f"{settings.api_prefix}/books",
                "topics": f"{settings.api_prefix}/topics",
                "hadiths": f"{settings.api_prefix}/hadiths",
                "search": f"{settings.api_prefix}/search",
                "random": f"{settings.api_prefix}/hadiths/random"
            }
        })

    # Health check endpoint
    @app.route("/health")
    def health():
        """Health check endpoint."""
        search_service = get_search_service()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "search": "connected" if search_service.is_connected() else "disconnected"
        })

    # Cleanup database session after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=settings.debug)
