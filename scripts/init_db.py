#!/usr/bin/env python3
"""
Initialize database with tables and seed data
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from app.database import create_tables, drop_tables, engine
    from app.config import settings
    from sqlalchemy import text
    
    def test_database_connection():
        """Test database connection"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                return result.fetchone() is not None
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def init_database():
        """Initialize database"""
        print(f"🗄️ Initializing database for {settings.APP_NAME}...")
        print(f"📍 Environment: {settings.ENVIRONMENT}")
        print(f"🔗 Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Hidden'}")
        
        # Test connection first
        if not test_database_connection():
            print("❌ Cannot connect to database. Please check your connection settings.")
            sys.exit(1)
        
        print("✅ Database connection successful!")
        
        if settings.ENVIRONMENT == "development":
            print("⚠️ Development mode: Dropping existing tables...")
            try:
                drop_tables()
                print("✅ Tables dropped successfully!")
            except Exception as e:
                print(f"⚠️ Warning: Could not drop tables: {e}")
        
        print("📋 Creating tables...")
        try:
            create_tables()
            print("✅ Tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            sys.exit(1)
        
        print("🎉 Database initialized successfully!")
        print(f"📊 Ready to start {settings.APP_NAME}!")

    if __name__ == "__main__":
        init_database()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're running this script from the project root directory")
    print("💡 And that all dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)