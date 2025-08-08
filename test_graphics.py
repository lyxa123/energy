"""
Tests for Graphics Module - 3D Rendering and UI Components
Validates graphics functionality independently of pygame display
"""

import pytest
import pygame
import math
import os
from unittest.mock import Mock, patch

# Set up headless testing environment
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Initialize pygame for testing
pygame.init()
pygame.display.set_mode((1, 1))  # Minimal display for headless testing

from graphics import (
    Renderer3D, IsometricProjection, TrapezoidRenderer, ShadowRenderer,
    ColorManager, Theme, ColorUtils, color_manager,
    Button, Panel, SelectionHighlight, LogPanel, Menu,
    LayoutManager, Positioning, Dimensions, layout_manager,
    VisualEffects, AnimationManager, animation_manager
)


class TestColorManagement:
    """Test color management functionality"""
    
    def test_color_utils_darken(self):
        """Test color darkening utility"""
        color = (200, 100, 50)
        darkened = ColorUtils.darken_color(color, 0.5)
        assert darkened == (100, 50, 25)
    
    def test_color_utils_lighten(self):
        """Test color lightening utility"""
        color = (100, 50, 25)
        lightened = ColorUtils.lighten_color(color, 2.0)
        assert lightened == (200, 100, 50)
    
    def test_color_utils_lighten_clamp(self):
        """Test color lightening with clamping to 255"""
        color = (200, 200, 200)
        lightened = ColorUtils.lighten_color(color, 2.0)
        assert lightened == (255, 255, 255)
    
    def test_color_utils_blend(self):
        """Test color blending"""
        color1 = (255, 0, 0)  # Red
        color2 = (0, 255, 0)  # Green
        blended = ColorUtils.blend_colors(color1, color2, 0.5)
        assert blended == (127, 127, 0)
    
    def test_color_utils_with_alpha(self):
        """Test adding alpha channel"""
        color = (255, 128, 64)
        with_alpha = ColorUtils.with_alpha(color, 128)
        assert with_alpha == (255, 128, 64, 128)
    
    def test_theme_creation(self):
        """Test theme creation and color retrieval"""
        test_colors = {'red': (255, 0, 0), 'blue': (0, 0, 255)}
        theme = Theme("test", test_colors)
        assert theme.get_color('red') == (255, 0, 0)
        assert theme.get_color('blue') == (0, 0, 255)
    
    def test_color_manager_basic(self):
        """Test basic color manager functionality"""
        manager = ColorManager()
        # Test basic color access
        assert manager.white == (255, 255, 255)
        assert manager.black == (0, 0, 0)
        assert manager.red[0] == 200  # Status critical red
    
    def test_color_manager_status_colors(self):
        """Test electrical status color calculation"""
        manager = ColorManager()
        
        # Normal operation - green
        normal_color = manager.get_status_color(1.0, 0.5)
        assert normal_color == manager.get_color('status_normal')
        
        # Warning condition - yellow
        warning_color = manager.get_status_color(0.97, 0.8)
        assert warning_color == manager.get_color('status_warning')
        
        # Critical condition - red
        critical_color = manager.get_status_color(0.94, 0.95)
        assert critical_color == manager.get_color('status_critical')
    
    def test_color_manager_connection_colors(self):
        """Test connection color calculation based on voltage"""
        manager = ColorManager()
        
        # High voltage - green
        high_voltage_color = manager.get_connection_color(1.0)
        assert high_voltage_color == manager.get_color('connection_voltage_high')
        
        # Low voltage - red component should be present
        low_voltage_color = manager.get_connection_color(0.9)
        assert low_voltage_color[0] > 0  # Should have red component


class TestIsometricProjection:
    """Test isometric coordinate conversion"""
    
    def test_to_isometric_basic(self):
        """Test basic grid to isometric conversion"""
        iso_x, iso_y = IsometricProjection.to_isometric(1, 0)
        assert iso_x == 64  # TILE_WIDTH
        assert iso_y == 31  # TILE_HEIGHT (64 * sin(30°) = 64 * 0.5 = 32, but int() truncates to 31)
    
    def test_to_isometric_negative(self):
        """Test isometric conversion with negative coordinates"""
        iso_x, iso_y = IsometricProjection.to_isometric(-1, 1)
        assert iso_x == -128  # -2 * TILE_WIDTH
        assert iso_y == 0
    
    def test_from_isometric_roundtrip(self):
        """Test isometric conversion roundtrip"""
        original_x, original_y = 3, 2
        iso_x, iso_y = IsometricProjection.to_isometric(original_x, original_y)
        grid_x, grid_y = IsometricProjection.from_isometric(iso_x, iso_y)
        assert grid_x == original_x
        assert grid_y == original_y


