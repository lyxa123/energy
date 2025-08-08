"""
3D Rendering Engine for Energy Simulation
Provides isometric rendering, trapezoid shapes, and 3D visual effects
"""

import pygame
import math
from typing import Tuple, List, Optional

# Import from constants for now, will be migrated to color_manager later
from constants import TILE_WIDTH, TILE_HEIGHT, CUBE_SIZE


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


class IsometricProjection:
    """Handles conversion between grid coordinates and isometric screen coordinates"""
    
    @staticmethod
    def to_isometric(grid_x: int, grid_y: int) -> Tuple[int, int]:
        """Convert grid coordinates to isometric screen coordinates"""
        iso_x = (grid_x - grid_y) * TILE_WIDTH
        iso_y = (grid_x + grid_y) * TILE_HEIGHT
        return iso_x, iso_y
    
    @staticmethod
    def from_isometric(iso_x: int, iso_y: int) -> Tuple[int, int]:
        """Convert isometric screen coordinates back to grid coordinates"""
        grid_x = round((iso_x / TILE_WIDTH + iso_y / TILE_HEIGHT) / 2)
        grid_y = round((iso_y / TILE_HEIGHT - iso_x / TILE_WIDTH) / 2)
        return grid_x, grid_y


class TrapezoidRenderer:
    """Handles rendering of 3D trapezoid shapes for isometric entities"""
    
    @staticmethod
    def create_trapezoid_points(center_x: int, center_y: int, width: int, height: int) -> List[Tuple[int, int]]:
        """Create 3D trapezoid points based on user's specification.
        Creates a 3D box effect with nearside (bottom) and farside (top) where farside is 80% width."""
        
        # Tommy's algorithm implementation
        nearside_box_length = width
        half_nearside_length = nearside_box_length / 2
        box_height = half_nearside_length / 3
        
        # Use the calculated box_height instead of the passed height parameter
        actual_height = box_height
        
        # Nearside (bottom edge - closer to user)
        nearside_middle_point_x = center_x
        nearside_middle_point_y = center_y + (actual_height // 2)  # Bottom of the shape
        
        nearside_left_x = nearside_middle_point_x - half_nearside_length
        nearside_left_y = nearside_middle_point_y
        nearside_right_x = nearside_middle_point_x + half_nearside_length
        nearside_right_y = nearside_middle_point_y
        
        # Farside (top edge - further from user)
        farside_middle_point_y = center_y - (actual_height // 2)  # Top of the shape
        farside_left_x = nearside_middle_point_x - (half_nearside_length * 0.8)
        farside_right_x = nearside_middle_point_x + (half_nearside_length * 0.8)
        farside_left_y = farside_middle_point_y
        farside_right_y = farside_middle_point_y
        
        # Create trapezoid points (clockwise from top-left)
        points = [
            (farside_left_x, farside_left_y),      # Top left (farside)
            (farside_right_x, farside_right_y),    # Top right (farside)
            (nearside_right_x, nearside_right_y),  # Bottom right (nearside)
            (nearside_left_x, nearside_left_y)     # Bottom left (nearside)
        ]
        
        return points
    
    @staticmethod
    def render_3d_trapezoid(surface: pygame.Surface, center_x: int, center_y: int, 
                           base_color: Tuple[int, int, int], width: int = TILE_WIDTH, 
                           height: int = TILE_HEIGHT, depth_offset: int = 10) -> None:
        """Render a 3D trapezoid with depth effect"""
        
        # Create main trapezoid face
        main_points = TrapezoidRenderer.create_trapezoid_points(center_x, center_y, width, height)
        
        # Calculate colors for 3D effect
        top_color = base_color  # Main face color
        side_color = ColorUtils.darken_color(base_color, 0.8)  # Darker side face
        edge_color = ColorUtils.darken_color(base_color, 0.5)  # Darkest edge color
        
        # Draw the main trapezoid face (front face)
        pygame.draw.polygon(surface, top_color, main_points)
        
        # Create 3D depth effect by drawing side faces
        # Right side face (connecting right edges) - only offset upward
        right_side_points = [
            main_points[1],  # Top right of front face
            (main_points[1][0], main_points[1][1] - depth_offset),  # Top right back (only up)
            (main_points[2][0], main_points[2][1] - depth_offset),  # Bottom right back (only up)
            main_points[2]   # Bottom right of front face
        ]
        pygame.draw.polygon(surface, side_color, right_side_points)
        
        # Top side face (connecting top edges) - only offset upward
        top_side_points = [
            main_points[0],  # Top left of front face
            main_points[1],  # Top right of front face
            (main_points[1][0], main_points[1][1] - depth_offset),  # Top right back (only up)
            (main_points[0][0], main_points[0][1] - depth_offset)   # Top left back (only up)
        ]
        pygame.draw.polygon(surface, side_color, top_side_points)
        
        # Draw main face border for definition
        pygame.draw.polygon(surface, edge_color, main_points, 2)
        
        # Draw 3D edges
        pygame.draw.lines(surface, edge_color, False, right_side_points, 2)
        pygame.draw.lines(surface, edge_color, False, top_side_points, 2)
        
        # Add inner highlight for depth
        inner_width = int(width * 0.8)
        inner_height = int(height * 0.8)
        inner_points = TrapezoidRenderer.create_trapezoid_points(center_x, center_y, inner_width, inner_height)
        highlight_color = ColorUtils.lighten_color(base_color, 1.15)
        pygame.draw.polygon(surface, highlight_color, inner_points, 1)


class ShadowRenderer:
    """Handles rendering of drop shadows for 3D entities"""
    
    @staticmethod
    def render_trapezoid_shadow(surface: pygame.Surface, center_x: int, center_y: int, 
                               width: int = TILE_WIDTH, height: int = TILE_HEIGHT,
                               shadow_offset: Tuple[int, int] = (2, 2),
                               shadow_alpha: int = 40) -> None:
        """Render a drop shadow for a trapezoid shape"""
        
        # Create shadow points
        shadow_points = TrapezoidRenderer.create_trapezoid_points(center_x, center_y, width, height)
        
        # Create a surface for the shadow with transparency
        shadow_surface = pygame.Surface((width * 2, height * 2), pygame.SRCALPHA)
        pygame.draw.polygon(shadow_surface, (0, 0, 0, shadow_alpha), 
                          [(p[0] - center_x + width, p[1] - center_y + height) for p in shadow_points])
        
        # Blit shadow surface at offset position
        surface.blit(shadow_surface, (center_x - width + shadow_offset[0], 
                                    center_y - height + shadow_offset[1]))


class Renderer3D:
    """Main 3D rendering engine for entities and UI elements"""
    
    def __init__(self, main_area_width: int, screen_height: int):
        self.main_area_width = main_area_width
        self.screen_height = screen_height
        self.projection = IsometricProjection()
        self.trapezoid_renderer = TrapezoidRenderer()
        self.shadow_renderer = ShadowRenderer()
    
    def render_entity(self, surface: pygame.Surface, grid_x: int, grid_y: int, 
                     base_color: Tuple[int, int, int], label_text: str,
                     entity_size: int = TILE_WIDTH) -> pygame.Rect:
        """Render a complete 3D entity with shadow and label at grid position"""
        
        # Calculate screen position
        iso_x, iso_y = self.projection.to_isometric(grid_x, grid_y)
        screen_x = iso_x + self.main_area_width // 2
        screen_y = iso_y + self.screen_height // 2
        
        # Render shadow first (behind entity)
        self.shadow_renderer.render_trapezoid_shadow(surface, screen_x, screen_y)
        
        # Render main 3D trapezoid
        self.trapezoid_renderer.render_3d_trapezoid(surface, screen_x, screen_y, base_color, entity_size)
        
        # Add label
        if label_text:
            font = pygame.font.SysFont("Arial", 14, bold=True)
            text_surface = font.render(label_text, True, (255, 255, 255))  # White text
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            surface.blit(text_surface, text_rect)
        
        # Return bounding rectangle for collision detection
        return pygame.Rect(screen_x - entity_size, screen_y - entity_size, 
                          entity_size * 2, entity_size * 2)
    
    def render_entity_surface(self, base_color: Tuple[int, int, int], label_text: str,
                             entity_size: int = TILE_WIDTH) -> pygame.Surface:
        """Render an entity to its own surface for Entity.redraw() compatibility"""
        
        # Create surface for the entity
        surface = pygame.Surface((entity_size * 2, entity_size * 2), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))  # Transparent background
        
        # Calculate center points for rendering
        center_x = surface.get_width() // 2
        center_y = surface.get_height() // 2
        
        # Render 3D trapezoid
        self.trapezoid_renderer.render_3d_trapezoid(surface, center_x, center_y, base_color, entity_size)
        
        # Add label
        if label_text:
            try:
                font = pygame.font.SysFont("Arial", 14, bold=True)
                text_surface = font.render(label_text, True, (255, 255, 255))  # White text
                text_rect = text_surface.get_rect(center=(center_x, center_y))
                surface.blit(text_surface, text_rect)
            except pygame.error:
                # Font not available - skip text rendering in tests
                pass
        
        return surface
    
    def get_screen_position(self, grid_x: int, grid_y: int, entity_size: int = TILE_WIDTH) -> Tuple[int, int]:
        """Get screen position for an entity at grid coordinates"""
        iso_x, iso_y = self.projection.to_isometric(grid_x, grid_y)
        screen_x = iso_x + self.main_area_width // 2 - entity_size
        screen_y = iso_y + self.screen_height // 2 - entity_size
        return screen_x, screen_y
