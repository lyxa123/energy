"""
Unit tests for PowerConsumer entity

Tests the PowerConsumer class functionality including:
- Creation and initialization for different consumer types
- Configuration loading
- Reactive power calculations
- Connection management with PowerStations
- Status updates and visual feedback
"""
import os
import sys
import pytest
import pygame
import math

# Set pygame to headless mode for testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add the project root directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities.power_consumer import PowerConsumer
from entities.power_station import PowerStation
from config_manager import ConfigurationManager
from constants import (
    BLUE, RED, YELLOW, GREEN, CONSUMER_TYPE_INDUCTIVE,
    CONSUMER_TYPE_CAPACITIVE, CONSUMER_TYPE_RESISTIVE
)


class MockLogger:
    """Mock logger for testing"""
    def __init__(self):
        self.messages = []
    
    def __call__(self, message):
        self.messages.append(message)


class MockNetworkManager:
    """Mock network manager for testing"""
    def __init__(self):
        self.connections = []
        self.loads = {}
    
    def add_connection(self, from_bus, to_bus):
        self.connections.append((from_bus, to_bus))
    
    def remove_connection(self, bus_name):
        self.connections = [conn for conn in self.connections if bus_name not in conn]
    
    def update_load(self, bus_name, p, q):
        self.loads[bus_name] = (p, q)
    
    def reset_load(self, bus_name):
        if bus_name in self.loads:
            del self.loads[bus_name]


