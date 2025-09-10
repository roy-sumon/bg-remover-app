"""
URL configuration for bg_remover project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import Http404
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('remover.urls')),
]

# Serve media files
if settings.DEBUG:
    # Development: serve media files with Django
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Production: serve media files with custom view for better control
    def protected_media_serve(request, path, document_root=None, show_indexes=False):
        """Serve media files in production with some basic protection"""
        # You can add authentication/authorization here if needed
        # For now, we'll serve files directly but this can be enhanced
        
        # Ensure the file exists and is in the media directory
        full_path = os.path.join(document_root, path)
        if not os.path.exists(full_path) or not full_path.startswith(document_root):
            raise Http404("Media file not found")
            
        return serve(request, path, document_root, show_indexes)
    
    # Add media URL pattern for production
    urlpatterns += [
        path(settings.MEDIA_URL.lstrip('/'), protected_media_serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
