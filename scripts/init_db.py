#!/usr/bin/env python3
"""
Initialize database
"""
import sys
import os
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def wait_for_db(max_retries=30, delay=1):
    """Wait for database to be ready"""
    print("⏳ Waiting for database to be ready...")
    
    for i in range(max_retries):
        try:
            from app.database import test_connection
            if test_connection():
                print("✅ Database is ready!")
                return True
            else:
                print(f"🔄 Attempt {i+1}/{max_retries}: Database not ready, retrying...")
                time.sleep(delay)
        except Exception as e:
            print(f"🔄 Attempt {i+1}/{max_retries}: {e}")
            time.sleep(delay)
    
    print("❌ Database is not ready after maximum retries")
    return False


def main():
    """Initialize database"""
    print("🗄️ Database Initialization Script")
    print("=" * 50)
    
    try:
        # Test configuration first
        from app.config import settings
        print(f"📱 App Name: {settings.APP_NAME}")
        print(f"🌍 Environment: {settings.ENVIRONMENT}")
        print(f"🔗 Database: {settings.DATABASE_URL.split('/')[-1]}")
        print()
        
        # Wait for database
        if not wait_for_db():
            print("❌ Cannot connect to database")
            sys.exit(1)
        
        # Import after database is ready
        from app.database import create_tables, test_connection
        
        # Final connection test
        print("🔍 Final database connection test...")
        if not test_connection():
            print("❌ Database connection test failed")
            sys.exit(1)
        
        print("✅ Database connection confirmed")
        
        # Create tables
        print("📋 Creating database tables...")
        try:
            create_tables()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Failed to create tables: {e}")
            sys.exit(1)
        
        print()
        print("🎉 Database initialization completed successfully!")
        print("✅ Ready to start the application")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the project root")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()