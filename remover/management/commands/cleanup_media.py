"""
Management command to cleanup media files in production environment
This is important for Render.com as they have disk space limitations
"""

import os
import time
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from remover.models import ImageProcessing


class Command(BaseCommand):
    help = 'Clean up old media files and orphaned uploads'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Delete files older than specified days (default: 1)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup without confirmation'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(
            self.style.SUCCESS(f'Starting media cleanup (files older than {days} days)')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No files will actually be deleted')
            )

        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Clean up database records first
        deleted_records = self.cleanup_database_records(cutoff_date, dry_run)
        
        # Clean up orphaned files
        deleted_files = self.cleanup_orphaned_files(cutoff_date, dry_run, force)
        
        # Clean up empty directories
        cleaned_dirs = self.cleanup_empty_directories(dry_run)

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('CLEANUP SUMMARY:')
        self.stdout.write(f'Database records deleted: {deleted_records}')
        self.stdout.write(f'Orphaned files deleted: {deleted_files}')
        self.stdout.write(f'Empty directories cleaned: {cleaned_dirs}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nThis was a dry run. No actual changes were made.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nCleanup completed successfully!')
            )

    def cleanup_database_records(self, cutoff_date, dry_run):
        """Clean up old database records"""
        old_records = ImageProcessing.objects.filter(
            created_at__lt=cutoff_date
        )
        
        count = old_records.count()
        
        if count > 0:
            self.stdout.write(f'Found {count} old database records to delete')
            
            if not dry_run:
                # Delete files associated with records before deleting records
                for record in old_records:
                    if record.original_image and os.path.exists(record.original_image.path):
                        try:
                            os.remove(record.original_image.path)
                            self.stdout.write(f'Deleted: {record.original_image.path}')
                        except OSError as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error deleting {record.original_image.path}: {e}')
                            )
                    
                    if record.processed_image and os.path.exists(record.processed_image.path):
                        try:
                            os.remove(record.processed_image.path)
                            self.stdout.write(f'Deleted: {record.processed_image.path}')
                        except OSError as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error deleting {record.processed_image.path}: {e}')
                            )
                
                old_records.delete()
        
        return count

    def cleanup_orphaned_files(self, cutoff_date, dry_run, force):
        """Clean up files not referenced in database"""
        media_root = settings.MEDIA_ROOT
        deleted_count = 0
        
        if not os.path.exists(media_root):
            self.stdout.write('Media directory does not exist')
            return 0

        self.stdout.write(f'Scanning media directory: {media_root}')
        
        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Get file modification time
                try:
                    file_mtime = datetime.fromtimestamp(
                        os.path.getmtime(file_path), 
                        tz=timezone.get_current_timezone()
                    )
                except OSError:
                    continue
                
                # Skip if file is not old enough
                if file_mtime >= cutoff_date:
                    continue
                
                # Check if file is referenced in database
                relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                
                is_referenced = ImageProcessing.objects.filter(
                    models.Q(original_image=relative_path) |
                    models.Q(processed_image=relative_path)
                ).exists()
                
                if not is_referenced:
                    if dry_run:
                        self.stdout.write(f'Would delete orphaned file: {file_path}')
                        deleted_count += 1
                    else:
                        try:
                            if force or self.confirm_deletion(file_path):
                                os.remove(file_path)
                                self.stdout.write(f'Deleted orphaned file: {file_path}')
                                deleted_count += 1
                        except OSError as e:
                            self.stdout.write(
                                self.style.ERROR(f'Error deleting {file_path}: {e}')
                            )
        
        return deleted_count

    def cleanup_empty_directories(self, dry_run):
        """Remove empty directories in media root"""
        media_root = settings.MEDIA_ROOT
        cleaned_count = 0
        
        if not os.path.exists(media_root):
            return 0
        
        # Walk directories in reverse order (deepest first)
        for root, dirs, files in os.walk(media_root, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                
                try:
                    # Check if directory is empty
                    if not os.listdir(dir_path):
                        if dry_run:
                            self.stdout.write(f'Would remove empty directory: {dir_path}')
                            cleaned_count += 1
                        else:
                            os.rmdir(dir_path)
                            self.stdout.write(f'Removed empty directory: {dir_path}')
                            cleaned_count += 1
                except OSError:
                    # Directory might not be empty or might have permission issues
                    pass
        
        return cleaned_count

    def confirm_deletion(self, file_path):
        """Ask for confirmation before deleting a file"""
        response = input(f'Delete {file_path}? (y/N): ')
        return response.lower() == 'y'


# Import models at the end to avoid circular imports
from django.db import models
