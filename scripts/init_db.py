#!/usr/bin/env python3
"""
Initialize database with tables and seed data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import create_tables, drop_tables
from app.config import settings

def init_database():
    """Initialize database"""
    print("🗄️  Initializing database...")
    
    if settings.ENVIRONMENT == "development":
        print("⚠️  Development mode: Dropping existing tables...")
        drop_tables()
    
    print("📋 Creating tables...")
    create_tables()
    
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_database()