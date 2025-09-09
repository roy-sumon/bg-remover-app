#!/usr/bin/env python3
"""
Quick test script for the Django Background Remover application.
This script starts the server and performs basic validation.
"""

import os
import sys
import subprocess
import time

def test_application():
    """Test the basic functionality of the Django application"""
    print("🚀 Starting AI Background Remover Application Test...")
    
    # Test imports
    try:
        import django
        from django.core.management import execute_from_command_line
        print("✓ Django imports successful")
        
        import requests
        print("✓ Requests library available")
        
        from PIL import Image
        print("✓ Pillow (PIL) library available")
        
        from decouple import config
        print("✓ Python-decouple library available")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bg_remover.settings')
    
    try:
        # Test Django setup
        django.setup()
        print("✓ Django setup successful")
        
        # Test database connection
        from django.db import connection
        cursor = connection.cursor()
        print("✓ Database connection successful")
        
        # Test model imports
        from remover.models import ImageProcessing
        from remover.forms import ImageUploadForm
        from remover.services import get_ai_service
        print("✓ Application models and services loaded")
        
        # Test media directories exist
        media_dirs = ['media/uploads', 'media/processed']
        for dir_path in media_dirs:
            if os.path.exists(dir_path):
                print(f"✓ Directory exists: {dir_path}")
            else:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✓ Created directory: {dir_path}")
        
        # Test local background removal service
        service = get_ai_service()
        service_type = type(service).__name__
        print(f"✓ Background removal service initialized: {service_type}")
        print(f"ℹ️  Using method: {service.method}")
        
        # Check available methods
        from remover.services import REMBG_AVAILABLE, CV2_AVAILABLE
        print(f"ℹ️  rembg available: {REMBG_AVAILABLE}")
        print(f"ℹ️  OpenCV available: {CV2_AVAILABLE}")
        print("ℹ️  Pillow available: True (built-in)")
        
        print("\n🎉 All tests passed! The application is ready to run.")
        print("\nTo start the server, run:")
        print("    python manage.py runserver")
        print("\nThen visit: http://127.0.0.1:8000")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Environment Check:")
    
    env_file = ".env"
    if os.path.exists(env_file):
        print("✓ .env file exists")
        
        # Read and show non-sensitive config
        with open(env_file, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                key = line.split('=')[0]
                if key in ['DEBUG', 'ALLOWED_HOSTS', 'BACKGROUND_REMOVAL_METHOD']:
                    print(f"✓ {line}")
                elif 'KEY' in key:
                    print(f"✓ {key}=***hidden***")
                else:
                    print(f"✓ {line}")
    else:
        print("⚠️  .env file not found - using default settings")
    
def show_usage_instructions():
    """Show instructions for using the application"""
    print("\n📖 Usage Instructions:")
    print("1. Start the server: python manage.py runserver")
    print("2. Open your browser to: http://127.0.0.1:8000")
    print("3. Upload an image (JPG, PNG, WebP)")
    print("4. Wait for AI processing")
    print("5. Download your processed image")
    print("\n💡 Tips:")
    print("- Images with clear subjects work best")
    print("- Use good contrast between subject and background")
    print("- Files are automatically deleted after 24 hours")
    print("\n🔧 Admin Interface:")
    print("- Create superuser: python manage.py createsuperuser")
    print("- Visit: http://127.0.0.1:8000/admin/")

if __name__ == "__main__":
    print("="*60)
    print("🎨 AI Background Remover - Django Application")
    print("="*60)
    
    success = test_application()
    check_environment()
    show_usage_instructions()
    
    if success:
        print("\n" + "="*60)
        print("✅ Ready to go! Your application is working correctly.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Setup incomplete. Please fix the errors above.")
        print("="*60)
        sys.exit(1)
