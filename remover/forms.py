from django import forms
from django.core.exceptions import ValidationError
from PIL import Image
import os

from .models import ImageProcessing


class ImageUploadForm(forms.ModelForm):
    """Form for uploading images with validation"""
    
    class Meta:
        model = ImageProcessing
        fields = ['original_image']
        widgets = {
            'original_image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'id': 'image-upload'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['original_image'].required = True
        self.fields['original_image'].help_text = (
            'Upload an image file (JPG, PNG, WebP). Max size: 25MB.'
        )
    
    def clean_original_image(self):
        image = self.cleaned_data.get('original_image')
        
        if not image:
            raise ValidationError('Please select an image file.')
        
        # Check file size (25MB limit for better handling of high-res images)
        if image.size > 25 * 1024 * 1024:
            raise ValidationError('Image file too large. Please select a file under 25MB.')
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if image.content_type not in allowed_types:
            raise ValidationError(
                'Unsupported file type. Please upload a JPG, PNG, or WebP image.'
            )
        
        # Validate image using PIL
        try:
            img = Image.open(image)
            img.verify()  # Verify it's a valid image
            
            # Reset file pointer after verification
            image.seek(0)
            
            # Check minimum dimensions
            img = Image.open(image)
            width, height = img.size
            if width < 50 or height < 50:
                raise ValidationError('Image is too small. Minimum size is 50x50 pixels.')
            
            # Check maximum dimensions (increased for high-res support)
            if width > 6000 or height > 6000:
                raise ValidationError('Image is too large. Maximum size is 6000x6000 pixels.')
            
            # Reset file pointer again
            image.seek(0)
            
        except Exception as e:
            raise ValidationError(f'Invalid image file: {str(e)}')
        
        return image


class BackgroundOptionForm(forms.Form):
    """Form for selecting background options for download"""
    
    BACKGROUND_CHOICES = [
        ('transparent', 'Transparent (PNG)'),
        ('white', 'White Background'),
        ('black', 'Black Background'),
    ]
    
    background_type = forms.ChoiceField(
        choices=BACKGROUND_CHOICES,
        initial='transparent',
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio h-4 w-4 text-blue-600'
        })
    )
