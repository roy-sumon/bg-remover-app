#!/usr/bin/env python3
"""
Test script to verify the upload UI functionality
This script checks if all the UI components are properly configured
"""

import os
import sys
import django
from django.conf import settings
from django.test import Client
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bg_remover.settings')
django.setup()

def test_upload_page():
    """Test that the upload page loads correctly"""
    client = Client()
    
    print("Testing upload page...")
    response = client.get('/')
    
    if response.status_code == 200:
        print("✅ Upload page loads successfully")
        
        # Check for key elements in the HTML
        content = response.content.decode('utf-8')
        
        # Check for upload form
        if 'id="upload-form"' in content:
            print("✅ Upload form is present")
        else:
            print("❌ Upload form is missing")
            
        # Check for file input
        if 'id="image-upload"' in content:
            print("✅ File input is present")
        else:
            print("❌ File input is missing")
            
        # Check for drag and drop zone
        if 'id="drop-zone"' in content:
            print("✅ Drop zone is present")
        else:
            print("❌ Drop zone is missing")
            
        # Check for preview container
        if 'id="preview-container"' in content:
            print("✅ Preview container is present")
        else:
            print("❌ Preview container is missing")
            
        # Check for JavaScript functionality
        if 'handleFiles' in content:
            print("✅ File handling JavaScript is present")
        else:
            print("❌ File handling JavaScript is missing")
            
        # Check for drag and drop handlers
        if 'handleDragEnter' in content:
            print("✅ Drag and drop handlers are present")
        else:
            print("❌ Drag and drop handlers are missing")
            
        # Check for error handling
        if 'showError' in content:
            print("✅ Error handling is present")
        else:
            print("❌ Error handling is missing")
            
        # Check for form validation
        if 'validateFile' in content:
            print("✅ File validation is present")
        else:
            print("❌ File validation is missing")
            
        print("\n📋 Page Content Summary:")
        print(f"   - Page size: {len(content)} characters")
        print(f"   - Contains jQuery: {'jquery' in content.lower()}")
        print(f"   - Contains TailwindCSS classes: {'tailwind' in content.lower() or 'bg-' in content}")
        print(f"   - Contains drag-and-drop: {'dragenter' in content}")
        print(f"   - Contains file preview: {'preview-image' in content}")
        
    else:
        print(f"❌ Upload page failed to load. Status: {response.status_code}")

def test_form_configuration():
    """Test that the Django form is properly configured"""
    from remover.forms import ImageUploadForm
    
    print("\n🔧 Testing form configuration...")
    
    form = ImageUploadForm()
    
    # Check if form has the correct field
    if 'original_image' in form.fields:
        print("✅ Form has original_image field")
        
        # Check field attributes
        field = form.fields['original_image']
        widget_attrs = field.widget.attrs
        
        if widget_attrs.get('id') == 'image-upload':
            print("✅ Field has correct ID")
        else:
            print("❌ Field ID is incorrect or missing")
            
        if widget_attrs.get('accept') == 'image/*':
            print("✅ Field accepts image files")
        else:
            print("❌ Field accept attribute is incorrect")
            
        if 'hidden' in widget_attrs.get('class', ''):
            print("✅ Field is hidden (for custom UI)")
        else:
            print("❌ Field is not hidden")
            
    else:
        print("❌ Form is missing original_image field")

def main():
    """Run all tests"""
    print("🧪 Testing Django Image Background Remover Upload UI")
    print("=" * 60)
    
    try:
        test_upload_page()
        test_form_configuration()
        
        print("\n" + "=" * 60)
        print("✅ Upload UI test completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Run: python manage.py runserver")
        print("   2. Open: http://127.0.0.1:8000")
        print("   3. Test drag-and-drop or click-to-upload functionality")
        print("   4. Verify file preview and validation work")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
