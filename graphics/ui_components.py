"""
UI Components Module
Reusable user interface components for the energy simulation
"""

import pygame
import collections
from typing import Tuple, Optional, List, Any, Callable
from .color_manager import color_manager
from .renderer_3d import TrapezoidRenderer, IsometricProjection


class Button:
    """Interactive button component with hover states"""
    
    def __init__(self, x: int, y: int, size: int, text: str, 
                 color: Optional[Tuple[int, int, int]] = None):
        self.rect = pygame.Rect(x, y, size, size)
        self.text = text
        self.color = color or color_manager.get_color('button_normal')
        self.hover_color = color_manager.get_color('button_hover')
        self.text_color = color_manager.get_color('button_text')
        self.is_hovered = False
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button"""
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect)
        
        if self.text:
            font = pygame.font.SysFont("Arial", self.rect.width - 10)
            text_surface = font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False


class Panel:
    """Generic panel container for UI elements"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 bg_color: Optional[Tuple[int, int, int]] = None,
                 border_color: Optional[Tuple[int, int, int]] = None,
                 border_width: int = 0):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color or color_manager.get_color('panel_bg')
        self.border_color = border_color or color_manager.white
        self.border_width = border_width
        
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the panel"""
        # Fill background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        
        # Draw border if specified
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)


class SelectionHighlight:
    """Grid selection visualization component"""
    
    def __init__(self, main_area_width: int, screen_height: int):
        self.main_area_width = main_area_width
        self.screen_height = screen_height
        self.grid_x = 0
        self.grid_y = 0
        self.color = (255, 255, 255, 128)  # Semi-transparent white
        self.projection = IsometricProjection()
        
    def update_position(self, mouse_pos: Tuple[int, int]) -> None:
        """Update highlight position based on mouse position"""
        # Convert screen coordinates to grid coordinates
        screen_center_x = self.main_area_width // 2
        screen_center_y = self.screen_height // 2
        
        # Calculate relative position from screen center
        rel_x = mouse_pos[0] - screen_center_x
        rel_y = mouse_pos[1] - screen_center_y
        
        # Convert to isometric grid coordinates
        self.grid_x, self.grid_y = self.projection.from_isometric(rel_x, rel_y)
        
    def draw(self, surface: pygame.Surface, selected_grid_pos: Optional[Tuple[int, int]] = None) -> None:
        """Draw the selection highlight"""
        if selected_grid_pos is None:
            return
            
        # Use provided position or current position
        grid_x, grid_y = selected_grid_pos if selected_grid_pos else (self.grid_x, self.grid_y)
        
        # Import tile dimensions (TODO: move to layout manager)
        from constants import TILE_WIDTH, TILE_HEIGHT
        
        # Create surface for the highlight
        highlight_surface = pygame.Surface((TILE_WIDTH * 2, TILE_WIDTH * 2), pygame.SRCALPHA)
        
        # Calculate center points for the trapezoid shape
        center_x = highlight_surface.get_width() // 2
        center_y = highlight_surface.get_height() // 2
        
        # Create trapezoid shape for selection highlight
        points = TrapezoidRenderer.create_trapezoid_points(center_x, center_y, TILE_WIDTH, TILE_HEIGHT)
        
        # Draw semi-transparent highlight
        pygame.draw.polygon(highlight_surface, self.color, points)
        pygame.draw.polygon(highlight_surface, (255, 255, 255), points, 2)  # White border
        
        # Calculate screen position
        iso_x, iso_y = self.projection.to_isometric(grid_x, grid_y)
        screen_x = iso_x + self.main_area_width // 2 - highlight_surface.get_width()//2
        screen_y = iso_y + self.screen_height // 2 - highlight_surface.get_height()//2
        
        # Draw the highlight
        surface.blit(highlight_surface, (screen_x, screen_y))


class LogPanel:
    """Log message display panel"""
    
    def __init__(self, x: int, y: int, width: int, height: int, max_messages: int = 8):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_messages = max_messages
        self.messages = collections.deque(maxlen=max_messages)
        self.bg_color = color_manager.get_color('panel_bg')
        self.text_color = color_manager.get_color('log_text')
        self.border_color = color_manager.white
        try:
            self.font = pygame.font.SysFont("Arial", 14)
        except pygame.error:
            # Font not available - set to None for testing
            self.font = None
        
    def add_message(self, message: str) -> None:
        """Add a message to the log"""
        # Truncate message if too long
        if self.font:
            max_chars = self.rect.width // (self.font.size("A")[0] if self.font.size("A")[0] > 0 else 8) - 3
        else:
            max_chars = self.rect.width // 8 - 3  # Fallback for testing
        if len(message) > max_chars:
            message = message[:max_chars] + "..."
        self.messages.append(message)
    
    def clear(self) -> None:
        """Clear all messages"""
        self.messages.clear()
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the log panel"""
        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        
        # Draw top border
        pygame.draw.line(surface, self.border_color, 
                        (self.rect.left, self.rect.top), 
                        (self.rect.right, self.rect.top), 1)
        
        if not self.font:
            return
        
        # Draw messages
        start_y = self.rect.top + 5
        line_height = self.font.get_linesize()
        
        for i, msg in enumerate(list(self.messages)):
            if start_y + i * line_height > self.rect.bottom - line_height:
                break
            if self.font:
                text_surface = self.font.render(msg, True, self.text_color)
                surface.blit(text_surface, (self.rect.left + 5, start_y + i * line_height))


