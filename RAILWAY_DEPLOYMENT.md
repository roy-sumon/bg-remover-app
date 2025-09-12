# Railway Deployment Guide for Django Background Remover

## 🚀 Quick Deployment Steps

### 1. **Prepare Your Repository**
Ensure all these files are in your GitHub repository:
- ✅ `requirements.txt`
- ✅ `Procfile`
- ✅ `railway.toml`
- ✅ `start.sh`
- ✅ `runtime.txt`
- ✅ `manage.py`

### 2. **Connect to Railway**
1. Go to [Railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `bg-remover-app` repository

### 3. **Add Database Service**
1. In your Railway project dashboard
2. Click "New Service"
3. Select "PostgreSQL"
4. Railway will automatically provide `DATABASE_URL`

### 4. **Set Environment Variables**
In Railway project settings → Variables, add:

```bash
# REQUIRED
DJANGO_SECRET_KEY=your-50-character-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=web-production-a944f.up.railway.app

# OPTIONAL
BACKGROUND_REMOVAL_METHOD=auto
```

### 5. **Generate Secret Key**
Run this in Python to generate a secure secret key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 6. **Deploy**
1. Railway will automatically start building
2. Check the build logs for any errors
3. Once deployed, your app will be available at your Railway domain

---

## 🔧 Troubleshooting Common Issues

### **Build Fails**
- Check that `requirements.txt` has all dependencies
- Ensure `python-3.11` in `runtime.txt` is supported
- Look at build logs for specific error messages

### **App Doesn't Start**
- Verify `DJANGO_SECRET_KEY` is set
- Check that `DJANGO_DEBUG=False`
- Ensure database service is running

### **Static Files Not Loading**
- Verify `STATICFILES_STORAGE` in settings.py
- Check that `collectstatic` runs in build process
- Ensure WhiteNoise is configured correctly

### **Database Errors**
- Confirm PostgreSQL service is added
- Check that `DATABASE_URL` is automatically set
- Verify migrations run during startup

---

## 📋 Deployment Checklist

- [ ] All files committed and pushed to GitHub
- [ ] Railway project connected to GitHub repo  
- [ ] PostgreSQL database service added
- [ ] Environment variables set (especially DJANGO_SECRET_KEY)
- [ ] Domain updated in ALLOWED_HOSTS if using custom domain
- [ ] Build completes successfully
- [ ] App starts without errors
- [ ] Test file upload functionality
- [ ] Verify background removal works

---

## 🌐 Custom Domain (Optional)

To use a custom domain:
1. Add your domain in Railway project settings
2. Update `DJANGO_ALLOWED_HOSTS` to include your domain
3. Configure DNS to point to Railway

---

## 📞 Support

If deployment fails:
1. Check Railway build/deploy logs
2. Verify all environment variables are set
3. Test locally first with same environment variables
4. Ensure GitHub repo has latest changes

Your Django Background Remover should now be live on Railway! 🎉
