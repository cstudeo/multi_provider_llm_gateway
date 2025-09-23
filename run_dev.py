#!/usr/bin/env python3
"""
Development runner script

This script helps run both the Flask backend and React frontend in development mode.
"""

import subprocess
import sys
import os
import time
import signal
from threading import Thread


def run_backend():
    """Run the Flask backend"""
    print("Starting Flask backend...")
    os.chdir('/Users/dev/Desktop/tapistro')
    subprocess.run([sys.executable, 'main.py', 'server'])


def run_frontend():
    """Run the React frontend"""
    print("Starting React frontend...")
    os.chdir('/Users/dev/Desktop/tapistro/frontend')
    subprocess.run(['npm', 'start'])


def main():
    """Main function to run both services"""
    print("🚀 Starting Multi-Provider LLM Interface Development Environment")
    print("=" * 60)
    
    # Check if frontend dependencies are installed
    frontend_path = '/Users/dev/Desktop/tapistro/frontend'
    if not os.path.exists(os.path.join(frontend_path, 'node_modules')):
        print("📦 Installing frontend dependencies...")
        os.chdir(frontend_path)
        subprocess.run(['npm', 'install'])
    
    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down development environment...")
        sys.exit(0)


if __name__ == '__main__':
    main()
