#!/usr/bin/env python3
"""
Gmail Attachment Downloader Setup Script

This script helps with initial setup and testing of the Gmail attachment downloader.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True

def check_directories():
    """Create necessary directories if they don't exist."""
    directories = ['credentials', 'downloads', 'logs']
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")

def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        print(f"stderr: {e.stderr}")
        return False

def check_credentials():
    """Check if Gmail API credentials are configured."""
    creds_path = Path("credentials/credentials.json")
    
    if not creds_path.exists():
        print("\n❌ Gmail API credentials not found!")
        print("Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Gmail API")
        print("3. Create OAuth2 credentials (Desktop Application)")
        print("4. Download the JSON file as 'credentials/credentials.json'")
        print("\nSee credentials/README.txt for detailed instructions.")
        return False
    
    try:
        with open(creds_path, 'r') as f:
            creds = json.load(f)
        
        if 'installed' in creds and 'client_id' in creds['installed']:
            print("✓ Gmail API credentials found")
            return True
        else:
            print("❌ Invalid credentials format")
            return False
            
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_path = Path(".env")
    example_path = Path(".env.example")
    
    if not env_path.exists() and example_path.exists():
        with open(example_path, 'r') as src, open(env_path, 'w') as dst:
            dst.write(src.read())
        print("✓ Created .env file from template")
    elif env_path.exists():
        print("✓ .env file already exists")
    else:
        print("❌ Could not create .env file")

def test_import():
    """Test if all required modules can be imported."""
    print("\nTesting imports...")
    
    required_modules = [
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
    ]
    
    all_imported = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            all_imported = False
    
    return all_imported

def run_syntax_check():
    """Check if main.py has valid syntax."""
    print("\nChecking main.py syntax...")
    try:
        with open('main.py', 'r') as f:
            compile(f.read(), 'main.py', 'exec')
        print("✓ main.py syntax is valid")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in main.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking main.py: {e}")
        return False

def main():
    """Main setup function."""
    print("Gmail Attachment Downloader Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\nChecking directories...")
    check_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Test imports
    if not test_import():
        print("\n❌ Some required modules failed to import")
        sys.exit(1)
    
    # Check syntax
    if not run_syntax_check():
        print("\n❌ Python syntax errors found")
        sys.exit(1)
    
    # Create .env file
    print("\nConfiguring environment...")
    create_env_file()
    
    # Check credentials
    print("\nChecking Gmail API credentials...")
    creds_ok = check_credentials()
    
    print("\n" + "=" * 40)
    print("SETUP SUMMARY")
    print("=" * 40)
    
    if creds_ok:
        print("✅ Setup completed successfully!")
        print("\nYou can now run the application:")
        print("  python main.py")
        print("\nOr with Docker:")
        print("  docker-compose up --build")
    else:
        print("⚠️  Setup completed with warnings")
        print("\nNext steps:")
        print("1. Configure Gmail API credentials (see credentials/README.txt)")
        print("2. Run: python main.py")
    
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()