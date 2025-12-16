"""
Vercel Serverless Function Entry Point

This file wraps the FastAPI app for Vercel's Python runtime.
"""

import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel expects a handler or the app object
handler = app
