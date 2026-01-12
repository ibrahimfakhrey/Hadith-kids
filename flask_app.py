"""
Flask app entry point for PythonAnywhere deployment.

PythonAnywhere WSGI Configuration:
In your PythonAnywhere web app settings, set:
- Source code: /home/yourusername/hadeth
- Working directory: /home/yourusername/hadeth
- WSGI configuration file: Edit to contain:

    import sys
    path = '/home/yourusername/hadeth'
    if path not in sys.path:
        sys.path.insert(0, path)

    from flask_app import app as application
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

# Import the Flask app
from app.main import app

# PythonAnywhere expects 'application'
application = app

if __name__ == "__main__":
    app.run(debug=True)
