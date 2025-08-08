"""
Unit tests for electrical entities (PowerStation, PowerConsumer, etc.)
"""
import os
import sys
import pytest
import pygame
import math

# Set pygame to headless mode for testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from constants import *
from config_manager import ConfigurationManager, COMPONENT_TYPES

class TestEntity:
    """Test the base Entity class functionality"""
    
    @classmethod
    def setup_class(cls):
        """Initialize pygame for all tests"""
        pygame.init()
        # Create a minimal display for testing
        cls.screen = pygame.display.set_mode((100, 100))
    
    @classmethod
    def teardown_class(cls):
        """Clean up pygame after all tests"""
        pygame.quit()
    
    def test_entity_creation(self):
        """Test basic entity creation without pygame dependencies"""
        from pyPSA_db import Entity
        
        # Create an entity at grid position (5, 3)
        entity = Entity(5, 3, 50, GREEN, "TEST", "test_bus", "test_entity")
        
        # Verify grid position
        assert entity.grid_x == 5
        assert entity.grid_y == 3
        
        # Verify attributes
        assert entity.label_text == "TEST"
        assert entity.bus_name == "test_bus"
        assert entity.entity_type == "test_entity"
        assert entity.base_color == GREEN
        assert entity.is_connected == False
        assert entity.voltage_pu == 1.0

class TestPowerStation:
    """Test PowerStation entity functionality"""
    
    @classmethod
    def setup_class(cls):
        """Initialize pygame and config manager for tests"""
        pygame.init()
        cls.screen = pygame.display.set_mode((100, 100))
        cls.config_manager = ConfigurationManager(':memory:')  # Use in-memory DB for testing
    
    @classmethod
    def teardown_class(cls):
        """Clean up after tests"""
        pygame.quit()
    
    def test_power_station_creation(self):
        """Test PowerStation creation and default values"""
        from pyPSA_db import PowerStation
        
        # Mock config_manager globally for the test
        import pyPSA_db
        original_config = pyPSA_db.config_manager
        pyPSA_db.config_manager = self.config_manager
        
        try:
            power_station = PowerStation(0, 0, "PS_Bus_1")
            
            # Verify inheritance from Entity
            assert power_station.grid_x == 0
            assert power_station.grid_y == 0
            assert power_station.label_text == "PS"
            assert power_station.entity_type == "power_station"
            
            # Verify PowerStation-specific attributes
            assert power_station.connected_consumers == []
            assert power_station.total_p_demand == 0
            assert power_station.total_q_demand == 0
            assert power_station.voltage_pu == 1.0
            
            # Verify configured values are loaded
            assert hasattr(power_station, 'p_nom')
            assert hasattr(power_station, 'v_nom')
            
        finally:
            # Restore original config_manager
            pyPSA_db.config_manager = original_config
    
    def test_power_station_voltage_calculation(self):
        """Test voltage calculation based on loading"""
        from pyPSA_db import PowerStation, PowerConsumer, CONSUMER_TYPE_INDUCTIVE
        
        # Mock config_manager
        import pyPSA_db
        original_config = pyPSA_db.config_manager
        pyPSA_db.config_manager = self.config_manager
        
        try:
            power_station = PowerStation(0, 0, "PS_Bus_1")
            
            # Create a mock consumer for testing
            consumer = PowerConsumer(1, 1, "Consumer_Bus_1", CONSUMER_TYPE_INDUCTIVE)
            consumer.p_demand_rate = 100.0  # 100 MW
            consumer.q_demand_rate = 75.0   # 75 MVAr
            consumer.is_connected = True
            
            # Connect consumer to power station
            power_station.connected_consumers.append(consumer)
            
            # Update power station (this calculates voltage)
            power_station.update()
            
            # Verify voltage calculation
            # Expected: 1.0 - (100/1000 * 0.1) - (75 * 0.02) = 1.0 - 0.01 - 0.15 = 0.84
            expected_voltage = 1.0 - (100.0/DEFAULT_POWER_STATION_P_CAPACITY * 0.1) - (abs(75.0) * 0.02)
            assert abs(power_station.voltage_pu - expected_voltage) < 0.001
            
        finally:
            pyPSA_db.config_manager = original_config

