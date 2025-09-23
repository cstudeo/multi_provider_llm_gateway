#!/usr/bin/env python3
"""
Main entry point for the Multi-Provider LLM Interface

This script provides a simple command-line interface for testing the LLM service
and can also be used to run the Flask API server.
"""

import sys
import argparse
from llm_service import LLMService
from config import Config

def run_server():
    """Run the Flask API server"""
    from app import app
    print(f"Starting LLM Interface API on {Config.FLASK_HOST}:{Config.FLASK_PORT}")
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Multi-Provider LLM Interface')
    parser.add_argument('command', choices=['test', 'server'], 
                       help='Command to run: test or server')
    
    args = parser.parse_args()
    
    if not Config.validate_config():
        print("Configuration validation failed. Please check your environment variables.")
        print("Copy env.example to .env and fill in your API keys.")
        sys.exit(1)
    
    if args.command == 'server':
        run_server()

if __name__ == '__main__':
    main()
