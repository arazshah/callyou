#!/usr/bin/env python3
"""
Development helper script
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/dev.py [command]")
        print("Commands:")
        print("  setup    - Setup development environment")
        print("  start    - Start development server")
        print("  test     - Run tests")
        print("  lint     - Run linting")
        print("  format   - Format code")
        print("  migrate  - Run database migrations")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        run_command("docker-compose up -d postgres redis", "Starting database services")
        run_command("python scripts/init_db.py", "Initializing database")
        run_command("alembic upgrade head", "Running migrations")
        
    elif command == "start":
        run_command("docker-compose up", "Starting all services")
        
    elif command == "test":
        run_command("pytest tests/ -v --cov=app", "Running tests")
        
    elif command == "lint":
        run_command("flake8 app/", "Running linting")
        run_command("mypy app/", "Running type checking")
        
    elif command == "format":
        run_command("black app/ tests/", "Formatting code with Black")
        run_command("isort app/ tests/", "Sorting imports")
        
    elif command == "migrate":
        run_command("alembic upgrade head", "Running migrations")
        
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()