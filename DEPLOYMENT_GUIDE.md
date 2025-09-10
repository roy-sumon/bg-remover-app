# Django Background Remover - Render.com Deployment Guide

## Overview

This guide will walk you through deploying your Django Background Remover application on Render.com. The application has been configured for production deployment with PostgreSQL database, static file serving, and automatic background removal processing.

## Prerequisites

Before deploying, ensure you have:
- A GitHub or GitLab account
- A Render.com account (free tier available)
- Your project code committed to a Git repository

## Project Structure for Deployment

Your project includes these deployment-specific files:

```
background-remover/
├── render.yaml                 # Render deployment configuration
├── build.sh                   # Build script for Render
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── bg_remover/
│   ├── settings.py           # Production-ready Django settings
│   └── ...
└── remover/
    ├── management/commands/
    │   ├── cleanup_media.py  # Media cleanup command
    │   └── cleanup_old_images.py
    └── ...
```

## Step 1: Prepare Your Repository

1. **Commit all changes to Git**:
   ```bash
   git add .
   git commit -m "Configure for Render.com deployment"
   git push origin main
   ```

2. **Ensure your repository is public** (or you have a paid Render plan for private repos)

## Step 2: Set Up Render Services

### 2.1 Create a New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub/GitLab repository
4. Select your `background-remover` repository
5. Render will automatically detect the `render.yaml` file

### 2.2 Configure Build Settings

Render will automatically use these settings from `render.yaml`:
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn bg_remover.wsgi:application`
- **Environment**: Python 3.11
- **Plan**: Free (for testing)

### 2.3 Environment Variables

Set these environment variables in Render (some are set automatically by `render.yaml`):

**Required Variables:**
```bash
DJANGO_SECRET_KEY=<generate-a-new-secret-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
DATABASE_URL=<automatically-set-by-render>
BACKGROUND_REMOVAL_METHOD=rembg
```

**Optional Variables (for initial admin user):**
```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=your-email@example.com
DJANGO_SUPERUSER_PASSWORD=your-secure-password
```

**To generate a Django secret key:**
```python
# Run this locally or in Python shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Step 3: Database Setup

The `render.yaml` file automatically creates a PostgreSQL database service:
- **Service Name**: `django-background-remover-db`
- **Database Name**: `django_bg_remover`
- **Plan**: Free (1GB storage, expires in 90 days)

The `DATABASE_URL` environment variable will be automatically set by Render.

## Step 4: Deploy Your Application

1. **Trigger Initial Deploy**:
   - Click **"Create Web Service"**
   - Render will start building and deploying your app
   - Monitor the build logs for any issues

2. **Build Process** (automated by `build.sh`):
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Collect static files
   python manage.py collectstatic --no-input
   
   # Run database migrations
   python manage.py migrate
   
   # Create superuser (if env vars provided)
   # Clean up old images
   ```

3. **Deployment URL**:
   Your app will be available at: `https://your-service-name.onrender.com`

## Step 5: Post-Deployment Configuration

### 5.1 Remove Superuser Environment Variables

After the first successful deployment and admin user creation:
1. Go to your service's **Environment** tab in Render
2. Remove these variables for security:
   - `DJANGO_SUPERUSER_USERNAME`
   - `DJANGO_SUPERUSER_EMAIL`
   - `DJANGO_SUPERUSER_PASSWORD`

### 5.2 Test Your Application

1. Visit your deployment URL
2. Test image upload and background removal
3. Check admin interface: `https://your-service-name.onrender.com/admin/`

### 5.3 Monitor and Maintain

1. **Check Logs**: Monitor service logs in Render dashboard
2. **Database Usage**: Monitor PostgreSQL usage (free tier has limits)
3. **Disk Usage**: Run cleanup commands regularly

## Step 6: Maintenance Commands

### 6.1 Clean Up Old Files

Run these commands via Render's shell or through Django admin:

```bash
# Clean up files older than 1 day
python manage.py cleanup_media --days 1 --force

# Clean up old image processing records
python manage.py cleanup_old_images
```

### 6.2 Database Management

```bash
# Create database backup (if needed)
python manage.py dumpdata > backup.json

# Run migrations after code updates
python manage.py migrate
```

## Troubleshooting

### Common Issues

1. **Build Fails - Missing Dependencies**:
   ```bash
   # Check requirements.txt includes all needed packages
   # Verify Python version compatibility
   ```

2. **Database Connection Error**:
   ```bash
   # Verify DATABASE_URL is set correctly
   # Check PostgreSQL service is running
   ```

3. **Static Files Not Loading**:
   ```bash
   # Run collectstatic manually
   python manage.py collectstatic --no-input
   ```

4. **Background Removal Fails**:
   ```bash
   # Check rembg installation
   # Verify BACKGROUND_REMOVAL_METHOD setting
   # Monitor memory usage (free tier has limits)
   ```

### Debug Steps

1. **Check Service Logs** in Render dashboard
2. **Enable Debug Temporarily**:
   ```bash
   # Set DJANGO_DEBUG=True temporarily
   # Remember to set back to False after debugging
   ```

3. **Test Locally First**:
   ```bash
   # Test production settings locally
   export DJANGO_DEBUG=False
   export DATABASE_URL=sqlite:///db.sqlite3
   python manage.py runserver
   ```

## Scaling and Upgrades

### Free Tier Limitations
- **Web Service**: Sleeps after 15 minutes of inactivity
- **Database**: 1GB storage, 90-day limit
- **Build Time**: Up to 20 minutes
- **Memory**: 512MB RAM

### Upgrade Options
- **Paid Plans**: Always-on services, more resources
- **Database**: Persistent PostgreSQL with more storage
- **Custom Domain**: Use your own domain name

## Security Considerations

1. **Environment Variables**: Never commit secrets to Git
2. **HTTPS**: Render provides SSL certificates automatically
3. **Secret Key**: Generate unique secret key for production
4. **Debug Mode**: Always set `DEBUG=False` in production
5. **File Cleanup**: Regular cleanup prevents disk space issues

## Alternative Deployment Options

If you encounter issues with Render, the application is also configured for:
- **Heroku** (modify `requirements.txt` for Heroku-specific packages)
- **Railway** (similar to Render configuration)
- **DigitalOcean App Platform**
- **Any Docker-compatible platform**

## Support and Resources

- **Render Documentation**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Background Remover Issues**: Check project documentation

## Summary Checklist

Before deployment:
- [ ] Code committed to Git repository
- [ ] Environment variables configured
- [ ] Database service created
- [ ] Build and start commands verified

After deployment:
- [ ] Application loads successfully
- [ ] Upload and background removal works
- [ ] Admin interface accessible
- [ ] Cleanup commands functional
- [ ] Monitoring and maintenance scheduled

Your Django Background Remover is now ready for production use on Render.com!
