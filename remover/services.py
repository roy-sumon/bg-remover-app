import logging
import os
from typing import Optional
from django.core.files.base import ContentFile
from PIL import Image
import io
import numpy as np

# Try to import rembg for advanced background removal
try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

# Try to import cv2 for basic image processing
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

logger = logging.getLogger(__name__)


class BackgroundRemovalError(Exception):
    """Custom exception for background removal errors"""
    pass


class LocalBackgroundRemover:
    """Local background removal service using Python libraries"""
    
    def __init__(self):
        self.method = self._determine_best_method()
        logger.info(f"Initialized background remover with method: {self.method}")
    
    def _determine_best_method(self) -> str:
        """Determine the best available method for background removal"""
        if REMBG_AVAILABLE:
            return "rembg"
        elif CV2_AVAILABLE:
            return "opencv"
        else:
            return "pillow"
    
    def remove_background(self, image_path: str) -> Optional[ContentFile]:
        """
        Remove background from image using local Python libraries
        
        Args:
            image_path: Path to the image file
            
        Returns:
            ContentFile with processed image or None if failed
            
        Raises:
            BackgroundRemovalError: If processing fails
        """
        try:
            # Optimize image if too large
            optimized_path = BackgroundProcessor.optimize_image_for_processing(image_path)
            
            if self.method == "rembg":
                return self._remove_with_rembg(optimized_path)
            elif self.method == "opencv":
                return self._remove_with_opencv(optimized_path)
            else:
                return self._remove_with_pillow(optimized_path)
                
        except FileNotFoundError:
            raise BackgroundRemovalError("Image file not found")
        except Exception as e:
            logger.error(f"Unexpected error in background removal: {str(e)}")
            raise BackgroundRemovalError(f"Processing error: {str(e)}")
        finally:
            # Clean up optimized file if it was created
            if 'optimized_path' in locals() and optimized_path != image_path:
                try:
                    os.remove(optimized_path)
                except:
                    pass
    
    def _remove_with_rembg(self, image_path: str) -> ContentFile:
        """Remove background using rembg library (AI-based)"""
        logger.info("Processing image with rembg (AI-based method)")
        
        try:
            # Read the input image
            with open(image_path, 'rb') as input_file:
                input_data = input_file.read()
            
            # Create a new session for better performance
            session = new_session('u2net')
            
            # Remove background
            output_data = remove(input_data, session=session)
            
            # Create ContentFile
            processed_image = ContentFile(output_data)
            processed_image.name = 'processed_image.png'
            
            logger.info("Background removal with rembg completed successfully")
            return processed_image
            
        except Exception as e:
            logger.error(f"rembg processing failed: {str(e)}")
            # Fallback to OpenCV method
            if CV2_AVAILABLE:
                return self._remove_with_opencv(image_path)
            else:
                return self._remove_with_pillow(image_path)
    
    def _remove_with_opencv(self, image_path: str) -> ContentFile:
        """Remove background using OpenCV (edge detection + masking)"""
        logger.info("Processing image with OpenCV (edge detection method)")
        
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise BackgroundRemovalError("Could not read image file")
            
            # Convert to different color spaces for better processing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Create mask from largest contour (assumed to be the main subject)
            mask = np.zeros(gray.shape, np.uint8)
            if contours:
                # Find the largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                cv2.fillPoly(mask, [largest_contour], 255)
                
                # Smooth the mask
                mask = cv2.GaussianBlur(mask, (5, 5), 0)
            
            # Convert original image to RGBA
            img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
            
            # Apply mask to alpha channel
            img_rgba[:, :, 3] = mask
            
            # Convert to PIL Image
            pil_image = Image.fromarray(img_rgba, 'RGBA')
            
            # Save to bytes
            output = io.BytesIO()
            pil_image.save(output, format='PNG')
            output.seek(0)
            
            # Create ContentFile
            processed_image = ContentFile(output.getvalue())
            processed_image.name = 'processed_image.png'
            
            logger.info("Background removal with OpenCV completed successfully")
            return processed_image
            
        except Exception as e:
            logger.error(f"OpenCV processing failed: {str(e)}")
            # Fallback to Pillow method
            return self._remove_with_pillow(image_path)
    
    def _remove_with_pillow(self, image_path: str) -> ContentFile:
        """Remove background using PIL/Pillow (simple color-based method)"""
        logger.info("Processing image with Pillow (color-based method)")
        
        try:
            # Open image with PIL
            with Image.open(image_path) as img:
                # Convert to RGBA if not already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Get image data
                data = np.array(img)
                
                # Simple background removal based on corner colors
                # Assume corners contain background color
                h, w = data.shape[:2]
                
                # Sample corner colors
                corner_colors = [
                    data[0, 0][:3],      # Top-left
                    data[0, w-1][:3],    # Top-right
                    data[h-1, 0][:3],    # Bottom-left
                    data[h-1, w-1][:3]   # Bottom-right
                ]
                
                # Find the most common corner color (likely background)
                from collections import Counter
                corner_tuples = [tuple(color) for color in corner_colors]
                most_common_bg = Counter(corner_tuples).most_common(1)[0][0]
                
                # Create mask for pixels similar to background color
                bg_color = np.array(most_common_bg)
                
                # Calculate color difference
                color_diff = np.sqrt(np.sum((data[:, :, :3] - bg_color) ** 2, axis=2))
                
                # Set threshold for background detection
                threshold = 50  # Adjust this value for sensitivity
                
                # Create alpha mask
                alpha_mask = (color_diff > threshold).astype(np.uint8) * 255
                
                # Apply some morphological operations to clean up the mask
                try:
                    if CV2_AVAILABLE:
                        # Use OpenCV for better morphological operations
                        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                        alpha_mask = cv2.morphologyEx(alpha_mask, cv2.MORPH_CLOSE, kernel)
                        alpha_mask = cv2.morphologyEx(alpha_mask, cv2.MORPH_OPEN, kernel)
                        # Apply Gaussian blur to smooth edges
                        alpha_mask = cv2.GaussianBlur(alpha_mask, (3, 3), 0)
                except:
                    pass
                
                # Apply alpha mask
                data[:, :, 3] = alpha_mask
                
                # Convert back to PIL Image
                result_img = Image.fromarray(data, 'RGBA')
                
                # Save to bytes
                output = io.BytesIO()
                result_img.save(output, format='PNG')
                output.seek(0)
                
                # Create ContentFile
                processed_image = ContentFile(output.getvalue())
                processed_image.name = 'processed_image.png'
                
                logger.info("Background removal with Pillow completed successfully")
                return processed_image
                
        except Exception as e:
            logger.error(f"Pillow processing failed: {str(e)}")
            raise BackgroundRemovalError(f"All background removal methods failed: {str(e)}")