class Menu:
    """Main menu system component"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        try:
            self.title_font = pygame.font.SysFont("Arial", 48)
            self.button_font = pygame.font.SysFont("Arial", 32)
        except pygame.error:
            # Font not available - set to None for testing
            self.title_font = None
            self.button_font = None
        self.background_image = None
        
        # Button configuration
        self.button_width = 400
        self.button_height = 60
        self.left_margin = 50
        self.title_y = 100
        self.title_spacing = 100
        self.button_spacing = 20
        
        # Try to load background image
        try:
            self.background_image = pygame.image.load("assets/menu_background.png")
            self.background_image = pygame.transform.scale(self.background_image, 
                                                          (screen_width, screen_height))
        except (pygame.error, FileNotFoundError):
            self.background_image = None
    
    def draw(self, surface: pygame.Surface) -> List[pygame.Rect]:
        """Draw the menu and return button rects for interaction"""
        # Draw background
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            surface.fill(color_manager.black)
        
        # Create title surface
        if self.title_font:
            title_surface = self.title_font.render("Energy City Simulator", True, color_manager.white)
            title_x = self.left_margin
            
            # Draw title with shadow
            title_shadow = self.title_font.render("Energy City Simulator", True, color_manager.black)
            surface.blit(title_shadow, (title_x + 2, self.title_y + 2))
            surface.blit(title_surface, (title_x, self.title_y))
        
        # Create button rectangles
        start_button = pygame.Rect(
            self.left_margin,
            self.title_y + self.title_spacing,
            self.button_width,
            self.button_height
        )
        
        config_button = pygame.Rect(
            self.left_margin,
            start_button.bottom + self.button_spacing,
            self.button_width,
            self.button_height
        )
        
        exit_button = pygame.Rect(
            self.left_margin,
            config_button.bottom + self.button_spacing,
            self.button_width,
            self.button_height
        )
        
        # Draw buttons
        for button, text in [
            (start_button, "Start Simulation"),
            (config_button, "Configure Components"),
            (exit_button, "Exit")
        ]:
            # Semi-transparent button background
            button_surface = pygame.Surface((button.width, button.height))
            button_surface.set_alpha(180)
            button_surface.fill(color_manager.get_color('panel_bg'))
            surface.blit(button_surface, button.topleft)
            
            # Button border
            pygame.draw.rect(surface, color_manager.white, button, width=2, border_radius=5)
            
            # Button text
            if self.button_font:
                text_surface = self.button_font.render(text, True, color_manager.white)
                text_rect = text_surface.get_rect(center=button.center)
                surface.blit(text_surface, text_rect)
        
        return [start_button, config_button, exit_button]


class Sidebar:
    """Component sidebar container - simplified version for graphics module"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = color_manager.get_color('sidebar_bg')
        self.text_color = color_manager.get_color('sidebar_text')
        self.shadow_color = color_manager.get_color('sidebar_shadow')
        try:
            self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        except pygame.error:
            # Font not available - set to None for testing
            self.title_font = None
        
        # Shadow configuration
        self.shadow_width = 10
        self.shadow_alpha = 128
        self.title_height = 50
        
    def draw_background(self, surface: pygame.Surface) -> None:
        """Draw sidebar background and shadow"""
        # Draw shadow
        shadow_surface = pygame.Surface((self.shadow_width, self.rect.height), pygame.SRCALPHA)
        shadow_color = (*self.shadow_color, self.shadow_alpha)
        pygame.draw.rect(shadow_surface, shadow_color, shadow_surface.get_rect())
        surface.blit(shadow_surface, (self.rect.x - self.shadow_width, self.rect.y))
        
        # Draw background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        
        # Draw title
        title_surface = self.title_font.render("Components", True, self.text_color)
        title_x = self.rect.x + (self.rect.width - title_surface.get_width()) // 2
        title_y = (self.title_height - title_surface.get_height()) // 2
        surface.blit(title_surface, (title_x, title_y))


# Helper function for drawing outlined text
def draw_outlined_text(surface: pygame.Surface, text: str, font: pygame.font.Font, 
                      x: int, y: int, text_color: Tuple[int, int, int], 
                      outline_color: Tuple[int, int, int] = None) -> None:
    """Draw text with an outline for better visibility"""
    if outline_color is None:
        outline_color = color_manager.black
        
    # Draw outline
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                outline_surface = font.render(text, True, outline_color)
                surface.blit(outline_surface, (x + dx, y + dy))
    
    # Draw main text
    text_surface = font.render(text, True, text_color)
    surface.blit(text_surface, (x, y))