class TestTrapezoidRenderer:
    """Test 3D trapezoid shape rendering"""
    
    def test_trapezoid_points_creation(self):
        """Test trapezoid point generation"""
        points = TrapezoidRenderer.create_trapezoid_points(100, 100, 64, 32)
        assert len(points) == 4
        
        # Check that points form a trapezoid shape
        # Top edge should be shorter than bottom edge
        top_width = abs(points[1][0] - points[0][0])
        bottom_width = abs(points[2][0] - points[3][0])
        assert top_width < bottom_width
    
    def test_trapezoid_points_center(self):
        """Test that trapezoid is centered correctly"""
        center_x, center_y = 50, 75
        points = TrapezoidRenderer.create_trapezoid_points(center_x, center_y, 32, 16)
        
        # Calculate centroid
        centroid_x = sum(p[0] for p in points) / 4
        centroid_y = sum(p[1] for p in points) / 4
        
        # Should be close to the specified center
        assert abs(centroid_x - center_x) < 2
        assert abs(centroid_y - center_y) < 2
    
    def test_render_3d_trapezoid(self):
        """Test 3D trapezoid rendering"""
        surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Should not raise exception
        TrapezoidRenderer.render_3d_trapezoid(surface, 100, 100, (255, 0, 0))
        
        # Surface should have been modified (not transparent)
        surface_data = pygame.surfarray.array3d(surface)
        assert surface_data.max() > 0


class TestRenderer3D:
    """Test main 3D rendering engine"""
    
    def test_renderer_creation(self):
        """Test 3D renderer initialization"""
        renderer = Renderer3D(800, 600)
        assert renderer.main_area_width == 800
        assert renderer.screen_height == 600
        assert renderer.projection is not None
    
    def test_render_entity_surface(self):
        """Test entity surface rendering"""
        renderer = Renderer3D(800, 600)
        surface = renderer.render_entity_surface((0, 255, 0), "PS", 64)
        
        # Should return a valid surface
        assert isinstance(surface, pygame.Surface)
        assert surface.get_width() == 128  # 64 * 2
        assert surface.get_height() == 128
    
    def test_get_screen_position(self):
        """Test screen position calculation"""
        renderer = Renderer3D(800, 600)
        screen_x, screen_y = renderer.get_screen_position(0, 0, 64)
        
        # Should be centered in main area
        assert screen_x == 400 - 64  # main_area_width // 2 - entity_size
        assert screen_y == 300 - 64  # screen_height // 2 - entity_size


