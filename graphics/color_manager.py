"""
Color Management System
Centralized color definitions, themes, and color manipulation utilities
"""

from typing import Tuple, Dict, Any
import pygame


class ColorUtils:
    """Utility functions for color manipulation"""
    
    @staticmethod
    def darken_color(color: Tuple[int, int, int], factor: float = 0.7) -> Tuple[int, int, int]:
        """Darken a color by a given factor"""
        return tuple(int(c * factor) for c in color)
    
    @staticmethod
    def lighten_color(color: Tuple[int, int, int], factor: float = 1.3) -> Tuple[int, int, int]:
        """Lighten a color by a given factor"""
        return tuple(min(255, int(c * factor)) for c in color)
    
    @staticmethod
    def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    factor: float = 0.5) -> Tuple[int, int, int]:
        """Blend two colors together with given factor (0.0 = color1, 1.0 = color2)"""
        factor = max(0.0, min(1.0, factor))  # Clamp factor between 0 and 1
        return tuple(int(c1 * (1 - factor) + c2 * factor) for c1, c2 in zip(color1, color2))
    
    @staticmethod
    def with_alpha(color: Tuple[int, int, int], alpha: int) -> Tuple[int, int, int, int]:
        """Add alpha channel to RGB color"""
        return (*color, alpha)


class Theme:
    """Color theme definition"""
    
    def __init__(self, name: str, colors: Dict[str, Tuple[int, int, int]]):
        self.name = name
        self.colors = colors
    
    def get_color(self, key: str) -> Tuple[int, int, int]:
        """Get color by key, with fallback to default colors"""
        return self.colors.get(key, DEFAULT_THEME.colors.get(key, (255, 255, 255)))


# Base color definitions
BASE_COLORS = {
    # Primary colors
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (200, 0, 0),
    'green': (0, 200, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'grey': (200, 200, 200),
    
    # Status colors for electrical components
    'status_normal': (0, 200, 0),      # Green - Normal operation
    'status_warning': (255, 255, 0),   # Yellow - Warning conditions
    'status_critical': (200, 0, 0),    # Red - Critical conditions
    'status_inactive': (0, 0, 255),    # Blue - Inactive/unconnected
    
    # UI Background colors
    'panel_bg': (30, 30, 30),
    'menu_bg': (50, 50, 50),
    'config_bg': (93, 194, 237),
    'help_bg': (40, 40, 40),
    
    # UI Element colors
    'menu_text': (220, 220, 220),
    'log_text': (220, 220, 220),
    'button_normal': (100, 100, 100),
    'button_hover': (150, 150, 150),
    'button_text': (255, 255, 255),
    
    # Configuration colors
    'config_item_bg': (60, 60, 60),
    'config_item_hover': (80, 80, 80),
    'config_highlight': (0, 200, 0),
    'component_bg': (40, 40, 40),
    'component_hover': (55, 55, 55),
    'value_color': (220, 220, 220),
    'unit_color': (160, 160, 160),
    
    # Sidebar colors
    'sidebar_bg': (45, 45, 45),
    'sidebar_item_bg': (60, 60, 60),
    'sidebar_item_hover': (75, 75, 75),
    'sidebar_text': (220, 220, 220),
    'sidebar_shadow': (0, 0, 0),
    
    # Connection colors
    'connection_normal': (200, 200, 200),  # Grey for normal connections
    'connection_voltage_high': (0, 255, 0),    # Green for good voltage
    'connection_voltage_medium': (255, 255, 0), # Yellow for medium voltage
    'connection_voltage_low': (255, 0, 0),      # Red for low voltage
}

# Default theme
DEFAULT_THEME = Theme("Default", BASE_COLORS)

# Alternative themes for future expansion
DARK_THEME = Theme("Dark", {
    **BASE_COLORS,
    'panel_bg': (20, 20, 20),
    'menu_bg': (30, 30, 30),
    'sidebar_bg': (25, 25, 25),
})

HIGH_CONTRAST_THEME = Theme("High Contrast", {
    **BASE_COLORS,
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'status_normal': (0, 255, 0),      # Brighter green
    'status_critical': (255, 0, 0),    # Brighter red
    'status_warning': (255, 255, 0),   # Brighter yellow
})


class ColorManager:
    """Central color management system"""
    
    def __init__(self, theme: Theme = DEFAULT_THEME):
        self.current_theme = theme
        self.themes = {
            'default': DEFAULT_THEME,
            'dark': DARK_THEME,
            'high_contrast': HIGH_CONTRAST_THEME
        }
    
    def get_color(self, key: str) -> Tuple[int, int, int]:
        """Get color from current theme"""
        return self.current_theme.get_color(key)
    
    def set_theme(self, theme_name: str) -> bool:
        """Set active theme by name"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            return True
        return False
    
    def add_theme(self, theme: Theme) -> None:
        """Add a new theme"""
        self.themes[theme.name.lower()] = theme
    
    def get_status_color(self, voltage_pu: float, loading_percent: float = 0.0) -> Tuple[int, int, int]:
        """Get appropriate status color based on electrical conditions"""
        # Direct threshold-based color selection
        if loading_percent > 0.9 or voltage_pu < 0.95:
            return self.get_color('status_critical')  # Red
        elif loading_percent > 0.7 or voltage_pu < 0.98:
            return self.get_color('status_warning')   # Yellow
        else:
            return self.get_color('status_normal')    # Green
    
    def get_connection_color(self, voltage_pu: float) -> Tuple[int, int, int]:
        """Get connection line color based on voltage level"""
        if voltage_pu >= 0.98:
            return self.get_color('connection_voltage_high')      # Green
        elif voltage_pu >= 0.95:
            # Interpolation between yellow and green
            factor = (voltage_pu - 0.95) / 0.03  # Safe interpolation
            factor = max(0.0, min(1.0, factor))  # Clamp between 0 and 1
            yellow = self.get_color('connection_voltage_medium')
            green = self.get_color('connection_voltage_high')
            return ColorUtils.blend_colors(yellow, green, factor)
        else:
            # Interpolation between red and yellow
            factor = max(0.0, min(1.0, voltage_pu / 0.95))  # Safe interpolation
            red = self.get_color('connection_voltage_low')
            yellow = self.get_color('connection_voltage_medium')
            return ColorUtils.blend_colors(red, yellow, factor)
    
    # Convenience methods for common colors
    @property
    def white(self) -> Tuple[int, int, int]:
        return self.get_color('white')
    
    @property
    def black(self) -> Tuple[int, int, int]:
        return self.get_color('black')
    
    @property
    def green(self) -> Tuple[int, int, int]:
        return self.get_color('status_normal')
    
    @property 
    def red(self) -> Tuple[int, int, int]:
        return self.get_color('status_critical')
    
    @property
    def yellow(self) -> Tuple[int, int, int]:
        return self.get_color('status_warning')
    
    @property
    def blue(self) -> Tuple[int, int, int]:
        return self.get_color('status_inactive')
    
    @property
    def grey(self) -> Tuple[int, int, int]:
        return self.get_color('grey')


# Global color manager instance (can be configured by main application)
color_manager = ColorManager()


# Backward compatibility functions for existing code
def get_color(key: str) -> Tuple[int, int, int]:
    """Get color from global color manager"""
    return color_manager.get_color(key)


# Legacy color constants for backward compatibility
WHITE = color_manager.white
BLACK = color_manager.black
GREEN = color_manager.green
RED = color_manager.red
BLUE = color_manager.blue
YELLOW = color_manager.yellow
GREY = color_manager.grey