class TestPowerConsumer:
    """Test PowerConsumer entity functionality"""
    
    @classmethod
    def setup_class(cls):
        """Initialize pygame for all tests"""
        pygame.init()
        cls.screen = pygame.display.set_mode((100, 100))
    
    @classmethod
    def teardown_class(cls):
        """Clean up after tests"""
        pygame.quit()
    
    def test_inductive_consumer_creation(self):
        """Test creating inductive consumer"""
        logger = MockLogger()
        consumer = PowerConsumer(2, 3, "Consumer_Bus_1", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        # Verify basic properties
        assert consumer.grid_x == 2
        assert consumer.grid_y == 3
        assert consumer.bus_name == "Consumer_Bus_1"
        assert consumer.consumer_type == CONSUMER_TYPE_INDUCTIVE
        assert consumer.label_text == "CI"
        assert consumer.entity_type == "consumer"
        
        # Verify electrical properties
        assert consumer.p_demand_rate > 0
        assert consumer.q_demand_rate > 0  # Inductive should have positive Q
        assert consumer.power_factor > 0 and consumer.power_factor < 1
        assert not consumer.is_connected
        assert consumer.connected_power_station is None
        
        # Verify Q calculation
        expected_q = consumer.p_demand_rate * math.tan(math.acos(consumer.power_factor))
        assert abs(consumer.q_demand_rate - expected_q) < 0.001
    
    def test_capacitive_consumer_creation(self):
        """Test creating capacitive consumer"""
        logger = MockLogger()
        consumer = PowerConsumer(4, 5, "Consumer_Bus_2", CONSUMER_TYPE_CAPACITIVE, None, logger)
        
        assert consumer.label_text == "CC"
        assert consumer.consumer_type == CONSUMER_TYPE_CAPACITIVE
        assert consumer.q_demand_rate < 0  # Capacitive should have negative Q
        
        # Verify Q calculation
        expected_q = -consumer.p_demand_rate * math.tan(math.acos(consumer.power_factor))
        assert abs(consumer.q_demand_rate - expected_q) < 0.001
    
    def test_resistive_consumer_creation(self):
        """Test creating resistive consumer"""
        logger = MockLogger()
        consumer = PowerConsumer(6, 7, "Consumer_Bus_3", CONSUMER_TYPE_RESISTIVE, None, logger)
        
        assert consumer.label_text == "CR"
        assert consumer.consumer_type == CONSUMER_TYPE_RESISTIVE
        assert consumer.q_demand_rate == 0  # Resistive should have zero Q
        assert consumer.power_factor == 1.0  # Perfect power factor
    
    def test_consumer_with_configuration(self):
        """Test consumer creation with configuration manager"""
        config_manager = ConfigurationManager(':memory:')
        logger = MockLogger()
        consumer = PowerConsumer(0, 0, "Consumer_Bus_4", CONSUMER_TYPE_INDUCTIVE, config_manager, logger)
        
        # Should load values from configuration
        assert hasattr(consumer, 'p_demand_rate')
        assert hasattr(consumer, 'power_factor')
        assert consumer.p_demand_rate > 0
        assert consumer.power_factor > 0
    
    def test_connection_to_power_station(self):
        """Test connecting consumer to power station"""
        logger = MockLogger()
        network_manager = MockNetworkManager()
        
        power_station = PowerStation(0, 0, "PS_Bus_1", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_5", CONSUMER_TYPE_INDUCTIVE, 
                                None, logger, network_manager)
        
        # Initial state
        assert not consumer.is_connected
        assert consumer.connected_power_station is None
        assert len(power_station.connected_consumers) == 0
        
        # Connect
        result = consumer.connect(power_station)
        assert result == True
        assert consumer.is_connected
        assert consumer.connected_power_station is power_station
        assert consumer in power_station.connected_consumers
        
        # Verify network manager was called
        assert len(network_manager.connections) == 1
        assert network_manager.connections[0] == ("PS_Bus_1", "Consumer_Bus_5")
        assert "Consumer_Bus_5" in network_manager.loads
    
    def test_disconnection_from_power_station(self):
        """Test disconnecting consumer from power station"""
        logger = MockLogger()
        network_manager = MockNetworkManager()
        
        power_station = PowerStation(0, 0, "PS_Bus_2", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_6", CONSUMER_TYPE_INDUCTIVE, 
                                None, logger, network_manager)
        
        # Connect then disconnect
        consumer.connect(power_station)
        assert consumer.is_connected
        
        result = consumer.disconnect()
        assert result == True
        assert not consumer.is_connected
        assert consumer.connected_power_station is None
        assert consumer not in power_station.connected_consumers
        
        # Verify network manager cleanup
        assert len(network_manager.connections) == 0
        assert "Consumer_Bus_6" not in network_manager.loads
    
    def test_status_update_unconnected(self):
        """Test status update when unconnected"""
        logger = MockLogger()
        consumer = PowerConsumer(1, 1, "Consumer_Bus_7", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        consumer.update()
        assert consumer.base_color == BLUE  # Unconnected color
    
    def test_status_update_connected(self):
        """Test status update when connected with different voltage levels"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_3", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_8", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        consumer.connect(power_station)
        
        # Normal voltage (>= 0.98) - should be green
        power_station.voltage_pu = 1.0
        consumer.update()
        assert consumer.base_color == GREEN
        
        # Warning voltage (0.95-0.98) - should be yellow
        power_station.voltage_pu = 0.96
        consumer.update()
        assert consumer.base_color == YELLOW
        
        # Low voltage (< 0.95) - should be red
        power_station.voltage_pu = 0.94
        consumer.update()
        assert consumer.base_color == RED
        
        # Check that low voltage was logged
        low_voltage_messages = [msg for msg in logger.messages if "Low voltage" in msg]
        assert len(low_voltage_messages) > 0
    
    def test_apparent_power_calculation(self):
        """Test apparent power calculation"""
        logger = MockLogger()
        consumer = PowerConsumer(1, 1, "Consumer_Bus_9", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        # Set known values
        consumer.p_demand_rate = 3.0  # MW
        consumer.q_demand_rate = 4.0  # MVAr
        
        # S = sqrt(P^2 + Q^2) = sqrt(9 + 16) = 5
        expected_s = math.sqrt(3.0**2 + 4.0**2)
        assert abs(consumer.get_apparent_power() - expected_s) < 0.001
        
        # Verify power factor calculation
        expected_pf = 3.0 / 5.0  # P/S = 0.6
        assert abs(consumer.get_power_factor_actual() - expected_pf) < 0.001
    
    def test_demand_update(self):
        """Test updating power demand"""
        logger = MockLogger()
        network_manager = MockNetworkManager()
        consumer = PowerConsumer(1, 1, "Consumer_Bus_10", CONSUMER_TYPE_INDUCTIVE, 
                                None, logger, network_manager)
        
        # Update demand
        old_p = consumer.p_demand_rate
        old_q = consumer.q_demand_rate
        
        consumer.update_demand(10.0, 0.85)
        
        assert consumer.p_demand_rate == 10.0
        assert consumer.power_factor == 0.85
        assert consumer.q_demand_rate != old_q  # Should recalculate
        
        # Verify Q recalculation
        expected_q = 10.0 * math.tan(math.acos(0.85))
        assert abs(consumer.q_demand_rate - expected_q) < 0.001
    
    def test_status_summary(self):
        """Test status summary functionality"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_4", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_11", CONSUMER_TYPE_CAPACITIVE, None, logger)
        
        consumer.connect(power_station)
        status = consumer.get_status_summary()
        
        assert status['consumer_type'] == CONSUMER_TYPE_CAPACITIVE
        assert status['is_connected'] == True
        assert status['connected_to'] == "PS_Bus_4"
        assert 'p_demand_rate' in status
        assert 'q_demand_rate' in status
        assert 'power_factor' in status
        assert 'apparent_power' in status
        assert 'actual_power_factor' in status
        assert 'voltage_pu' in status
    
    def test_connection_line_color_calculation(self):
        """Test connection line color calculation for different voltage levels"""
        logger = MockLogger()
        power_station = PowerStation(0, 0, "PS_Bus_5", None, logger)
        consumer = PowerConsumer(1, 1, "Consumer_Bus_12", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        consumer.connect(power_station)
        
        # High voltage - should be green
        power_station.voltage_pu = 1.0
        color = consumer._get_connection_line_color()
        assert color == GREEN
        
        # Medium voltage - should be interpolated yellow-green
        power_station.voltage_pu = 0.96
        color = consumer._get_connection_line_color()
        assert color != GREEN and color != RED
        
        # Low voltage - should be interpolated red-yellow
        power_station.voltage_pu = 0.92
        color = consumer._get_connection_line_color()
        assert color != GREEN
    
    def test_connection_failure_cases(self):
        """Test connection failure cases"""
        logger = MockLogger()
        consumer = PowerConsumer(1, 1, "Consumer_Bus_13", CONSUMER_TYPE_INDUCTIVE, None, logger)
        
        # Try to connect to None
        result = consumer.connect(None)
        assert result == False
        assert not consumer.is_connected
        
        # Try to disconnect when not connected
        result = consumer.disconnect()
        assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