class TestPowerConsumer:
    """Test PowerConsumer entity functionality"""
    
    @classmethod
    def setup_class(cls):
        """Initialize pygame and config manager for tests"""
        pygame.init()
        cls.screen = pygame.display.set_mode((100, 100))
        cls.config_manager = ConfigurationManager(':memory:')
    
    @classmethod
    def teardown_class(cls):
        """Clean up after tests"""
        pygame.quit()
    
    def test_inductive_consumer_creation(self):
        """Test inductive consumer creation and Q calculation"""
        from pyPSA_db import PowerConsumer, CONSUMER_TYPE_INDUCTIVE
        
        # Mock config_manager
        import pyPSA_db
        original_config = pyPSA_db.config_manager
        pyPSA_db.config_manager = self.config_manager
        
        try:
            consumer = PowerConsumer(2, 3, "Consumer_Bus_1", CONSUMER_TYPE_INDUCTIVE)
            
            # Verify basic attributes
            assert consumer.grid_x == 2
            assert consumer.grid_y == 3
            assert consumer.label_text == "CI"  # Inductive consumer label
            assert consumer.consumer_type == CONSUMER_TYPE_INDUCTIVE
            assert consumer.is_connected == False
            assert consumer.connected_power_station is None
            
            # Verify Q calculation for inductive load
            # Q = P * tan(acos(PF))
            expected_q = consumer.p_demand_rate * math.tan(math.acos(consumer.power_factor))
            assert abs(consumer.q_demand_rate - expected_q) < 0.001
            assert consumer.q_demand_rate > 0  # Inductive Q should be positive
            
        finally:
            pyPSA_db.config_manager = original_config
    
    def test_capacitive_consumer_creation(self):
        """Test capacitive consumer creation and Q calculation"""
        from pyPSA_db import PowerConsumer, CONSUMER_TYPE_CAPACITIVE
        
        # Mock config_manager
        import pyPSA_db
        original_config = pyPSA_db.config_manager
        pyPSA_db.config_manager = self.config_manager
        
        try:
            consumer = PowerConsumer(4, 5, "Consumer_Bus_2", CONSUMER_TYPE_CAPACITIVE)
            
            # Verify basic attributes
            assert consumer.label_text == "CC"  # Capacitive consumer label
            assert consumer.consumer_type == CONSUMER_TYPE_CAPACITIVE
            
            # Verify Q calculation for capacitive load
            # Q = -P * tan(acos(PF))
            expected_q = -consumer.p_demand_rate * math.tan(math.acos(consumer.power_factor))
            assert abs(consumer.q_demand_rate - expected_q) < 0.001
            assert consumer.q_demand_rate < 0  # Capacitive Q should be negative
            
        finally:
            pyPSA_db.config_manager = original_config
    
    def test_resistive_consumer_creation(self):
        """Test resistive consumer creation"""
        from pyPSA_db import PowerConsumer, CONSUMER_TYPE_RESISTIVE
        
        # Mock config_manager
        import pyPSA_db
        original_config = pyPSA_db.config_manager
        pyPSA_db.config_manager = self.config_manager
        
        try:
            consumer = PowerConsumer(6, 7, "Consumer_Bus_3", CONSUMER_TYPE_RESISTIVE)
            
            # Verify basic attributes
            assert consumer.label_text == "CR"  # Resistive consumer label
            assert consumer.consumer_type == CONSUMER_TYPE_RESISTIVE
            
            # Verify Q is zero for resistive load
            assert consumer.q_demand_rate == 0
            assert consumer.power_factor == 1.0
            
        finally:
            pyPSA_db.config_manager = original_config

class TestUtilityFunctions:
    """Test utility functions that don't require pygame"""
    
    def test_isometric_conversion(self):
        """Test grid to isometric coordinate conversion"""
        from pyPSA_db import to_isometric
        
        # Test center position
        iso_x, iso_y = to_isometric(0, 0)
        assert iso_x == 0
        assert iso_y == 0
        
        # Test known positions
        iso_x, iso_y = to_isometric(1, 0)
        assert iso_x == TILE_WIDTH
        assert iso_y == TILE_HEIGHT
        
        iso_x, iso_y = to_isometric(0, 1)
        assert iso_x == -TILE_WIDTH
        assert iso_y == TILE_HEIGHT
    
    def test_trapezoid_points_creation(self):
        """Test trapezoid point calculation"""
        from pyPSA_db import create_trapezoid_points
        
        # Test basic trapezoid creation
        points = create_trapezoid_points(100, 100, 64, 32)
        
        # Should return 4 points
        assert len(points) == 4
        
        # All points should be tuples of (x, y)
        for point in points:
            assert len(point) == 2
            assert isinstance(point[0], (int, float))
            assert isinstance(point[1], (int, float))
    
    def test_color_utility_functions(self):
        """Test color manipulation functions"""
        from pyPSA_db import darken_color, lighten_color
        
        test_color = (100, 150, 200)
        
        # Test darkening
        darker = darken_color(test_color, 0.5)
        assert darker == (50, 75, 100)
        
        # Test lightening
        lighter = lighten_color(test_color, 1.5)
        assert lighter == (150, 225, 255)  # Clamped to 255
        
        # Test default factors
        default_darker = darken_color(test_color)
        assert default_darker == (70, 105, 140)  # 0.7 factor

class TestConfigurationManager:
    """Test configuration management functionality"""
    
    def test_config_manager_creation(self):
        """Test creating a configuration manager with in-memory database"""
        config_manager = ConfigurationManager(':memory:')
        
        # Verify default configurations are loaded
        assert 'POWER_STATION' in config_manager.current_configs
        assert 'INDUCTIVE_CONSUMER' in config_manager.current_configs
        assert 'CAPACITIVE_CONSUMER' in config_manager.current_configs
        assert 'RESISTIVE_CONSUMER' in config_manager.current_configs
        
        # Verify power station config
        ps_config = config_manager.current_configs['POWER_STATION']
        assert 'p_nom_mw' in ps_config
        assert 'v_nom_kv' in ps_config
        assert ps_config['p_nom_mw'] == 1000.0  # Default value
        assert ps_config['v_nom_kv'] == 110.0   # Default value
    
    def test_component_types_definition(self):
        """Test that component types are properly defined"""
        # Verify all expected component types exist
        expected_components = [
            'POWER_STATION', 'INDUCTIVE_CONSUMER', 'CAPACITIVE_CONSUMER', 
            'RESISTIVE_CONSUMER', 'TRANSMISSION_LINE', 'SUBSTATION',
            'STEP_UP_TRANSFORMER', 'STEP_DOWN_TRANSFORMER', 'POWER_LINE', 'POWER_POLE'
        ]
        
        for component in expected_components:
            assert component in COMPONENT_TYPES
            assert 'label' in COMPONENT_TYPES[component]
            assert 'description' in COMPONENT_TYPES[component]
            assert 'icon_color' in COMPONENT_TYPES[component]


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])
