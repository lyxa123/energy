"""
Layout Management System
Handles screen dimensions, positioning, and responsive layout calculations
"""

import pygame
import math
from typing import Tuple, Dict, Any


class Dimensions:
    """Screen and component size management"""
    
    def __init__(self, screen_width: int = 1600, screen_height: int = 900, 
                 sidebar_width: int = 250):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.sidebar_width = sidebar_width
        self.main_area_width = screen_width - sidebar_width
        
        # 3D isometric settings
        self.cube_size = 64
        self.tile_width = self.cube_size
        self.tile_height = int(self.cube_size * math.sin(math.radians(30)))
        self.tile_depth = self.cube_size
        
        # UI element sizes
        self.button_size = 30
        self.button_padding = 10
        self.entity_font_size = 16
        
        # Menu dimensions
        self.menu_height = 40
        self.menu_title_size = 48
        self.menu_item_size = 36
        self.menu_button_width = 300
        self.menu_button_height = 60
        
        # Log panel dimensions
        self.log_panel_height = 150
        
        # Sidebar dimensions
        self.sidebar_item_height = 80
        self.sidebar_item_padding = 20
        self.sidebar_item_margin = 10
        self.sidebar_title_height = 50
        self.sidebar_shadow_width = 10
    
    def get_main_area_rect(self) -> pygame.Rect:
        """Get the main simulation area rectangle"""
        return pygame.Rect(0, 0, self.main_area_width, self.screen_height)
    
    def get_sidebar_rect(self) -> pygame.Rect:
        """Get the sidebar rectangle"""
        return pygame.Rect(self.main_area_width, 0, self.sidebar_width, self.screen_height)
    
    def get_log_panel_rect(self) -> pygame.Rect:
        """Get the log panel rectangle"""
        return pygame.Rect(0, self.screen_height - self.log_panel_height, 
                          self.screen_width, self.log_panel_height)
    
    def get_menu_rect(self) -> pygame.Rect:
        """Get the menu bar rectangle"""
        return pygame.Rect(0, 0, self.screen_width, self.menu_height)


