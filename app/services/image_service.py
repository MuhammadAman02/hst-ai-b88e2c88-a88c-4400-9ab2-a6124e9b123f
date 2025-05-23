"""Image processing service for skin tone analysis and modification."""
import os
import uuid
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, Optional, List
import logging
from skimage import color
from colorthief import ColorThief

from app.core.config import settings
from app.core.error_handling import ApplicationError, ErrorCode
from app.models.color_model import SkinTone, ColorPalette

logger = logging.getLogger(__name__)

class ImageService:
    """Service for processing images and detecting skin tones."""
    
    @staticmethod
    def save_upload(file_data: bytes, filename: str) -> str:
        """
        Save an uploaded file to disk.
        
        Args:
            file_data: The binary file data
            filename: Original filename
            
        Returns:
            Path to the saved file
            
        Raises:
            ApplicationError: If file saving fails
        """
        try:
            # Generate a unique filename to prevent collisions
            ext = filename.split('.')[-1].lower()
            if ext not in settings.allowed_extensions:
                raise ApplicationError(
                    f"File type .{ext} not allowed. Allowed types: {', '.join(settings.allowed_extensions)}",
                    ErrorCode.VALIDATION_ERROR
                )
            
            unique_filename = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join(settings.upload_folder, unique_filename)
            
            # Save the file
            with open(file_path, "wb") as f:
                f.write(file_data)
                
            logger.info(f"Saved uploaded file to {file_path}")
            return file_path
            
        except ApplicationError:
            raise
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {str(e)}")
            raise ApplicationError(
                "Failed to save uploaded file",
                ErrorCode.FILE_ERROR,
                {"original_error": str(e)}
            )
    
    @staticmethod
    def detect_skin_tone(image_path: str) -> Tuple[SkinTone, Dict[str, Any]]:
        """
        Detect the skin tone from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (SkinTone enum, metadata dictionary)
            
        Raises:
            ApplicationError: If skin tone detection fails
        """
        try:
            # Load the image
            image = cv2.imread(image_path)
            if image is None:
                raise ApplicationError(
                    "Failed to load image",
                    ErrorCode.IMAGE_PROCESSING_ERROR
                )
            
            # Convert to RGB (OpenCV uses BGR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Use ColorThief to extract dominant colors
            color_thief = ColorThief(image_path)
            dominant_color = color_thief.get_color(quality=1)
            palette = color_thief.get_palette(color_count=5, quality=1)
            
            # Convert to HSV for better skin tone analysis
            image_hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create a mask for skin color
            skin_mask = cv2.inRange(image_hsv, lower_skin, upper_skin)
            
            # Apply the mask to the original image
            skin_only = cv2.bitwise_and(image_rgb, image_rgb, mask=skin_mask)
            
            # Calculate average color of skin pixels
            skin_pixels = skin_only[np.where(skin_mask > 0)]
            if len(skin_pixels) > 0:
                avg_skin_color = np.mean(skin_pixels, axis=0).astype(int)
            else:
                # Fallback to dominant color if no skin detected
                avg_skin_color = np.array(dominant_color)
            
            # Convert to Lab color space for better perceptual analysis
            avg_skin_lab = color.rgb2lab([[avg_skin_color / 255.0]])[0][0]
            
            # L* component in Lab color space represents lightness
            lightness = avg_skin_lab[0]
            
            # Determine skin tone category based on lightness
            if lightness > 85:
                skin_tone = SkinTone.VERY_LIGHT
            elif lightness > 75:
                skin_tone = SkinTone.LIGHT
            elif lightness > 65:
                skin_tone = SkinTone.MEDIUM_LIGHT
            elif lightness > 55:
                skin_tone = SkinTone.MEDIUM
            elif lightness > 45:
                skin_tone = SkinTone.MEDIUM_DARK
            elif lightness > 35:
                skin_tone = SkinTone.DARK
            else:
                skin_tone = SkinTone.VERY_DARK
            
            # Prepare metadata
            metadata = {
                "avg_skin_color": {
                    "rgb": avg_skin_color.tolist(),
                    "hex": f"#{avg_skin_color[0]:02x}{avg_skin_color[1]:02x}{avg_skin_color[2]:02x}",
                },
                "dominant_color": {
                    "rgb": dominant_color,
                    "hex": f"#{dominant_color[0]:02x}{dominant_color[1]:02x}{dominant_color[2]:02x}",
                },
                "palette": [
                    {
                        "rgb": color,
                        "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                    }
                    for color in palette
                ],
                "lightness": lightness,
            }
            
            return skin_tone, metadata
            
        except ApplicationError:
            raise
        except Exception as e:
            logger.error(f"Failed to detect skin tone: {str(e)}")
            raise ApplicationError(
                "Failed to detect skin tone",
                ErrorCode.IMAGE_PROCESSING_ERROR,
                {"original_error": str(e)}
            )
    
    @staticmethod
    def adjust_skin_tone(image_path: str, target_tone: SkinTone) -> str:
        """
        Adjust the skin tone in an image.
        
        Args:
            image_path: Path to the original image
            target_tone: Target skin tone to adjust to
            
        Returns:
            Path to the adjusted image
            
        Raises:
            ApplicationError: If skin tone adjustment fails
        """
        try:
            # Load the image
            image = cv2.imread(image_path)
            if image is None:
                raise ApplicationError(
                    "Failed to load image",
                    ErrorCode.IMAGE_PROCESSING_ERROR
                )
            
            # Convert to RGB (OpenCV uses BGR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to HSV for better skin tone analysis
            image_hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # Create a mask for skin color
            skin_mask = cv2.inRange(image_hsv, lower_skin, upper_skin)
            
            # Target skin tones (average values in HSV)
            target_hsv_values = {
                SkinTone.VERY_LIGHT: [0, 30, 240],
                SkinTone.LIGHT: [0, 40, 230],
                SkinTone.MEDIUM_LIGHT: [0, 50, 220],
                SkinTone.MEDIUM: [0, 60, 200],
                SkinTone.MEDIUM_DARK: [0, 70, 180],
                SkinTone.DARK: [0, 80, 160],
                SkinTone.VERY_DARK: [0, 90, 140],
            }
            
            # Get target HSV values
            target_hsv = np.array(target_hsv_values[target_tone], dtype=np.uint8)
            
            # Create a copy of the original image
            adjusted_image = image_rgb.copy()
            
            # Apply skin mask to find skin pixels
            skin_pixels = np.where(skin_mask > 0)
            
            # Get current skin HSV values
            skin_hsv = image_hsv[skin_pixels]
            
            # Calculate adjustment factors
            h_factor = target_hsv[0] / np.mean(skin_hsv[:, 0]) if np.mean(skin_hsv[:, 0]) > 0 else 1
            s_factor = target_hsv[1] / np.mean(skin_hsv[:, 1]) if np.mean(skin_hsv[:, 1]) > 0 else 1
            v_factor = target_hsv[2] / np.mean(skin_hsv[:, 2]) if np.mean(skin_hsv[:, 2]) > 0 else 1
            
            # Create adjusted HSV image
            adjusted_hsv = image_hsv.copy()
            
            # Adjust only skin pixels
            adjusted_hsv[skin_pixels] = np.clip([
                skin_hsv[:, 0] * h_factor,
                np.clip(skin_hsv[:, 1] * s_factor, 0, 255),
                np.clip(skin_hsv[:, 2] * v_factor, 0, 255)
            ], 0, 255).transpose()
            
            # Convert back to RGB
            adjusted_rgb = cv2.cvtColor(adjusted_hsv, cv2.COLOR_HSV2RGB)
            
            # Save the adjusted image
            ext = image_path.split('.')[-1].lower()
            adjusted_path = os.path.join(settings.upload_folder, f"adjusted_{uuid.uuid4()}.{ext}")
            
            # Convert to PIL Image and save
            adjusted_pil = Image.fromarray(adjusted_rgb)
            adjusted_pil.save(adjusted_path)
            
            return adjusted_path
            
        except ApplicationError:
            raise
        except Exception as e:
            logger.error(f"Failed to adjust skin tone: {str(e)}")
            raise ApplicationError(
                "Failed to adjust skin tone",
                ErrorCode.IMAGE_PROCESSING_ERROR,
                {"original_error": str(e)}
            )
    
    @staticmethod
    def get_image_url(file_path: str) -> str:
        """
        Convert a file path to a URL that can be accessed by the frontend.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            URL to access the image
        """
        # Extract just the filename from the path
        filename = os.path.basename(file_path)
        return f"/uploads/{filename}"