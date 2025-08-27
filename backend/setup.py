#!/usr/bin/env python
"""
Enhanced Setup script for NXTSCHOLAR Django Backend
"""

import os
import sys
import subprocess
from pathlib import Path
import json

def run_command(command, description, capture_output=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        if capture_output and hasattr(e, 'stderr') and e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_database_connection(python_path):
    """Check if database connection is working"""
    print("\n🔍 Checking database connection...")
    try:
        result = subprocess.run(
            f"{python_path} manage.py check --database default", 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print("✅ Database connection successful")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Database connection failed:")
        print(f"Error: {e.stderr}")
        return False

def reset_migrations(python_path):
    """Reset migrations if there are conflicts"""
    print("\n🔄 Attempting to reset migrations...")
    
    # Find all apps with migrations
    apps_with_migrations = []
    for path in Path(".").glob("*/migrations"):
        if path.parent.name != "__pycache__":
            apps_with_migrations.append(path.parent.name)
    
    print(f"Found apps with migrations: {apps_with_migrations}")
    
    # Delete migration files (keep __init__.py)
    for app in apps_with_migrations:
        migration_path = Path(f"{app}/migrations")
        if migration_path.exists():
            for file in migration_path.glob("*.py"):
                if file.name != "__init__.py":
                    file.unlink()
                    print(f"Deleted {file}")
    
    # Delete database if SQLite
    db_file = Path("db.sqlite3")
    if db_file.exists():
        db_file.unlink()
        print("Deleted db.sqlite3")
    
    return True

def create_env_file():
    """Create .env file with default values"""
    env_content = """# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (SQLite by default)
# Uncomment and modify for PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost:5432/nxtscholar

# Email Settings (optional)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# Media and Static Files
MEDIA_ROOT=media/
STATIC_ROOT=staticfiles/

# Security Settings (for production)
# SECURE_SSL_REDIRECT=True
# SECURE_BROWSER_XSS_FILTER=True
# SECURE_CONTENT_TYPE_NOSNIFF=True
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("✅ Created .env file with default values")

def handle_superuser_creation(python_path):
    """Handle superuser creation with better error handling"""
    print("\n👤 Creating superuser...")
    
    # First, try the interactive way
    print("Choose superuser creation method:")
    print("1. Interactive (recommended)")
    print("2. Skip for now")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        print("Please enter the following information for the admin user:")
        try:
            subprocess.run(f"{python_path} manage.py createsuperuser", shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            print("⚠️  Interactive superuser creation failed.")
            print("You can create a superuser later using: python manage.py createsuperuser")
            return False
    else:
        print("⚠️  Superuser creation skipped. You can create one later using: python manage.py createsuperuser")
        return True

def check_requirements():
    """Check if requirements.txt exists and install dependencies"""
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt not found")
        print("Creating basic requirements.txt...")
        
        basic_requirements = """Django>=4.2.0,<5.0.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
python-decouple>=3.8
Pillow>=10.0.0
django-extensions>=3.2.0
"""
        with open("requirements.txt", "w") as f:
            f.write(basic_requirements)
        print("✅ Created basic requirements.txt")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up NXTSCHOLAR Django Backend...")
    print("=" * 50)
    
    # Check if Python 3.8+ is available
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment if it doesn't exist
    venv_path = Path("venv")
    if not venv_path.exists():
        print("\n📦 Creating virtual environment...")
        if not run_command("python -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Determine the correct pip and python paths
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
        python_path = "venv\\Scripts\\python"
        activate_path = "venv\\Scripts\\activate"
    else:  # Unix/Linux/Mac
        pip_path = "venv/bin/pip"
        python_path = "venv/bin/python"
        activate_path = "source venv/bin/activate"
    
    # Check and create requirements.txt
    check_requirements()
    
    # Upgrade pip first
    if not run_command(f"{pip_path} install --upgrade pip", "Upgrading pip"):
        print("⚠️  Pip upgrade failed, continuing anyway...")
    
    # Install requirements
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("\n📝 Creating .env file...")
        if Path("env.example").exists():
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ .env file created from template")
        else:
            create_env_file()
        print("⚠️  Please update the .env file with your actual configuration values")
    else:
        print("✅ .env file already exists")
    
    # Check database connection
    if not check_database_connection(python_path):
        print("⚠️  Database connection issues detected")
        reset_choice = input("Would you like to reset migrations? (y/N): ").lower().strip()
        if reset_choice == 'y':
            reset_migrations(python_path)
        else:
            print("❌ Database issues not resolved. Please fix manually.")
            sys.exit(1)
    
    # Run Django migrations
    print("\n🔄 Running Django migrations...")
    
    # First, try makemigrations
    if not run_command(f"{python_path} manage.py makemigrations", "Creating migrations"):
        print("⚠️  makemigrations failed, trying to continue...")
    
    # Then migrate
    migrate_success = run_command(f"{python_path} manage.py migrate", "Running migrations")
    if not migrate_success:
        print("❌ Migration failed. Attempting to fix...")
        reset_choice = input("Would you like to reset the database and migrations? (y/N): ").lower().strip()
        if reset_choice == 'y':
            reset_migrations(python_path)
            # Try migrations again
            if not run_command(f"{python_path} manage.py makemigrations", "Creating fresh migrations"):
                sys.exit(1)
            if not run_command(f"{python_path} manage.py migrate", "Running fresh migrations"):
                sys.exit(1)
        else:
            sys.exit(1)
    
    # Create superuser
    handle_superuser_creation(python_path)
    
    # Collect static files
    static_success = run_command(f"{python_path} manage.py collectstatic --noinput", "Collecting static files")
    if not static_success:
        print("⚠️  Static files collection failed, but this is not critical for development")
    
    # Final checks
    print("\n🔍 Running final system checks...")
    if not run_command(f"{python_path} manage.py check", "System checks"):
        print("⚠️  Some system checks failed, but setup completed")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("=" * 50)
    print("\n📋 Next steps:")
    print(f"1. Activate virtual environment: {activate_path}")
    print("2. Update the .env file with your actual configuration values")
    print("3. Start the development server: python manage.py runserver")
    print("4. Access the admin interface at: http://localhost:8000/admin/")
    print("5. API endpoints will be available at: http://localhost:8000/api/")
    print("\n📚 Useful commands:")
    print("- Create superuser: python manage.py createsuperuser")
    print("- Run tests: python manage.py test")
    print("- Show URLs: python manage.py show_urls (if django-extensions installed)")
    print("- Django shell: python manage.py shell")
    print("\n💡 Troubleshooting:")
    print("- If migrations fail, delete db.sqlite3 and migration files, then run this script again")
    print("- Check the .env file for correct database settings")
    print("- Ensure all required environment variables are set")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the error and try again")
        sys.exit(1)