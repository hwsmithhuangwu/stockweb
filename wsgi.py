"""
WSGI config for stockweb project.

This module contains the WSGI application used by Gunicorn or other WSGI servers.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.app import app

if __name__ == "__main__":
    app.run()