#!/usr/bin/env python3
"""
Main entry point for the Multi-Provider LLM Interface

This script runs the Flask API server for the multi-provider LLM interface.
"""

import sys
from config import Config

def main():
    if not Config.validate_config():
        sys.exit(1)
    
    from app import app
    print(f"Starting LLM Interface API on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )

if __name__ == '__main__':
    main()