class TestUIComponents:
    """Test UI component functionality"""
    
    def test_button_creation(self):
        """Test button creation and properties"""
        button = Button(10, 20, 50, "Test")
        assert button.rect.x == 10
        assert button.rect.y == 20
        assert button.rect.width == 50
        assert button.text == "Test"
        assert button.is_hovered == False
    
    def test_button_hover_detection(self):
        """Test button hover state detection"""
        button = Button(10, 10, 50, "Test")
        
        # Create mock mouse motion event inside button
        event = Mock()
        event.type = pygame.MOUSEMOTION
        event.pos = (35, 35)  # Inside button
        
        result = button.handle_event(event)
        assert button.is_hovered == True
        assert result == False  # No click
    
    def test_button_click_detection(self):
        """Test button click detection"""
        button = Button(10, 10, 50, "Test")
        
        # Create mock click event inside button
        event = Mock()
        event.type = pygame.MOUSEBUTTONDOWN
        event.button = 1  # Left click
        event.pos = (35, 35)  # Inside button
        
        result = button.handle_event(event)
        assert result == True  # Click detected
    
    def test_panel_creation(self):
        """Test panel creation"""
        panel = Panel(0, 0, 100, 200)
        assert panel.rect.width == 100
        assert panel.rect.height == 200
    
    def test_panel_draw(self):
        """Test panel drawing"""
        surface = pygame.Surface((200, 200))
        panel = Panel(10, 10, 100, 50)
        
        # Should not raise exception
        panel.draw(surface)
    
    def test_selection_highlight_creation(self):
        """Test selection highlight creation"""
        highlight = SelectionHighlight(800, 600)
        assert highlight.main_area_width == 800
        assert highlight.screen_height == 600
    
    def test_selection_highlight_position_update(self):
        """Test selection highlight position update"""
        highlight = SelectionHighlight(800, 600)
        highlight.update_position((450, 350))  # Slightly off center
        
        # Grid position should be calculated
        assert isinstance(highlight.grid_x, int)
        assert isinstance(highlight.grid_y, int)
    
    def test_log_panel_creation(self):
        """Test log panel creation"""
        log_panel = LogPanel(0, 500, 800, 100, max_messages=5)
        assert log_panel.max_messages == 5
        assert len(log_panel.messages) == 0
    
    def test_log_panel_add_message(self):
        """Test log panel message addition"""
        log_panel = LogPanel(0, 500, 800, 100, max_messages=3)
        
        log_panel.add_message("Message 1")
        log_panel.add_message("Message 2")
        log_panel.add_message("Message 3")
        log_panel.add_message("Message 4")  # Should replace first message
        
        assert len(log_panel.messages) == 3
        assert "Message 4" in log_panel.messages
        assert "Message 1" not in log_panel.messages  # Should be removed
    
    def test_log_panel_clear(self):
        """Test log panel clearing"""
        log_panel = LogPanel(0, 500, 800, 100)
        log_panel.add_message("Test message")
        log_panel.clear()
        assert len(log_panel.messages) == 0
    
    def test_menu_creation(self):
        """Test menu creation"""
        menu = Menu(800, 600)
        assert menu.screen_width == 800
        assert menu.screen_height == 600
    
    def test_menu_draw(self):
        """Test menu drawing"""
        surface = pygame.Surface((800, 600))
        menu = Menu(800, 600)
        
        button_rects = menu.draw(surface)
        assert len(button_rects) == 3  # Start, Config, Exit


class TestLayoutManager:
    """Test layout management functionality"""
    
    def test_dimensions_creation(self):
        """Test dimensions object creation"""
        dims = Dimensions(1600, 900, 250)
        assert dims.screen_width == 1600
        assert dims.screen_height == 900
        assert dims.sidebar_width == 250
        assert dims.main_area_width == 1350  # 1600 - 250
    
    def test_positioning_center(self):
        """Test element centering calculations"""
        center_x = Positioning.center_horizontally(800, 200)
        center_y = Positioning.center_vertically(600, 100)
        
        assert center_x == 300  # (800 - 200) // 2
        assert center_y == 250  # (600 - 100) // 2
    
    def test_positioning_center_in_rect(self):
        """Test centering element in rectangle"""
        container = pygame.Rect(100, 50, 400, 300)
        element_size = (100, 50)
        
        x, y = Positioning.center_in_rect(container, element_size)
        assert x == 250  # 100 + (400 - 100) // 2
        assert y == 175  # 50 + (300 - 50) // 2
    
    def test_positioning_distribute_evenly(self):
        """Test even distribution of elements"""
        positions = Positioning.distribute_evenly(800, 3, 100)
        assert len(positions) == 3
        assert positions[0] > 0  # Should have some margin
        assert positions[2] < 700  # Should fit within container
    
    def test_layout_manager_creation(self):
        """Test layout manager initialization"""
        manager = LayoutManager(1600, 900, 250)
        assert manager.dimensions.screen_width == 1600
        assert manager.dimensions.main_area_width == 1350
    
    def test_layout_manager_rectangles(self):
        """Test layout manager rectangle calculations"""
        manager = LayoutManager(1600, 900, 250)
        
        main_rect = manager.main_area_rect
        sidebar_rect = manager.sidebar_rect
        
        assert main_rect.width == 1350
        assert sidebar_rect.width == 250
        assert sidebar_rect.x == 1350  # Should start after main area
    
    def test_layout_manager_button_positions(self):
        """Test button position calculations"""
        manager = LayoutManager(1600, 900, 250)
        positions = manager.calculate_button_positions(3, 50, 1350, 10)
        
        assert len(positions) == 3
        # All positions should be within the area
        for x, y in positions:
            assert x >= 0
            assert x + 50 <= 1350


