from django.urls import path
from . import views

app_name = 'remover'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('process/<uuid:pk>/', views.ProcessView.as_view(), name='process'),
    path('result/<uuid:pk>/', views.ResultView.as_view(), name='result'),
    path('download/<uuid:pk>/', views.DownloadView.as_view(), name='download'),
    
    # AJAX endpoints
    path('api/process/<uuid:pk>/', views.process_image_ajax, name='process_ajax'),
    path('api/status/<uuid:pk>/', views.status_check, name='status_check'),
]
