"""
Visual Effects Module
Handles special visual effects like transitions, animations, and visual feedback
"""

import pygame
import math
from typing import Tuple, Optional, List
from .color_manager import ColorUtils


class VisualEffects:
    """Collection of visual effects for the energy simulation"""
    
    @staticmethod
    def draw_glow_effect(surface: pygame.Surface, center: Tuple[int, int], 
                        radius: int, color: Tuple[int, int, int], 
                        intensity: float = 1.0) -> None:
        """Draw a glowing effect around a point"""
        # Create multiple circles with decreasing alpha for glow effect
        num_layers = 5
        for i in range(num_layers):
            layer_radius = radius + (i * 3)
            alpha = int((intensity * 50) / (i + 1))  # Decrease alpha for outer layers
            glow_color = (*color, alpha)
            
            # Create surface for this layer
            glow_surface = pygame.Surface((layer_radius * 2, layer_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (layer_radius, layer_radius), layer_radius)
            
            # Blit to main surface
            surface.blit(glow_surface, (center[0] - layer_radius, center[1] - layer_radius))
    
    @staticmethod
    def draw_pulse_effect(surface: pygame.Surface, center: Tuple[int, int], 
                         base_radius: int, color: Tuple[int, int, int], 
                         time_factor: float) -> None:
        """Draw a pulsing effect that varies with time"""
        # Calculate pulsing radius
        pulse_amplitude = base_radius * 0.3
        pulse_radius = base_radius + pulse_amplitude * math.sin(time_factor)
        
        # Draw the pulsing circle
        alpha = int(128 + 127 * math.sin(time_factor * 0.5))  # Vary alpha too
        pulse_color = (*color, alpha)
        
        pulse_surface = pygame.Surface((pulse_radius * 2, pulse_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(pulse_surface, pulse_color, (int(pulse_radius), int(pulse_radius)), int(pulse_radius))
        
        surface.blit(pulse_surface, (center[0] - int(pulse_radius), center[1] - int(pulse_radius)))
    
    @staticmethod
    def draw_connection_flow(surface: pygame.Surface, start_pos: Tuple[int, int], 
                           end_pos: Tuple[int, int], color: Tuple[int, int, int],
                           flow_progress: float, thickness: int = 3) -> None:
        """Draw animated flow effect along a connection line"""
        # Calculate line properties
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        line_length = math.sqrt(dx * dx + dy * dy)
        
        if line_length == 0:
            return
        
        # Normalize direction vector
        dir_x = dx / line_length
        dir_y = dy / line_length
        
        # Draw base line
        pygame.draw.line(surface, color, start_pos, end_pos, thickness)
        
        # Draw flowing dots
        num_dots = 5
        dot_spacing = line_length / num_dots
        
        for i in range(num_dots):
            # Calculate dot position with flow animation
            base_distance = i * dot_spacing
            flow_distance = (base_distance + flow_progress * line_length) % line_length
            
            dot_x = start_pos[0] + int(flow_distance * dir_x)
            dot_y = start_pos[1] + int(flow_distance * dir_y)
            
            # Draw flowing dot with glow
            bright_color = ColorUtils.lighten_color(color, 1.5)
            pygame.draw.circle(surface, bright_color, (dot_x, dot_y), thickness + 1)
    
    @staticmethod
    def draw_voltage_indicator(surface: pygame.Surface, position: Tuple[int, int], 
                              voltage_pu: float, size: int = 20) -> None:
        """Draw voltage level indicator with color coding"""
        # Determine color based on voltage level
        if voltage_pu >= 0.98:
            color = (0, 255, 0)  # Green
        elif voltage_pu >= 0.95:
            # Interpolate between yellow and green
            factor = (voltage_pu - 0.95) / 0.03
            color = ColorUtils.blend_colors((255, 255, 0), (0, 255, 0), factor)
        else:
            # Interpolate between red and yellow
            factor = voltage_pu / 0.95
            color = ColorUtils.blend_colors((255, 0, 0), (255, 255, 0), factor)
        
        # Draw voltage bar
        bar_width = size
        bar_height = int(size * 0.3)
        fill_width = int(bar_width * voltage_pu)
        
        # Background bar
        bg_rect = pygame.Rect(position[0] - bar_width//2, position[1] - bar_height//2, 
                             bar_width, bar_height)
        pygame.draw.rect(surface, (64, 64, 64), bg_rect)
        
        # Voltage level fill
        fill_rect = pygame.Rect(position[0] - bar_width//2, position[1] - bar_height//2, 
                               fill_width, bar_height)
        pygame.draw.rect(surface, color, fill_rect)
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), bg_rect, 1)
    
    @staticmethod
    def draw_loading_indicator(surface: pygame.Surface, position: Tuple[int, int], 
                              loading_percent: float, size: int = 20) -> None:
        """Draw loading percentage indicator with color coding"""
        # Determine color based on loading level
        if loading_percent <= 0.7:
            color = (0, 255, 0)  # Green - Normal
        elif loading_percent <= 0.9:
            color = (255, 255, 0)  # Yellow - Warning
        else:
            color = (255, 0, 0)  # Red - Critical
        
        # Draw circular loading indicator
        center = position
        radius = size // 2
        
        # Background circle
        pygame.draw.circle(surface, (64, 64, 64), center, radius)
        
        # Loading arc
        if loading_percent > 0:
            end_angle = loading_percent * 360
            # PyGame arc angles are in radians and start from 3 o'clock
            start_angle_rad = math.radians(-90)  # Start from 12 o'clock
            end_angle_rad = math.radians(-90 + end_angle)
            
            # Draw arc (simulate with small rectangles for better control)
            num_segments = int(end_angle / 5)  # 5 degrees per segment
            for i in range(num_segments):
                angle = start_angle_rad + (i * math.radians(5))
                x1 = center[0] + int((radius - 3) * math.cos(angle))
                y1 = center[1] + int((radius - 3) * math.sin(angle))
                x2 = center[0] + int((radius + 1) * math.cos(angle))
                y2 = center[1] + int((radius + 1) * math.sin(angle))
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)
        
        # Border circle
        pygame.draw.circle(surface, (255, 255, 255), center, radius, 1)
    
    @staticmethod
    def draw_fade_transition(surface: pygame.Surface, alpha: int, 
                           color: Tuple[int, int, int] = (0, 0, 0)) -> None:
        """Draw fade overlay for transitions"""
        if alpha <= 0:
            return
            
        fade_surface = pygame.Surface(surface.get_size())
        fade_surface.set_alpha(alpha)
        fade_surface.fill(color)
        surface.blit(fade_surface, (0, 0))
    
    @staticmethod
    def draw_highlight_border(surface: pygame.Surface, rect: pygame.Rect, 
                             color: Tuple[int, int, int] = (255, 255, 255),
                             width: int = 2, pulse_time: Optional[float] = None) -> None:
        """Draw animated highlight border around a rectangle"""
        if pulse_time is not None:
            # Animate border intensity
            intensity = 0.5 + 0.5 * math.sin(pulse_time * 4)
            animated_color = tuple(int(c * intensity) for c in color)
            pygame.draw.rect(surface, animated_color, rect, width)
        else:
            pygame.draw.rect(surface, color, rect, width)
    
    @staticmethod
    def draw_particle_effect(surface: pygame.Surface, center: Tuple[int, int],
                           particles: List[dict], color: Tuple[int, int, int]) -> None:
        """Draw particle system effect"""
        for particle in particles:
            x = int(particle['x'])
            y = int(particle['y'])
            size = int(particle['size'])
            alpha = int(particle['alpha'])
            
            if alpha > 0 and size > 0:
                particle_color = (*color, alpha)
                particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, particle_color, (size, size), size)
                surface.blit(particle_surface, (x - size, y - size))


