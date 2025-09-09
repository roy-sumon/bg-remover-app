# AI Background Remover Website

A professional Django-based web application that removes backgrounds from images using local Python libraries (no API required). Features a modern, responsive interface built with TailwindCSS.

## Features

🎯 **Core Features**
- Drag-and-drop image upload
- Local AI-powered background removal (no API required)
- Multiple processing methods (rembg, OpenCV, Pillow)
- Before/after comparison slider
- Multiple download options (transparent PNG, white/black backgrounds)
- Real-time processing status
- Secure file handling with auto-cleanup

🎨 **UI/UX Features**
- Modern, clean design with TailwindCSS
- Fully responsive (mobile-first approach)
- Interactive before/after slider
- Loading animations and progress bars
- Professional error handling

🔒 **Security Features**
- Session-based access control
- File validation and size limits
- Automatic file cleanup after 24 hours
- CSRF protection
- Secure file handling

## Tech Stack

- **Backend**: Django 4.2.7
- **Frontend**: TailwindCSS (CDN)
- **AI Processing**: Local Python libraries (rembg, OpenCV, Pillow)
- **Image Processing**: Pillow (PIL), NumPy
- **Database**: SQLite (default, can be changed)
- **Server**: Django development server / Gunicorn

## Quick Start

### 1. Clone and Setup

```bash
cd "D:\Django Projects\background-remover"
pip install -r requirements.txt
```

### 2. Environment Configuration

Create/update your `.env` file:

```env
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
BACKGROUND_REMOVAL_METHOD=auto
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Note**: No API key required! The application uses local Python libraries for background removal.

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

### 4. Run the Application

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to use the application.

## Background Removal Methods

The application automatically selects the best available method:

### 1. rembg (Recommended)
- **Best Quality**: Uses pre-trained AI models for professional results
- **Installation**: `pip install rembg`
- **Models**: Automatically downloads AI models on first use
- **Best for**: Professional photos, portraits, products

### 2. OpenCV (Fallback)
- **Good Quality**: Uses edge detection and contour analysis
- **Installation**: `pip install opencv-python`
- **Processing**: Fast, works well with high-contrast images
- **Best for**: Simple backgrounds, high contrast subjects

### 3. Pillow (Always Available)
- **Basic Quality**: Uses color-based background detection
- **Installation**: Built-in with Django
- **Processing**: Simple corner-based background detection
- **Best for**: Basic processing when other methods aren't available

### Configuration

Set your preferred method in `.env`:
```env
BACKGROUND_REMOVAL_METHOD=auto  # auto, rembg, opencv, pillow
```

## Project Structure

```
background-remover/
├── bg_remover/              # Django project settings
│   ├── settings.py          # Configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI config
├── remover/                 # Main application
│   ├── models.py           # Data models
│   ├── views.py            # View logic
│   ├── forms.py            # Form definitions
│   ├── services.py         # AI service integration
│   ├── admin.py            # Admin interface
│   └── management/         # Custom commands
│       └── commands/
│           └── cleanup_files.py
├── templates/               # HTML templates
│   ├── base.html           # Base template
│   └── remover/
│       ├── index.html      # Home page
│       ├── processing.html # Processing page
│       ├── result.html     # Results page
│       └── error.html      # Error page
├── media/                   # User uploads (auto-created)
│   ├── uploads/            # Original images
│   └── processed/          # Processed images
└── static/                  # Static files
```

## Usage

### Basic Workflow

1. **Upload Image**: Drag & drop or click to select an image
2. **Processing**: AI removes the background (typically takes a few seconds)
3. **Review Results**: Use the before/after slider to compare images
4. **Download**: Choose from transparent PNG, white background, or black background

### Supported Formats

- **Input**: JPG, PNG, WebP
- **Output**: PNG (transparent), JPG (solid backgrounds)
- **Size Limits**: 10MB max, 50x50px minimum, 4000x4000px maximum

### Admin Interface

Access the Django admin at `/admin/` to:
- View processing records
- Monitor system usage
- Clean up files manually
- View processing statistics

## Management Commands

### File Cleanup

Automatically clean up expired files:

```bash
# Dry run (see what would be deleted)
python manage.py cleanup_files --dry-run

# Delete files older than 24 hours (default)
python manage.py cleanup_files

# Delete files older than custom hours
python manage.py cleanup_files --hours 48
```

### Recommended Cron Job

Add to your server's crontab for automatic cleanup:

```cron
# Clean up files daily at 2 AM
0 2 * * * cd /path/to/project && python manage.py cleanup_files
```

## Deployment

### Environment Variables

For production, set these environment variables:

```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
BACKGROUND_REMOVAL_METHOD=rembg
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Static Files

```bash
python manage.py collectstatic
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn bg_remover.wsgi:application --bind 0.0.0.0:8000
```

### Nginx Configuration (Example)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/your/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/your/media/;
    }
}
```

## Development

### Adding New Features

The codebase is well-structured for extensions:

- **Models**: Add fields to `ImageProcessing` model
- **Views**: Extend views in `remover/views.py`
- **Templates**: Modify templates in `templates/remover/`
- **Services**: Extend AI services in `remover/services.py`

### Testing

Basic testing setup:

```bash
python manage.py test
```

### Code Style

The project follows Django best practices:
- Class-based views for consistency
- Proper separation of concerns
- Comprehensive error handling
- Security best practices

## Troubleshooting

### Common Issues

1. **"Background removal error"**: Try installing additional libraries (rembg, opencv-python)
2. **"File upload failed"**: Ensure file meets size/format requirements
3. **"Processing stuck"**: Refresh the page or try a different image
4. **Media files not serving**: Check `MEDIA_URL` and `MEDIA_ROOT` settings

### Debug Mode

Enable debug mode in `.env`:

```env
DEBUG=True
```

This will show detailed error messages and serve media files during development.

### Logs

Check Django logs for detailed error information:

```bash
# In development
python manage.py runserver --verbosity=2

# Check specific app logs
tail -f /path/to/your/logs/django.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open-source. Feel free to use it for personal or commercial projects.

## Support

For issues or questions:
1. Check this README
2. Review the Django documentation
3. Check your AI service API documentation
4. Create an issue in the repository

---

**Connect with Sumon Roy | Made with ❤️ using Django**
