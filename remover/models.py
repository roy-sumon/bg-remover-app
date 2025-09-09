import os
import uuid
from django.db import models
from django.urls import reverse
from django.utils import timezone
from PIL import Image


def upload_to_uploads(instance, filename):
    """Generate unique filename for uploaded images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads', filename)


def upload_to_processed(instance, filename):
    """Generate unique filename for processed images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}_processed.{ext}"
    return os.path.join('processed', filename)


class ImageProcessing(models.Model):
    """Model to track image processing requests"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_image = models.ImageField(upload_to=upload_to_uploads)
    processed_image = models.ImageField(upload_to=upload_to_processed, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Original image metadata
    original_width = models.PositiveIntegerField(blank=True, null=True)
    original_height = models.PositiveIntegerField(blank=True, null=True)
    original_size = models.PositiveIntegerField(blank=True, null=True)  # in bytes
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Image Processing'
        verbose_name_plural = 'Image Processings'
    
    def __str__(self):
        return f"Processing {self.id} - {self.status}"
    
    def save(self, *args, **kwargs):
        if self.original_image and not self.original_width:
            # Extract metadata from original image
            try:
                with Image.open(self.original_image.path) as img:
                    self.original_width, self.original_height = img.size
                    self.original_size = self.original_image.size
            except Exception:
                pass
        
        if self.status == 'completed' and not self.processed_at:
            self.processed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('remover:result', kwargs={'pk': self.pk})
    
    @property
    def is_expired(self):
        """Check if the processing request is older than 24 hours"""
        if self.created_at:
            return timezone.now() - self.created_at > timezone.timedelta(hours=24)
        return False
    
    @property
    def processing_duration(self):
        """Get processing duration in seconds"""
        if self.processed_at and self.created_at:
            return (self.processed_at - self.created_at).total_seconds()
        return None
    
    def cleanup_files(self):
        """Clean up associated files"""
        try:
            if self.original_image and os.path.exists(self.original_image.path):
                os.remove(self.original_image.path)
        except Exception:
            pass
            
        try:
            if self.processed_image and os.path.exists(self.processed_image.path):
                os.remove(self.processed_image.path)
        except Exception:
            pass