class TestVisualEffects:
    """Test visual effects functionality"""
    
    def test_glow_effect(self):
        """Test glow effect rendering"""
        surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Should not raise exception
        VisualEffects.draw_glow_effect(surface, (100, 100), 20, (255, 0, 0), 1.0)
    
    def test_pulse_effect(self):
        """Test pulse effect rendering"""
        surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Should not raise exception
        VisualEffects.draw_pulse_effect(surface, (100, 100), 30, (0, 255, 0), 1.0)
    
    def test_connection_flow(self):
        """Test connection flow animation"""
        surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Should not raise exception
        VisualEffects.draw_connection_flow(surface, (50, 50), (150, 150), (255, 255, 0), 0.5)
    
    def test_voltage_indicator(self):
        """Test voltage indicator rendering"""
        surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Should not raise exception for various voltage levels
        VisualEffects.draw_voltage_indicator(surface, (100, 100), 1.0)  # High voltage
        VisualEffects.draw_voltage_indicator(surface, (100, 120), 0.96)  # Medium voltage
        VisualEffects.draw_voltage_indicator(surface, (100, 140), 0.9)   # Low voltage
    
    def test_loading_indicator(self):
        """Test loading indicator rendering"""
        surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
        # Should not raise exception for various loading levels
        VisualEffects.draw_loading_indicator(surface, (100, 100), 0.5)   # Normal
        VisualEffects.draw_loading_indicator(surface, (100, 120), 0.8)   # Warning
        VisualEffects.draw_loading_indicator(surface, (100, 140), 0.95)  # Critical
    
    def test_fade_transition(self):
        """Test fade transition effect"""
        surface = pygame.Surface((200, 200))
        
        # Should not raise exception
        VisualEffects.draw_fade_transition(surface, 128, (0, 0, 0))
        VisualEffects.draw_fade_transition(surface, 0, (0, 0, 0))  # No fade


class TestAnimationManager:
    """Test animation management functionality"""
    
    def test_animation_manager_creation(self):
        """Test animation manager initialization"""
        manager = AnimationManager()
        assert isinstance(manager.get_time(), float)
    
    def test_animation_add_and_progress(self):
        """Test adding animations and getting progress"""
        manager = AnimationManager()
        manager.add_animation("test", 2.0, loop=True)
        
        progress = manager.get_animation_progress("test")
        assert 0.0 <= progress <= 1.0
    
    def test_animation_completion(self):
        """Test animation completion detection"""
        manager = AnimationManager()
        manager.add_animation("test", 0.01, loop=False)  # 10ms duration
        
        # Should be completed after sufficient time
        import time
        time.sleep(0.02)  # Wait longer than animation duration
        assert manager.is_animation_complete("test") == True
    
    def test_animation_removal(self):
        """Test animation removal"""
        manager = AnimationManager()
        manager.add_animation("test", 1.0)
        manager.remove_animation("test")
        
        # Should return default values after removal
        progress = manager.get_animation_progress("test")
        assert progress == 0.0


class TestGraphicsIntegration:
    """Test integration between graphics components"""
    
    def test_renderer_with_color_manager(self):
        """Test 3D renderer using color manager"""
        renderer = Renderer3D(800, 600)
        green_color = color_manager.green
        
        surface = renderer.render_entity_surface(green_color, "PS")
        assert isinstance(surface, pygame.Surface)
    
    def test_ui_with_layout_manager(self):
        """Test UI components using layout manager"""
        main_rect = layout_manager.main_area_rect
        button = Button(main_rect.x + 10, main_rect.y + 10, 50, "Test")
        
        assert button.rect.x >= main_rect.x
        assert button.rect.y >= main_rect.y
    
    def test_effects_with_color_manager(self):
        """Test visual effects using color manager"""
        surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        red_color = color_manager.red
        
        # Should not raise exception
        VisualEffects.draw_glow_effect(surface, (100, 100), 20, red_color)


if __name__ == "__main__":
    # Run tests directly if script is executed
    pytest.main([__file__, "-v"])