class AnimationManager:
    """Manages timing and state for animations"""
    
    def __init__(self):
        self.animations = {}
        self.start_time = pygame.time.get_ticks()
    
    def get_time(self) -> float:
        """Get current animation time in seconds"""
        return (pygame.time.get_ticks() - self.start_time) / 1000.0
    
    def add_animation(self, name: str, duration: float, loop: bool = True) -> None:
        """Add a named animation with duration"""
        self.animations[name] = {
            'duration': duration,
            'loop': loop,
            'start_time': self.get_time()
        }
    
    def get_animation_progress(self, name: str) -> float:
        """Get animation progress (0.0 to 1.0)"""
        if name not in self.animations:
            return 0.0
        
        anim = self.animations[name]
        elapsed = self.get_time() - anim['start_time']
        progress = elapsed / anim['duration']
        
        if anim['loop']:
            return progress % 1.0
        else:
            return min(progress, 1.0)
    
    def is_animation_complete(self, name: str) -> bool:
        """Check if non-looping animation is complete"""
        if name not in self.animations:
            return True
        
        anim = self.animations[name]
        if anim['loop']:
            return False
        
        elapsed = self.get_time() - anim['start_time']
        return elapsed >= anim['duration']
    
    def remove_animation(self, name: str) -> None:
        """Remove animation"""
        if name in self.animations:
            del self.animations[name]


# Global animation manager instance
animation_manager = AnimationManager()