class Positioning:
    """Element positioning utilities"""
    
    @staticmethod
    def center_horizontally(container_width: int, element_width: int) -> int:
        """Calculate x position to center element horizontally"""
        return (container_width - element_width) // 2
    
    @staticmethod
    def center_vertically(container_height: int, element_height: int) -> int:
        """Calculate y position to center element vertically"""
        return (container_height - element_height) // 2
    
    @staticmethod
    def center_in_rect(container: pygame.Rect, element_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate position to center element in container rectangle"""
        element_width, element_height = element_size
        x = container.x + Positioning.center_horizontally(container.width, element_width)
        y = container.y + Positioning.center_vertically(container.height, element_height)
        return x, y
    
    @staticmethod
    def grid_layout(container: pygame.Rect, item_size: Tuple[int, int], 
                   spacing: Tuple[int, int], start_offset: Tuple[int, int] = (0, 0)) -> list:
        """Generate grid positions for items within a container"""
        positions = []
        item_width, item_height = item_size
        spacing_x, spacing_y = spacing
        offset_x, offset_y = start_offset
        
        x = container.x + offset_x
        y = container.y + offset_y
        
        while y + item_height <= container.bottom:
            while x + item_width <= container.right:
                positions.append((x, y))
                x += item_width + spacing_x
            x = container.x + offset_x  # Reset x for next row
            y += item_height + spacing_y
        
        return positions
    
    @staticmethod
    def distribute_evenly(container_width: int, num_items: int, item_width: int) -> list:
        """Distribute items evenly across container width"""
        if num_items <= 1:
            return [Positioning.center_horizontally(container_width, item_width)]
        
        total_item_width = num_items * item_width
        available_space = container_width - total_item_width
        spacing = available_space // (num_items + 1)
        
        positions = []
        x = spacing
        for i in range(num_items):
            positions.append(x)
            x += item_width + spacing
        
        return positions


class LayoutManager:
    """Main layout management system"""
    
    def __init__(self, screen_width: int = 1600, screen_height: int = 900, 
                 sidebar_width: int = 250):
        self.dimensions = Dimensions(screen_width, screen_height, sidebar_width)
        self.positioning = Positioning()
        
        # Cache frequently used rectangles
        self._main_area_rect = None
        self._sidebar_rect = None
        self._log_panel_rect = None
        self._menu_rect = None
    
    @property
    def main_area_rect(self) -> pygame.Rect:
        """Get cached main area rectangle"""
        if self._main_area_rect is None:
            self._main_area_rect = self.dimensions.get_main_area_rect()
        return self._main_area_rect
    
    @property
    def sidebar_rect(self) -> pygame.Rect:
        """Get cached sidebar rectangle"""
        if self._sidebar_rect is None:
            self._sidebar_rect = self.dimensions.get_sidebar_rect()
        return self._sidebar_rect
    
    @property
    def log_panel_rect(self) -> pygame.Rect:
        """Get cached log panel rectangle"""
        if self._log_panel_rect is None:
            self._log_panel_rect = self.dimensions.get_log_panel_rect()
        return self._log_panel_rect
    
    @property
    def menu_rect(self) -> pygame.Rect:
        """Get cached menu rectangle"""
        if self._menu_rect is None:
            self._menu_rect = self.dimensions.get_menu_rect()
        return self._menu_rect
    
    def calculate_button_positions(self, num_buttons: int, button_size: int, 
                                 area_width: int, padding: int = 10) -> list:
        """Calculate positions for a row of buttons"""
        total_width = num_buttons * button_size + (num_buttons - 1) * padding
        start_x = area_width - total_width - padding
        
        positions = []
        x = start_x
        for i in range(num_buttons):
            positions.append((x, padding))
            x += button_size + padding
        
        return positions
    
    def calculate_menu_layout(self) -> Dict[str, Any]:
        """Calculate layout for main menu"""
        title_y = 100
        title_spacing = 100
        button_spacing = 20
        left_margin = 50
        
        return {
            'title_pos': (left_margin, title_y),
            'start_button': pygame.Rect(
                left_margin,
                title_y + title_spacing,
                self.dimensions.menu_button_width,
                self.dimensions.menu_button_height
            ),
            'config_button': pygame.Rect(
                left_margin,
                title_y + title_spacing + self.dimensions.menu_button_height + button_spacing,
                self.dimensions.menu_button_width,
                self.dimensions.menu_button_height
            ),
            'exit_button': pygame.Rect(
                left_margin,
                title_y + title_spacing + 2 * (self.dimensions.menu_button_height + button_spacing),
                self.dimensions.menu_button_width,
                self.dimensions.menu_button_height
            )
        }
    
    def calculate_sidebar_component_positions(self, num_components: int) -> list:
        """Calculate vertical positions for sidebar components"""
        positions = []
        y = self.dimensions.sidebar_title_height
        
        for i in range(num_components):
            positions.append(y)
            y += self.dimensions.sidebar_item_height + self.dimensions.sidebar_item_margin
        
        return positions
    
    def get_isometric_screen_center(self) -> Tuple[int, int]:
        """Get screen center for isometric projection"""
        return (self.dimensions.main_area_width // 2, self.dimensions.screen_height // 2)
    
    def resize(self, new_width: int, new_height: int) -> None:
        """Handle screen resize"""
        self.dimensions.screen_width = new_width
        self.dimensions.screen_height = new_height
        self.dimensions.main_area_width = new_width - self.dimensions.sidebar_width
        
        # Clear cached rectangles
        self._main_area_rect = None
        self._sidebar_rect = None
        self._log_panel_rect = None
        self._menu_rect = None


# Global layout manager instance
layout_manager = LayoutManager()


# Backward compatibility functions
def get_main_area_width() -> int:
    """Get main area width"""
    return layout_manager.dimensions.main_area_width

def get_screen_dimensions() -> Tuple[int, int]:
    """Get screen dimensions"""
    return layout_manager.dimensions.screen_width, layout_manager.dimensions.screen_height

def get_tile_dimensions() -> Tuple[int, int, int]:
    """Get tile dimensions for isometric rendering"""
    dims = layout_manager.dimensions
    return dims.tile_width, dims.tile_height, dims.tile_depth
