#!/usr/bin/env python3
"""
Build script for React frontend

This script builds the React frontend for production deployment.
"""

import subprocess
import sys
import os


def build_frontend():
    """Build the React frontend for production"""
    print("🏗️Building React frontend for production...")
    
    frontend_path = '/Users/dev/Desktop/tapistro/frontend'
    
    if not os.path.exists(frontend_path):
        print("Frontend directory not found!")
        return False
    
    os.chdir(frontend_path)
    
    if not os.path.exists('node_modules'):
        print("📦 Installing dependencies...")
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to install dependencies: {result.stderr}")
            return False
    
    print("🔨 Building frontend...")
    result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Build failed: {result.stderr}")
        return False
    
    print("Frontend built successfully!")
    print("Build files are in: frontend/build/")
    return True


def main():
    """Main function"""
    print("🚀 Multi-Provider LLM Interface - Frontend Build")
    print("=" * 50)
    
    success = build_frontend()
    
    if success:
        print("\n🎉 Build completed successfully!")
        print("You can now run the Flask server to serve the built frontend.")
        print("Run: python main.py server")
    else:
        print("\n Build failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
