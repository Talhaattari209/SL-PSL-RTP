#!/usr/bin/env python3
"""
Simple script to run the Sign Language Translator FastAPI server.
"""

import uvicorn
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app from app.py
from app import app

if __name__ == "__main__":
    print("🤟 Starting Sign Language Translator API...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🌐 Web UI will be available at: http://localhost:8000/ui")
    print("📋 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the FastAPI server
    uvicorn.run(
        app,
        host="0.0.0.0",  # Allow external connections
        port=8000,
        reload=True,     # Auto-reload on code changes
        log_level="info"
    ) 