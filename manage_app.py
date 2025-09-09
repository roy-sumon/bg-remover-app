#!/usr/bin/env python3
"""
Management script for the AI Background Remover Django application.
Provides easy commands for development, deployment, and maintenance.
"""

import os
import sys
import subprocess
import argparse

def run_command(command, description=None):
    """Run a shell command with error handling"""
    if description:
        print(f"🔧 {description}...")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def setup_project():
    """Initial project setup"""
    print("🚀 Setting up AI Background Remover project...")
    
    commands = [
        ("pip install -r requirements.txt", "Installing dependencies"),
        ("python manage.py makemigrations", "Creating database migrations"),
        ("python manage.py migrate", "Applying database migrations"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"❌ Setup failed at: {description}")
            return False
    
    print("✅ Project setup completed successfully!")
    print("\nOptional next steps:")
    print("- Create admin user: python manage.py createsuperuser")
    print("- Start development server: python manage.py runserver")
    return True

def start_server(host="127.0.0.1", port=8000):
    """Start the development server"""
    print(f"🌐 Starting development server at http://{host}:{port}")
    command = f"python manage.py runserver {host}:{port}"
    os.system(command)  # Use os.system for interactive mode

def create_superuser():
    """Create Django superuser"""
    print("👤 Creating Django superuser...")
    os.system("python manage.py createsuperuser")

def collect_static():
    """Collect static files for production"""
    return run_command("python manage.py collectstatic --noinput", 
                      "Collecting static files")

def cleanup_files(dry_run=False, hours=24):
    """Clean up expired files"""
    command = f"python manage.py cleanup_files --hours {hours}"
    if dry_run:
        command += " --dry-run"
    
    description = f"Cleaning up files older than {hours} hours"
    if dry_run:
        description += " (dry run)"
    
    return run_command(command, description)

def run_tests():
    """Run Django tests"""
    return run_command("python manage.py test", "Running tests")

def check_deployment():
    """Run deployment checks"""
    return run_command("python manage.py check --deploy", 
                      "Running deployment checks")

def backup_database():
    """Create database backup"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_db_{timestamp}.json"
    
    return run_command(f"python manage.py dumpdata > {backup_file}", 
                      f"Creating database backup: {backup_file}")

def show_status():
    """Show application status"""
    print("📊 Application Status:")
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000", timeout=2)
        print("✅ Server is running")
    except:
        print("❌ Server is not running")
    
    # Check database
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bg_remover.settings')
        import django
        django.setup()
        
        from remover.models import ImageProcessing
        total_count = ImageProcessing.objects.count()
        completed_count = ImageProcessing.objects.filter(status='completed').count()
        pending_count = ImageProcessing.objects.filter(status='pending').count()
        
        print(f"📈 Database stats:")
        print(f"   Total processings: {total_count}")
        print(f"   Completed: {completed_count}")
        print(f"   Pending: {pending_count}")
        
        # Check expired files
        from django.utils import timezone
        cutoff_time = timezone.now() - timezone.timedelta(hours=24)
        expired_count = ImageProcessing.objects.filter(
            created_at__lt=cutoff_time
        ).count()
        
        if expired_count > 0:
            print(f"🗑️  Files needing cleanup: {expired_count}")
        else:
            print("✅ No expired files")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="AI Background Remover - Management Script"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    subparsers.add_parser('setup', help='Initial project setup')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start development server')
    server_parser.add_argument('--host', default='127.0.0.1', help='Server host')
    server_parser.add_argument('--port', type=int, default=8000, help='Server port')
    
    # Admin command
    subparsers.add_parser('createuser', help='Create Django superuser')
    
    # Static files command
    subparsers.add_parser('static', help='Collect static files')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up expired files')
    cleanup_parser.add_argument('--dry-run', action='store_true', 
                               help='Show what would be deleted')
    cleanup_parser.add_argument('--hours', type=int, default=24, 
                               help='Delete files older than this many hours')
    
    # Test command
    subparsers.add_parser('test', help='Run tests')
    
    # Check command
    subparsers.add_parser('check', help='Run deployment checks')
    
    # Backup command
    subparsers.add_parser('backup', help='Backup database')
    
    # Status command
    subparsers.add_parser('status', help='Show application status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🎨 AI Background Remover - Management Script")
    print("=" * 50)
    
    if args.command == 'setup':
        setup_project()
    elif args.command == 'server':
        start_server(args.host, args.port)
    elif args.command == 'createuser':
        create_superuser()
    elif args.command == 'static':
        collect_static()
    elif args.command == 'cleanup':
        cleanup_files(args.dry_run, args.hours)
    elif args.command == 'test':
        run_tests()
    elif args.command == 'check':
        check_deployment()
    elif args.command == 'backup':
        backup_database()
    elif args.command == 'status':
        show_status()

if __name__ == "__main__":
    main()
