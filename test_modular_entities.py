"""
Unit tests for the new modular entity system

These tests verify that the refactored entities work correctly and 
maintain backward compatibility with the existing codebase.
"""
import os
import sys
import pytest
import pygame

# Set pygame to headless mode for testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from entities.base_entity import Entity
from constants import GREEN, BLUE, RED, TILE_WIDTH, TILE_HEIGHT


class TestModularEntities:
    """Test the new modular entity system"""
    
    @classmethod
    def setup_class(cls):
        """Initialize pygame for all tests"""
        pygame.init()
        cls.screen = pygame.display.set_mode((100, 100))
    
    @classmethod
    def teardown_class(cls):
        """Clean up pygame after all tests"""
        pygame.quit()
    
    def test_entity_module_import(self):
        """Test that we can import Entity from the new module"""
        from entities.base_entity import Entity as ModularEntity
        from entities import Entity as PackageEntity
        
        # Both imports should work and be the same class
        assert ModularEntity is not None
        assert PackageEntity is not None
        assert ModularEntity is PackageEntity
    
    def test_entity_creation_with_new_module(self):
        """Test creating entities with the new modular structure"""
        entity = Entity(3, 4, 50, GREEN, "TEST", "test_bus", "test_type")
        
        # Verify all attributes are set correctly
        assert entity.grid_x == 3
        assert entity.grid_y == 4
        assert entity.base_color == GREEN
        assert entity.label_text == "TEST"
        assert entity.bus_name == "test_bus"
        assert entity.entity_type == "test_type"
        
        # Verify pygame attributes are created
        assert entity.image is not None
        assert entity.rect is not None
        assert entity.image.get_width() == TILE_WIDTH * 2
        assert entity.image.get_height() == TILE_WIDTH * 2
    
    def test_entity_redraw_functionality(self):
        """Test that entity redraw works correctly"""
        entity = Entity(0, 0, 50, BLUE, "REDRAW")
        
        # Change color and redraw
        original_color = entity.base_color
        entity.update_status_color(RED)
        
        # Verify color changed
        assert entity.base_color == RED
        assert entity.base_color != original_color
    
    def test_entity_position_methods(self):
        """Test entity positioning and coordinate conversion"""
        entity = Entity(5, 7, 50, GREEN, "POS")
        
        # Test that entity stores grid position correctly
        assert entity.grid_x == 5
        assert entity.grid_y == 7
        
        # Test that draw method can be called without error
        try:
            test_surface = pygame.Surface((100, 100))
            entity.draw(test_surface)
            # If we reach here, draw() worked without error
            assert True
        except Exception as e:
            pytest.fail(f"Entity.draw() raised an exception: {e}")
    
    def test_entity_electrical_properties(self):
        """Test that electrical properties are initialized correctly"""
        entity = Entity(1, 1, 30, BLUE, "ELEC")
        
        # Verify electrical properties
        assert entity.voltage_pu == 1.0
        assert entity.is_connected == False
        assert entity.total_p_demand == 0
        assert entity.total_q_demand == 0
        assert entity.p_demand_rate == 0
        assert entity.power_factor == 1.0
    
    def test_entity_abstract_methods(self):
        """Test that abstract methods can be called"""
        entity = Entity(2, 2, 40, RED, "ABSTRACT")
        
        # These should not raise errors (they're no-op in base class)
        try:
            test_surface = pygame.Surface((100, 100))
            entity.draw_connections(test_surface)
            entity.update()
            assert True
        except Exception as e:
            pytest.fail(f"Abstract methods raised an exception: {e}")


class TestBackwardCompatibility:
    """Test that the new modular structure maintains backward compatibility"""
    
    @classmethod
    def setup_class(cls):
        """Initialize pygame for all tests"""
        pygame.init()
        cls.screen = pygame.display.set_mode((100, 100))
    
    @classmethod  
    def teardown_class(cls):
        """Clean up pygame after all tests"""
        pygame.quit()
    
    def test_original_entity_still_works(self):
        """Test that the original Entity from pyPSA_db.py still works"""
        # Import the original Entity
        from pyPSA_db import Entity as OriginalEntity
        
        # Create entity using original interface
        entity = OriginalEntity(1, 2, 50, GREEN, "ORIG", "orig_bus", "orig_type")
        
        # Verify it has the same interface as our new Entity
        assert hasattr(entity, 'grid_x')
        assert hasattr(entity, 'grid_y') 
        assert hasattr(entity, 'base_color')
        assert hasattr(entity, 'label_text')
        assert hasattr(entity, 'redraw')
        assert hasattr(entity, 'draw')
        assert hasattr(entity, 'update_status_color')
    
    def test_entity_api_compatibility(self):
        """Test that both old and new entities have the same API"""
        from pyPSA_db import Entity as OriginalEntity
        from entities.base_entity import Entity as NewEntity
        
        # Create instances of both
        orig_entity = OriginalEntity(1, 1, 50, GREEN, "ORIG")
        new_entity = NewEntity(1, 1, 50, GREEN, "NEW")
        
        # Test that they have the same key attributes
        common_attrs = [
            'grid_x', 'grid_y', 'base_color', 'label_text', 
            'bus_name', 'entity_type', 'is_connected', 'voltage_pu'
        ]
        
        for attr in common_attrs:
            assert hasattr(orig_entity, attr), f"Original entity missing {attr}"
            assert hasattr(new_entity, attr), f"New entity missing {attr}"
        
        # Test that they have the same key methods
        common_methods = ['redraw', 'draw', 'update_status_color', 'draw_connections']
        
        for method in common_methods:
            assert hasattr(orig_entity, method), f"Original entity missing {method}"
            assert hasattr(new_entity, method), f"New entity missing {method}"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])
