"""
Unit tests for PowerStation entity

Tests the PowerStation class functionality including:
- Creation and initialization
- Configuration loading
- Consumer connection management
- Voltage and loading calculations
- Status updates and color changes
"""
import os
import sys
import pytest
import pygame

# Set pygame to headless mode for testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add the project root directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.power_station import PowerStation
from entities.power_consumer import PowerConsumer
from config_manager import ConfigurationManager
from constants import GREEN, RED, YELLOW, CONSUMER_TYPE_INDUCTIVE


class MockLogger:
    """Mock logger for testing"""
    def __init__(self):
        self.messages = []
    
    def __call__(self, message):
        self.messages.append(message)


class TestPowerStation:
    """Test PowerStation entity functionality"""
    
    @classmethod
    def setup_class(cls):
        """Initialize pygame for all tests"""
        pygame.init()
        cls.screen = pygame.display.set_mode((100, 100))
    
    @classmethod
    def teardown_class(cls):
        """Clean up after tests"""
        pygame.quit()
    
    def test_power_station_creation_without_config(self):
        """Test PowerStation creation without configuration manager"""
        logger = MockLogger()
        power_station = PowerStation(5, 3, "PS_Bus_1", None, logger)
        
        # Verify basic properties
        assert power_station.grid_x == 5
        assert power_station.grid_y == 3
        assert power_station.bus_name == "PS_Bus_1"
        assert power_station.entity_type == "power_station"
        assert power_station.label_text == "PS"
        
        # Verify electrical properties
        assert power_station.connected_consumers == []
        assert power_station.total_p_demand == 0
        assert power_station.total_q_demand == 0
        assert power_station.voltage_pu == 1.0
        
        # Verify default configuration
        assert power_station.p_nom == 1000.0
        assert power_station.v_nom == 110.0
    
    def test_power_station_creation_with_config(self):
        """Test PowerStation creation with configuration manager"""
        config_manager = ConfigurationManager(':memory:')
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_2", config_manager, logger)
        
        # Verify configured values are loaded
        assert hasattr(power_station, 'p_nom')
        assert hasattr(power_station, 'v_nom')
        assert power_station.p_nom > 0
        assert power_station.v_nom > 0
    
    def test_consumer_connection(self):
        """Test connecting consumers to power station"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_3", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_1", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        # Initial state
        assert len(power_station.connected_consumers) == 0
        assert not consumer.is_connected
        
        # Connect consumer
        result = power_station.connect_consumer(consumer)
        assert result == True
        assert len(power_station.connected_consumers) == 1
        assert consumer in power_station.connected_consumers
        
        # Check logger messages
        assert len(logger.messages) > 0
        assert "connected" in logger.messages[-1].lower()
        
        # Try to connect same consumer again
        result = power_station.connect_consumer(consumer)
        assert result == False  # Should fail (already connected)
        assert len(power_station.connected_consumers) == 1  # No duplicates
    
    def test_consumer_disconnection(self):
        """Test disconnecting consumers from power station"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_4", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_2", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        # Connect then disconnect
        power_station.connect_consumer(consumer)
        assert len(power_station.connected_consumers) == 1
        
        result = power_station.disconnect_consumer(consumer)
        assert result == True
        assert len(power_station.connected_consumers) == 0
        assert consumer not in power_station.connected_consumers
        
        # Try to disconnect again
        result = power_station.disconnect_consumer(consumer)
        assert result == False  # Should fail (not connected)
    
    def test_voltage_calculation_normal_loading(self):
        """Test voltage calculation under normal loading"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_5", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_3", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        # Set moderate demand
        consumer.p_demand_rate = 100.0  # 100 MW (10% of 1000 MW capacity)
        consumer.q_demand_rate = 75.0   # 75 MVAr
        consumer.is_connected = True
        
        power_station.connect_consumer(consumer)
        
        # Verify voltage calculation
        expected_voltage = 1.0 - (0.1 * 0.1) - (75.0 * 0.02)  # 1.0 - 0.01 - 1.5 = -0.51
        assert power_station.voltage_pu == expected_voltage
        assert power_station.total_p_demand == 100.0
        assert power_station.total_q_demand == 75.0
    
    def test_loading_percentage_calculation(self):
        """Test loading percentage calculation"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_6", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_4", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        consumer.p_demand_rate = 500.0  # 50% loading
        consumer.is_connected = True
        power_station.connect_consumer(consumer)
        
        assert power_station.get_loading_percent() == 0.5
        assert power_station.get_available_capacity() == 500.0
        assert not power_station.is_overloaded()
    
    def test_overload_condition(self):
        """Test overload detection"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_7", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_5", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        consumer.p_demand_rate = 1200.0  # 120% loading (overload)
        consumer.is_connected = True
        power_station.connect_consumer(consumer)
        
        assert power_station.get_loading_percent() > 1.0
        assert power_station.get_available_capacity() == 0  # Clamped to 0
        assert power_station.is_overloaded()
    
    def test_status_color_updates(self):
        """Test status color updates based on operating conditions"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_8", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_6", CONSUMER_TYPE_INDUCTIVE, None, logger)
        consumer.is_connected = True
        
        # Normal conditions - should be green (low loading, good voltage)
        consumer.p_demand_rate = 200.0  # 20% loading, voltage = 0.98 pu
        consumer.q_demand_rate = 0      # No reactive power
        power_station.connect_consumer(consumer)
        assert power_station.base_color == GREEN
        
        # Warning conditions - should be yellow (loading > 70% but voltage still above 0.95)  
        consumer.p_demand_rate = 400.0  # 40% loading, voltage = 0.96 pu
        power_station.update()
        assert power_station.base_color == YELLOW  # voltage < 0.98 triggers yellow
        
        # Critical conditions - should be red (voltage drops below 0.95)
        consumer.p_demand_rate = 600.0  # 60% loading, voltage = 0.94 pu  
        power_station.update()
        assert power_station.base_color == RED
        
        # Check that warning messages were logged
        warning_messages = [msg for msg in logger.messages if "Warning" in msg]
        assert len(warning_messages) > 0
    
    def test_status_summary(self):
        """Test status summary functionality"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_9", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_7", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        consumer.p_demand_rate = 300.0
        consumer.q_demand_rate = 150.0
        consumer.is_connected = True
        power_station.connect_consumer(consumer)
        
        status = power_station.get_status_summary()
        
        assert status['loading_percent'] == 0.3
        assert status['total_p_demand'] == 300.0
        assert status['total_q_demand'] == 150.0
        assert status['available_capacity'] == 700.0
        assert status['connected_consumers'] == 1
        assert status['is_overloaded'] == False
        assert 'voltage_pu' in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