def get_ai_service():
    """
    Factory function to get the local background removal service
    No API key required - uses local Python libraries
    """
    return LocalBackgroundRemover()


class BackgroundProcessor:
    """Utility class for processing images with different background options"""
    
    @staticmethod
    def add_solid_background(image_path: str, background_color: str = 'white') -> ContentFile:
        """
        Add a solid background to a transparent image
        
        Args:
            image_path: Path to the transparent image
            background_color: 'white', 'black', or hex color (e.g., '#ff0000')
            
        Returns:
            ContentFile with solid background image
        """
        try:
            with Image.open(image_path) as img:
                # Ensure image has transparency
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Parse background color
                if background_color == 'white':
                    bg_color = (255, 255, 255, 255)
                elif background_color == 'black':
                    bg_color = (0, 0, 0, 255)
                elif background_color.startswith('#'):
                    # Parse hex color
                    hex_color = background_color.lstrip('#')
                    if len(hex_color) == 6:
                        r = int(hex_color[0:2], 16)
                        g = int(hex_color[2:4], 16)
                        b = int(hex_color[4:6], 16)
                        bg_color = (r, g, b, 255)
                    else:
                        raise ValueError(f"Invalid hex color: {background_color}")
                else:
                    # Default to white
                    bg_color = (255, 255, 255, 255)
                
                # Create background
                background = Image.new('RGBA', img.size, bg_color)
                
                # Composite the image on the background
                combined = Image.alpha_composite(background, img)
                
                # Convert to RGB for JPEG output
                final_img = combined.convert('RGB')
                
                # Save to bytes
                output = io.BytesIO()
                format_type = 'JPEG'
                final_img.save(output, format=format_type, quality=95, optimize=True)
                output.seek(0)
                
                # Create ContentFile
                processed_image = ContentFile(output.getvalue())
                color_name = background_color.replace('#', 'hex_')
                processed_image.name = f'background_{color_name}.jpg'
                
                return processed_image
                
        except Exception as e:
            logger.error(f"Error adding solid background: {str(e)}")
            raise BackgroundRemovalError(f"Background processing error: {str(e)}")
    
    @staticmethod
    def optimize_image_for_processing(image_path: str, max_size: tuple = (2000, 2000)) -> str:
        """
        Optimize image for processing by resizing if too large
        
        Args:
            image_path: Path to the original image
            max_size: Maximum width/height tuple
            
        Returns:
            Path to optimized image (same path if no optimization needed)
        """
        try:
            with Image.open(image_path) as img:
                # Check if image needs resizing
                if img.width > max_size[0] or img.height > max_size[1]:
                    logger.info(f"Resizing large image from {img.width}x{img.height}")
                    
                    # Calculate new size maintaining aspect ratio
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save optimized image
                    optimized_path = image_path.replace('.', '_optimized.')
                    img.save(optimized_path, optimize=True, quality=95)
                    
                    logger.info(f"Image resized to {img.width}x{img.height}")
                    return optimized_path
                
                return image_path
                
        except Exception as e:
            logger.error(f"Error optimizing image: {str(e)}")
            # Return original path if optimization fails
            return image_path

