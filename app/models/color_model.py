"""Color models and recommendation logic."""
from typing import List, Dict, Tuple, Optional
import numpy as np
from enum import Enum

class SkinTone(Enum):
    """Skin tone categories."""
    VERY_LIGHT = "Very Light"
    LIGHT = "Light"
    MEDIUM_LIGHT = "Medium Light"
    MEDIUM = "Medium"
    MEDIUM_DARK = "Medium Dark"
    DARK = "Dark"
    VERY_DARK = "Very Dark"

class ColorPalette:
    """Color palette recommendations for different skin tones."""
    
    # Color recommendations based on skin tone
    # These are simplified recommendations and can be expanded
    RECOMMENDATIONS: Dict[SkinTone, Dict[str, List[Tuple[int, int, int]]]] = {
        SkinTone.VERY_LIGHT: {
            "clothing": [
                (0, 0, 0),      # Black
                (0, 0, 128),    # Navy
                (128, 0, 0),    # Maroon
                (0, 100, 0),    # Dark Green
                (128, 0, 128),  # Purple
            ],
            "makeup": [
                (255, 182, 193),  # Light Pink
                (255, 228, 225),  # Misty Rose
                (255, 192, 203),  # Pink
                (219, 112, 147),  # Pale Violet Red
            ]
        },
        SkinTone.LIGHT: {
            "clothing": [
                (0, 0, 0),      # Black
                (0, 0, 128),    # Navy
                (128, 0, 0),    # Maroon
                (0, 100, 0),    # Dark Green
                (128, 0, 128),  # Purple
                (255, 0, 0),    # Red
            ],
            "makeup": [
                (255, 182, 193),  # Light Pink
                (255, 228, 225),  # Misty Rose
                (255, 192, 203),  # Pink
                (219, 112, 147),  # Pale Violet Red
                (205, 92, 92),    # Indian Red
            ]
        },
        SkinTone.MEDIUM_LIGHT: {
            "clothing": [
                (0, 0, 0),      # Black
                (0, 0, 128),    # Navy
                (128, 0, 0),    # Maroon
                (0, 100, 0),    # Dark Green
                (255, 0, 0),    # Red
                (255, 165, 0),  # Orange
            ],
            "makeup": [
                (255, 192, 203),  # Pink
                (219, 112, 147),  # Pale Violet Red
                (205, 92, 92),    # Indian Red
                (233, 150, 122),  # Dark Salmon
            ]
        },
        SkinTone.MEDIUM: {
            "clothing": [
                (0, 0, 0),      # Black
                (0, 0, 128),    # Navy
                (255, 0, 0),    # Red
                (255, 165, 0),  # Orange
                (255, 215, 0),  # Gold
                (255, 255, 255),# White
            ],
            "makeup": [
                (219, 112, 147),  # Pale Violet Red
                (205, 92, 92),    # Indian Red
                (233, 150, 122),  # Dark Salmon
                (250, 128, 114),  # Salmon
            ]
        },
        SkinTone.MEDIUM_DARK: {
            "clothing": [
                (0, 0, 0),      # Black
                (255, 0, 0),    # Red
                (255, 165, 0),  # Orange
                (255, 215, 0),  # Gold
                (255, 255, 255),# White
                (0, 255, 255),  # Cyan
            ],
            "makeup": [
                (205, 92, 92),    # Indian Red
                (233, 150, 122),  # Dark Salmon
                (250, 128, 114),  # Salmon
                (255, 99, 71),    # Tomato
            ]
        },
        SkinTone.DARK: {
            "clothing": [
                (255, 0, 0),    # Red
                (255, 165, 0),  # Orange
                (255, 215, 0),  # Gold
                (255, 255, 255),# White
                (0, 255, 255),  # Cyan
                (255, 192, 203),# Pink
            ],
            "makeup": [
                (233, 150, 122),  # Dark Salmon
                (250, 128, 114),  # Salmon
                (255, 99, 71),    # Tomato
                (255, 69, 0),     # Orange Red
            ]
        },
        SkinTone.VERY_DARK: {
            "clothing": [
                (255, 0, 0),    # Red
                (255, 165, 0),  # Orange
                (255, 215, 0),  # Gold
                (255, 255, 255),# White
                (0, 255, 255),  # Cyan
                (255, 192, 203),# Pink
                (255, 255, 0),  # Yellow
            ],
            "makeup": [
                (250, 128, 114),  # Salmon
                (255, 99, 71),    # Tomato
                (255, 69, 0),     # Orange Red
                (255, 140, 0),    # Dark Orange
            ]
        }
    }
    
    @staticmethod
    def get_color_name(rgb: Tuple[int, int, int]) -> str:
        """Get a human-readable name for an RGB color."""
        # This is a simplified version - a real implementation would use a color name database
        color_names = {
            (0, 0, 0): "Black",
            (255, 255, 255): "White",
            (255, 0, 0): "Red",
            (0, 255, 0): "Green",
            (0, 0, 255): "Blue",
            (255, 255, 0): "Yellow",
            (255, 0, 255): "Magenta",
            (0, 255, 255): "Cyan",
            (128, 0, 0): "Maroon",
            (0, 128, 0): "Dark Green",
            (0, 0, 128): "Navy",
            (128, 128, 0): "Olive",
            (128, 0, 128): "Purple",
            (0, 128, 128): "Teal",
            (255, 165, 0): "Orange",
            (255, 215, 0): "Gold",
            (255, 192, 203): "Pink",
            (219, 112, 147): "Pale Violet Red",
            (205, 92, 92): "Indian Red",
            (233, 150, 122): "Dark Salmon",
            (250, 128, 114): "Salmon",
            (255, 99, 71): "Tomato",
            (255, 69, 0): "Orange Red",
            (255, 140, 0): "Dark Orange",
            (255, 182, 193): "Light Pink",
            (255, 228, 225): "Misty Rose",
        }
        
        # Find the closest color by Euclidean distance
        min_distance = float('inf')
        closest_color = "Unknown"
        
        for color_rgb, name in color_names.items():
            distance = np.sqrt(sum((np.array(rgb) - np.array(color_rgb))**2))
            if distance < min_distance:
                min_distance = distance
                closest_color = name
                
        return closest_color
    
    @staticmethod
    def get_recommendations(skin_tone: SkinTone) -> Dict[str, List[Dict[str, any]]]:
        """Get color recommendations for a given skin tone."""
        recommendations = ColorPalette.RECOMMENDATIONS.get(skin_tone, ColorPalette.RECOMMENDATIONS[SkinTone.MEDIUM])
        
        result = {}
        for category, colors in recommendations.items():
            result[category] = [
                {
                    "rgb": color,
                    "hex": f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                    "name": ColorPalette.get_color_name(color)
                }
                for color in colors
            ]
            
        return result