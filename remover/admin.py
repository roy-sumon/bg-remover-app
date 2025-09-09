from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ImageProcessing


@admin.register(ImageProcessing)
class ImageProcessingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'status', 'created_at', 'processed_at', 
        'original_size_display', 'processing_time_display', 'thumbnail_display'
    ]
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = ['id']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'processed_at',
        'original_width', 'original_height', 'original_size',
        'processing_duration', 'thumbnail_display', 'processed_thumbnail_display'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'status', 'error_message')
        }),
        ('Images', {
            'fields': (
                'original_image', 'thumbnail_display',
                'processed_image', 'processed_thumbnail_display'
            )
        }),
        ('Metadata', {
            'fields': (
                'original_width', 'original_height', 'original_size',
                'processing_duration'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def original_size_display(self, obj):
        if obj.original_width and obj.original_height:
            return f"{obj.original_width}×{obj.original_height}px"
        return "Unknown"
    original_size_display.short_description = "Size"
    
    def processing_time_display(self, obj):
        duration = obj.processing_duration
        if duration:
            return f"{duration:.1f}s"
        return "N/A"
    processing_time_display.short_description = "Processing Time"
    
    def thumbnail_display(self, obj):
        if obj.original_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.original_image.url
            )
        return "No image"
    thumbnail_display.short_description = "Original Thumbnail"
    
    def processed_thumbnail_display(self, obj):
        if obj.processed_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.processed_image.url
            )
        return "No processed image"
    processed_thumbnail_display.short_description = "Processed Thumbnail"
    
    def has_add_permission(self, request):
        # Disable adding through admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow viewing but not editing
        return True
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion for cleanup
        return True
    
    actions = ['cleanup_files']
    
    def cleanup_files(self, request, queryset):
        """Custom admin action to clean up selected files"""
        deleted_files = 0
        for processing in queryset:
            try:
                processing.cleanup_files()
                processing.delete()
                deleted_files += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error deleting {processing.id}: {e}",
                    level='ERROR'
                )
        
        if deleted_files:
            self.message_user(
                request,
                f"Successfully cleaned up {deleted_files} processing record(s)",
                level='SUCCESS'
            )
    
    cleanup_files.short_description = "Clean up selected files"
