"""
WSGI adapter for PythonAnywhere.
This wraps the FastAPI app for WSGI compatibility.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Change working directory to project root (important for relative paths)
os.chdir(project_root)

# Ensure data directory exists
data_dir = os.path.join(project_root, 'data')
os.makedirs(data_dir, exist_ok=True)

# Set DATABASE_URL to absolute path BEFORE any imports
db_path = os.path.join(data_dir, 'hadith.db')
os.environ['DATABASE_URL'] = f"sqlite:///{db_path}"

# Clear the settings cache to pick up new env var
from app.config import get_settings
get_settings.cache_clear()

# Now import the app (this will use the new DATABASE_URL)
from app.main import app as fastapi_app
from app.database import init_db

# Initialize database on startup
init_db()

# Use a2wsgi to convert ASGI to WSGI
try:
    from a2wsgi import ASGIMiddleware
    app = ASGIMiddleware(fastapi_app)
    application = app  # PythonAnywhere expects 'application'
except ImportError:
    def application(environ, start_response):
        start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
        return [b'Please install a2wsgi: pip install a2wsgi']
