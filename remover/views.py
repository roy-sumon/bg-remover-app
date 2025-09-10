import logging
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.core.files.storage import default_storage

from .models import ImageProcessing
from .forms import ImageUploadForm, BackgroundOptionForm
from .services import get_ai_service, BackgroundRemovalError, BackgroundProcessor

logger = logging.getLogger(__name__)


class HomeView(View):
    """Home page with image upload form"""
    
    def get(self, request):
        form = ImageUploadForm()
        return render(request, 'remover/index.html', {
            'form': form,
            'title': 'AI Background Remover'
        })
    
    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Save the uploaded image
                processing = form.save()
                
                # Store processing ID in session for security
                request.session[f'processing_{processing.id}'] = True
                
                # Redirect to processing page
                return redirect('remover:process', pk=processing.id)
                
            except Exception as e:
                logger.error(f"Error saving uploaded image: {str(e)}")
                messages.error(request, 'Failed to upload image. Please try again.')
        
        return render(request, 'remover/index.html', {
            'form': form,
            'title': 'AI Background Remover'
        })


class ProcessView(View):
    """Process uploaded image and show loading state"""
    
    def get(self, request, pk):
        processing = get_object_or_404(ImageProcessing, pk=pk)
        
        # Check session permission
        if not request.session.get(f'processing_{processing.id}'):
            raise Http404("Processing request not found or expired.")
        
        # If already processed, redirect to result
        if processing.status == 'completed':
            return redirect('remover:result', pk=processing.id)
        
        # If failed, show error
        if processing.status == 'failed':
            return render(request, 'remover/error.html', {
                'error_message': processing.error_message or 'Processing failed.',
                'processing': processing
            })
        
        return render(request, 'remover/processing.html', {
            'processing': processing,
            'title': 'Processing Image...'
        })


@csrf_exempt
@require_http_methods(["POST"])
def process_image_ajax(request, pk):
    """AJAX endpoint to process image with Warp AI"""
    try:
        processing = get_object_or_404(ImageProcessing, pk=pk)
        
        # Check session permission
        if not request.session.get(f'processing_{processing.id}'):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Check if already processed
        if processing.status == 'completed':
            return JsonResponse({
                'status': 'completed',
                'redirect_url': reverse('remover:result', kwargs={'pk': processing.id})
            })
        
        # Update status to processing
        processing.status = 'processing'
        processing.save()
        
        # Process with AI Service
        try:
            ai_service = get_ai_service()
            processed_image = ai_service.remove_background(processing.original_image.path)
            
            if processed_image:
                # Save processed image
                processing.processed_image.save(
                    f'processed_{processing.id}.png',
                    processed_image,
                    save=True
                )
                processing.status = 'completed'
                processing.save()
                
                return JsonResponse({
                    'status': 'completed',
                    'redirect_url': reverse('remover:result', kwargs={'pk': processing.id})
                })
            else:
                raise BackgroundRemovalError("No processed image returned")
                
        except BackgroundRemovalError as e:
            processing.status = 'failed'
            processing.error_message = str(e)
            processing.save()
            
            return JsonResponse({
                'status': 'failed',
                'error': str(e)
            })
    
    except Exception as e:
        logger.error(f"Unexpected error in image processing: {str(e)}")
        return JsonResponse({
            'status': 'failed',
            'error': 'An unexpected error occurred'
        }, status=500)


class ResultView(View):
    """Display processing results with download options"""
    
    def get(self, request, pk):
        processing = get_object_or_404(ImageProcessing, pk=pk)
        
        # Check session permission
        if not request.session.get(f'processing_{processing.id}'):
            raise Http404("Processing request not found or expired.")
        
        # Check if processing is complete
        if processing.status != 'completed':
            return redirect('remover:process', pk=processing.id)
        
        # Check if processed image exists
        if not processing.processed_image:
            logger.error(f"Processed image missing for processing {processing.id}")
            messages.error(request, 'Processed image not found.')
            return redirect('remover:home')
        
        # Check if processed image file exists on disk
        try:
            if not processing.processed_image.file:
                logger.error(f"Processed image file missing on disk for processing {processing.id}")
                messages.error(request, 'Processed image file not found on server.')
                return redirect('remover:home')
        except Exception as e:
            logger.error(f"Error checking processed image file for processing {processing.id}: {str(e)}")
            messages.error(request, 'Error accessing processed image.')
            return redirect('remover:home')
        
        background_form = BackgroundOptionForm()
        
        return render(request, 'remover/result.html', {
            'processing': processing,
            'background_form': background_form,
            'title': 'Processing Complete'
        })


class DownloadView(View):
    """Handle image downloads with different background options"""
    
    def get(self, request, pk):
        processing = get_object_or_404(ImageProcessing, pk=pk)
        
        # Check session permission
        if not request.session.get(f'processing_{processing.id}'):
            raise Http404("Download not available.")
        
        # Check if processed image exists
        if not processing.processed_image:
            raise Http404("Processed image not found.")
        
        background_type = request.GET.get('bg', 'transparent')
        custom_color = request.GET.get('color', '')
        
        try:
            if background_type == 'transparent':
                # Download original processed image (transparent)
                response = HttpResponse(
                    processing.processed_image.read(),
                    content_type='image/png'
                )
                filename = f'removed_background_{processing.id}.png'
                
            elif background_type in ['white', 'black']:
                # Create version with solid background
                processor = BackgroundProcessor()
                bg_image = processor.add_solid_background(
                    processing.processed_image.path,
                    background_type
                )
                
                response = HttpResponse(
                    bg_image.read(),
                    content_type='image/jpeg'
                )
                filename = f'background_{background_type}_{processing.id}.jpg'
                
            elif background_type == 'custom' and custom_color:
                # Create version with custom background color
                processor = BackgroundProcessor()
                bg_image = processor.add_solid_background(
                    processing.processed_image.path,
                    custom_color
                )
                
                response = HttpResponse(
                    bg_image.read(),
                    content_type='image/jpeg'
                )
                color_safe = custom_color.replace('#', '')
                filename = f'background_{color_safe}_{processing.id}.jpg'
                
            else:
                raise Http404("Invalid background type or missing color.")
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            messages.error(request, 'Download failed. Please try again.')
            return redirect('remover:result', pk=processing.id)


def status_check(request, pk):
    """AJAX endpoint to check processing status"""
    try:
        processing = get_object_or_404(ImageProcessing, pk=pk)
        
        # Check session permission
        if not request.session.get(f'processing_{processing.id}'):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        return JsonResponse({
            'status': processing.status,
            'error_message': processing.error_message
        })
    
    except Exception as e:
        return JsonResponse({'error': 'Not found'}, status=404)
