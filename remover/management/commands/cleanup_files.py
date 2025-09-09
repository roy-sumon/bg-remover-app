import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from remover.models import ImageProcessing


class Command(BaseCommand):
    help = 'Clean up expired image files and database records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting anything',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Delete files older than this many hours (default: 24)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        hours = options['hours']
        
        self.stdout.write(f"Looking for files older than {hours} hours...")
        
        # Find expired processing records
        cutoff_time = timezone.now() - timezone.timedelta(hours=hours)
        expired_processings = ImageProcessing.objects.filter(
            created_at__lt=cutoff_time
        )
        
        count = expired_processings.count()
        self.stdout.write(f"Found {count} expired processing record(s)")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No expired files to clean up"))
            return
        
        deleted_files = 0
        deleted_records = 0
        
        for processing in expired_processings:
            if dry_run:
                self.stdout.write(f"Would delete: {processing.id} (created: {processing.created_at})")
                if processing.original_image:
                    self.stdout.write(f"  - Original: {processing.original_image.path}")
                if processing.processed_image:
                    self.stdout.write(f"  - Processed: {processing.processed_image.path}")
            else:
                # Clean up files
                try:
                    if processing.original_image and os.path.exists(processing.original_image.path):
                        os.remove(processing.original_image.path)
                        deleted_files += 1
                        self.stdout.write(f"Deleted original: {processing.original_image.path}")
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to delete original file: {e}")
                    )
                
                try:
                    if processing.processed_image and os.path.exists(processing.processed_image.path):
                        os.remove(processing.processed_image.path)
                        deleted_files += 1
                        self.stdout.write(f"Deleted processed: {processing.processed_image.path}")
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to delete processed file: {e}")
                    )
                
                # Delete database record
                processing.delete()
                deleted_records += 1
                self.stdout.write(f"Deleted record: {processing.id}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would delete {count} record(s) and associated files"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully deleted {deleted_records} record(s) and {deleted_files} file(s)"
                )
            )
        
        # Clean up empty directories
        self._cleanup_empty_dirs(dry_run)
    
    def _cleanup_empty_dirs(self, dry_run):
        """Remove empty upload and processed directories"""
        from django.conf import settings
        
        dirs_to_check = [
            os.path.join(settings.MEDIA_ROOT, 'uploads'),
            os.path.join(settings.MEDIA_ROOT, 'processed'),
        ]
        
        for dir_path in dirs_to_check:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                try:
                    # Check if directory is empty
                    if not os.listdir(dir_path):
                        if dry_run:
                            self.stdout.write(f"Would remove empty directory: {dir_path}")
                        else:
                            # Don't actually remove the directories, just log
                            self.stdout.write(f"Empty directory found: {dir_path}")
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Error checking directory {dir_path}: {e}")
                    )
