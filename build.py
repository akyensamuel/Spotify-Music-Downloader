#!/usr/bin/env python3
"""
Pre-deployment script for Vercel
Handles Django static files and database setup
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_django():
    """Initialize Django settings"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotify_downloader.settings')
    django.setup()

def collect_static_files():
    """Collect static files for production"""
    print("📦 Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
        print("✅ Static files collected successfully")
        return True
    except Exception as e:
        print(f"❌ Error collecting static files: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def verify_environment():
    """Verify required environment variables"""
    required_vars = [
        'SECRET_KEY',
        'SPOTIFY_CLIENT_ID',
        'SPOTIFY_CLIENT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ All required environment variables present")
    return True

def main():
    """Main build process"""
    print("🚀 Starting Vercel pre-deployment build...")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Verify environment
    if not verify_environment():
        sys.exit(1)
    
    # Collect static files
    if not collect_static_files():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print("Ready for Vercel deployment")

if __name__ == "__main__":
    main()
