#!/usr/bin/env python3
"""
Initialize database
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.database import create_tables, test_connection
from app.config import settings


def main():
    """Initialize database"""
    print(f"🗄️ Initializing database for {settings.APP_NAME}")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    
    # Test connection
    if not test_connection():
        print("❌ Cannot connect to database")
        sys.exit(1)
    
    # Create tables
    try:
        create_tables()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()