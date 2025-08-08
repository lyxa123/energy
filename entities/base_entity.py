"""
Base Entity class for all electrical simulation components

This module contains the base Entity class that provides common functionality
for all electrical entities in the simulation including:
- 3D isometric rendering using trapezoid shapes
- Grid-based positioning 
- Status color management
- Basic electrical properties
"""

import pygame
from constants import (
    TILE_WIDTH, TILE_HEIGHT, MAIN_AREA_WIDTH, SCREEN_HEIGHT, WHITE,
    darken_color, lighten_color, to_isometric, create_trapezoid_points
)

class Entity(pygame.sprite.Sprite):
    """
    Base class for all electrical entities in the simulation.
    
    Provides common functionality for:
    - Grid-based positioning
    - 3D trapezoid rendering 
    - Status color management
    - Basic electrical properties
    """
    
    def __init__(self, x, y, size, color, label_text, bus_name=None, entity_type="unknown"):
        """
        Initialize a new Entity.
        
        Args:
            x (int): Grid X coordinate
            y (int): Grid Y coordinate  
            size (int): Size of the entity (used for rendering)
            color (tuple): RGB color tuple for entity base color
            label_text (str): Text label to display on entity
            bus_name (str, optional): Name of the electrical bus. Defaults to None.
            entity_type (str, optional): Type identifier. Defaults to "unknown".
        """
        super().__init__()
        
        # Grid position
        self.grid_x = x
        self.grid_y = y
        
        # Visual properties
        self.base_color = color
        self.label_text = label_text
        
        # Electrical properties
        self.bus_name = bus_name
        self.entity_type = entity_type
        self.is_connected = False
        self.voltage_pu = 1.0
        
        # Simulation properties
        self.total_p_demand = 0
        self.total_q_demand = 0
        self.p_demand_rate = 0
        self.power_factor = 1.0
        
        # UI interaction properties
        self.dragging = False
        self.connected_to = None
        
        # Create surface for rendering - match selection highlight size
        self.image = pygame.Surface((TILE_WIDTH * 2, TILE_WIDTH * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.redraw()

    def redraw(self):
        """
        Redraw the entity's visual representation.
        
        Creates a 3D trapezoid shape with:
        - Main face in base color
        - Darker side faces for 3D effect
        - Inner highlight for depth
        - Text label overlay
        """
        self.image.fill((0, 0, 0, 0))  # Transparent background
        
        # Calculate center points for 3D trapezoid box
        center_x = self.image.get_width() // 2
        center_y = self.image.get_height() // 2
        
        # Create main trapezoid face using algorithm
        main_points = create_trapezoid_points(center_x, center_y, TILE_WIDTH, TILE_HEIGHT)
        
        # Calculate colors for 3D effect
        top_color = self.base_color  # Main face color
        side_color = darken_color(self.base_color, 0.8)  # Darker side face
        edge_color = darken_color(self.base_color, 0.5)  # Darkest edge color
        
        # Draw the main trapezoid face (front face)
        pygame.draw.polygon(self.image, top_color, main_points)
        
        # Create 3D depth effect by drawing side faces
        depth_offset = 10  # Pixels of 3D depth
        
        # Right side face (connecting right edges) - only offset upward
        right_side_points = [
            main_points[1],  # Top right of front face
            (main_points[1][0], main_points[1][1] - depth_offset),  # Top right back (only up)
            (main_points[2][0], main_points[2][1] - depth_offset),  # Bottom right back (only up)
            main_points[2]   # Bottom right of front face
        ]
        pygame.draw.polygon(self.image, side_color, right_side_points)
        
        # Top side face (connecting top edges) - only offset upward
        top_side_points = [
            main_points[0],  # Top left of front face
            main_points[1],  # Top right of front face
            (main_points[1][0], main_points[1][1] - depth_offset),  # Top right back (only up)
            (main_points[0][0], main_points[0][1] - depth_offset)   # Top left back (only up)
        ]
        pygame.draw.polygon(self.image, side_color, top_side_points)
        
        # Draw main face border for definition
        pygame.draw.polygon(self.image, edge_color, main_points, 2)
        
        # Draw 3D edges
        pygame.draw.lines(self.image, edge_color, False, right_side_points, 2)
        pygame.draw.lines(self.image, edge_color, False, top_side_points, 2)
        
        # Add inner highlight for depth
        inner_width = int(TILE_WIDTH * 0.8)
        inner_height = int(TILE_HEIGHT * 0.8)
        inner_points = create_trapezoid_points(center_x, center_y, inner_width, inner_height)
        highlight_color = lighten_color(self.base_color, 1.15)
        pygame.draw.polygon(self.image, highlight_color, inner_points, 1)

        # Add label
        font = pygame.font.SysFont("Arial", 14, bold=True)
        text_surface = font.render(self.label_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        self.image.blit(text_surface, text_rect)

    def draw(self, surface):
        """
        Draw the entity on the given surface.
        
        Args:
            surface (pygame.Surface): The surface to draw on
        """
        # Calculate screen position using isometric conversion
        iso_x, iso_y = to_isometric(self.grid_x, self.grid_y)
        screen_x = iso_x + MAIN_AREA_WIDTH // 2 - self.rect.width//2
        screen_y = iso_y + SCREEN_HEIGHT // 2 - self.rect.height//2
        
        # Draw shadow using trapezoid shape
        shadow_center_x = self.rect.width//2
        shadow_center_y = self.rect.height//2
        shadow_points = create_trapezoid_points(shadow_center_x, shadow_center_y, TILE_WIDTH, TILE_HEIGHT)
        
        # Create a surface for the shadow
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.polygon(shadow_surface, (0, 0, 0, 40), shadow_points)
        
        # Draw shadow and entity
        surface.blit(shadow_surface, (screen_x + 2, screen_y + 2))
        surface.blit(self.image, (screen_x, screen_y))
        
        # Update rect position for collision detection
        self.rect.x = screen_x
        self.rect.y = screen_y

    def update_status_color(self, new_color):
        """
        Update the entity's status color and redraw if changed.
        
        Args:
            new_color (tuple): RGB color tuple for new status color
        """
        if self.base_color != new_color:
            self.base_color = new_color
            self.redraw()

    def draw_connections(self, surface):
        """
        Draw connections to other entities. Override in subclasses.
        
        Args:
            surface (pygame.Surface): The surface to draw connections on
        """
        pass

    def update(self):
        """
        Update entity state. Override in subclasses for specific behavior.
        """
        pass
