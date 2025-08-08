"""
PowerConsumer entity for electrical loads

This module contains the PowerConsumer class which represents electrical
loads in the simulation. PowerConsumers can be inductive, capacitive, or
resistive and connect to PowerStations for power supply.
"""

import math
import pygame
from .base_entity import Entity
from constants import (
    CONSUMER_SIZE, BLUE, RED, YELLOW, GREEN, CONNECTION_THICKNESS,
    DEFAULT_CONSUMER_P_DEMAND, CONSUMER_TYPE_INDUCTIVE, CONSUMER_TYPE_CAPACITIVE,
    CONSUMER_TYPE_RESISTIVE, DEFAULT_INDUCTIVE_PF, DEFAULT_CAPACITIVE_PF, 
    DEFAULT_RESISTIVE_PF
)


class PowerConsumer(Entity):
    """
    Electrical load entity that consumes power from PowerStations.
    
    Supports three types of loads:
    - Inductive: Motors, transformers (positive Q)
    - Capacitive: Capacitor banks (negative Q) 
    - Resistive: Heating, lighting (zero Q)
    
    Features:
    - Automatic reactive power calculation based on power factor
    - Visual status indication based on voltage level
    - Connection management with PowerStations
    - Network integration for PyPSA simulation
    """
    
    def __init__(self, grid_x, grid_y, bus_name, consumer_type, 
                 config_manager=None, logger=None, network_manager=None):
        """
        Initialize a new PowerConsumer.
        
        Args:
            grid_x (int): Grid X coordinate
            grid_y (int): Grid Y coordinate  
            bus_name (str): Name of the electrical bus
            consumer_type (str): Type of consumer (inductive/capacitive/resistive)
            config_manager (ConfigurationManager, optional): Configuration source
            logger (callable, optional): Logging function for messages
            network_manager (NetworkManager, optional): Network operations manager
        """
        # Set label based on consumer type
        label = self._get_consumer_label(consumer_type)
        
        super().__init__(grid_x, grid_y, CONSUMER_SIZE, BLUE, label, bus_name, "consumer")
        
        # Consumer properties
        self.consumer_type = consumer_type
        self.connected_power_station = None
        self.is_connected = False
        
        # External dependencies
        self.config_manager = config_manager
        self.logger = logger or self._default_logger
        self.network_manager = network_manager
        
        # Load electrical parameters
        self._load_electrical_parameters()

    def _get_consumer_label(self, consumer_type):
        """Get display label for consumer type"""
        if consumer_type == CONSUMER_TYPE_INDUCTIVE:
            return "CI"
        elif consumer_type == CONSUMER_TYPE_CAPACITIVE:
            return "CC"
        else:  # Resistive
            return "CR"

    def _load_electrical_parameters(self):
        """Load electrical parameters from configuration or defaults"""
        if self.config_manager:
            try:
                config_type = f"{self.consumer_type.upper()}_CONSUMER"
                self.p_demand_rate = self.config_manager.current_configs[config_type]["p_demand_rate"]
                self.power_factor = self.config_manager.current_configs[config_type]["power_factor"]
            except (KeyError, AttributeError):
                self._set_default_parameters()
        else:
            self._set_default_parameters()
        
        # Calculate reactive power based on consumer type and power factor
        self._calculate_reactive_power()

    def _set_default_parameters(self):
        """Set default electrical parameters"""
        self.p_demand_rate = DEFAULT_CONSUMER_P_DEMAND
        
        if self.consumer_type == CONSUMER_TYPE_INDUCTIVE:
            self.power_factor = DEFAULT_INDUCTIVE_PF
        elif self.consumer_type == CONSUMER_TYPE_CAPACITIVE:
            self.power_factor = DEFAULT_CAPACITIVE_PF
        else:  # Resistive
            self.power_factor = DEFAULT_RESISTIVE_PF

    def _calculate_reactive_power(self):
        """Calculate reactive power demand based on power factor and type"""
        if self.consumer_type == CONSUMER_TYPE_INDUCTIVE:
            # Inductive loads: positive Q
            self.q_demand_rate = self.p_demand_rate * math.tan(math.acos(self.power_factor))
        elif self.consumer_type == CONSUMER_TYPE_CAPACITIVE:
            # Capacitive loads: negative Q
            self.q_demand_rate = -self.p_demand_rate * math.tan(math.acos(self.power_factor))
        else:  # Resistive
            # Resistive loads: zero Q
            self.q_demand_rate = 0

    def _default_logger(self, message):
        """Default logger that does nothing (for testing)"""
        pass

    def connect(self, power_station):
        """
        Connect this consumer to a power station.
        
        Args:
            power_station (PowerStation): The power station to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        if power_station is None:
            return False
            
        # Update connection state
        self.connected_power_station = power_station
        self.is_connected = True
        
        # Connect at power station end
        power_station.connect_consumer(self)
        
        # Update network if network manager available
        if self.network_manager:
            try:
                self.network_manager.add_connection(power_station.bus_name, self.bus_name)
                self.network_manager.update_load(self.bus_name, self.p_demand_rate, self.q_demand_rate)
            except Exception as e:
                self.logger(f"Failed to update network: {str(e)}")
        
        self.logger(f"Connected {self.label_text} (P={self.p_demand_rate:.1f}MW, Q={self.q_demand_rate:.1f}MVAr)")
        return True

    def disconnect(self):
        """
        Disconnect this consumer from its power station.
        
        Returns:
            bool: True if disconnection successful, False if not connected
        """
        if self.connected_power_station is None:
            return False
        
        # Disconnect at power station end
        self.connected_power_station.disconnect_consumer(self)
        
        # Update network if network manager available
        if self.network_manager:
            try:
                self.network_manager.remove_connection(self.bus_name)
                self.network_manager.reset_load(self.bus_name)
            except Exception as e:
                self.logger(f"Failed to update network: {str(e)}")
        
        # Update connection state
        self.connected_power_station = None
        self.is_connected = False
        
        self.logger(f"Disconnected {self.label_text}")
        self.update_status_color(BLUE)
        return True

    def update(self):
        """
        Update consumer status based on connection state and voltage.
        
        Updates visual status color based on:
        - Connection state (blue if unconnected)
        - Voltage level from connected power station
        """
        if not self.is_connected:
            self.update_status_color(BLUE)  # Unconnected color
        elif self.connected_power_station:
            # Get voltage from connected power station
            voltage = self.connected_power_station.voltage_pu
            
            # Update status color based on voltage thresholds
            if voltage < 0.95:
                self.update_status_color(RED)
                self.logger(f"Low voltage at {self.label_text}: {voltage:.2f} pu")
            elif voltage < 0.98:
                self.update_status_color(YELLOW)
            else:
                self.update_status_color(GREEN)
        
        self.redraw()

    def draw_connections(self, surface):
        """
        Draw connection line to connected power station.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        if not self.connected_power_station:
            return
            
        # Calculate connection line endpoints
        start_pos = (self.rect.x + self.rect.width//2, self.rect.y + self.rect.height//2)
        end_pos = (
            self.connected_power_station.rect.x + self.connected_power_station.rect.width//2,
            self.connected_power_station.rect.y + self.connected_power_station.rect.height//2
        )
        
        # Get line color based on voltage level
        line_color = self._get_connection_line_color()
        
        # Draw connection line
        pygame.draw.line(surface, line_color, start_pos, end_pos, CONNECTION_THICKNESS)

    def _get_connection_line_color(self):
        """
        Get connection line color based on voltage level.
        
        Returns:
            tuple: RGB color tuple for connection line
        """
        voltage = self.connected_power_station.voltage_pu
        
        if voltage >= 0.98:
            return GREEN
        elif voltage >= 0.95:
            # Interpolate between yellow and green
            factor = min(max((voltage - 0.95) / 0.03, 0), 1)
            green = 255
            red = int(255 * (1-factor))
            return (red, green, 0)
        else:
            # Interpolate between red and yellow
            factor = min(max(voltage / 0.95, 0), 1)
            red = 255
            green = int(255 * factor)
            return (red, green, 0)

    def get_apparent_power(self):
        """
        Calculate apparent power (S) from active and reactive power.
        
        Returns:
            float: Apparent power in MVA
        """
        return math.sqrt(self.p_demand_rate**2 + self.q_demand_rate**2)

    def get_power_factor_actual(self):
        """
        Calculate actual power factor from P and S.
        
        Returns:
            float: Power factor (0.0 to 1.0)
        """
        s = self.get_apparent_power()
        return self.p_demand_rate / s if s > 0 else 1.0

    def update_demand(self, new_p_demand, new_power_factor=None):
        """
        Update power demand and recalculate reactive power.
        
        Args:
            new_p_demand (float): New active power demand in MW
            new_power_factor (float, optional): New power factor
        """
        self.p_demand_rate = new_p_demand
        
        if new_power_factor is not None:
            self.power_factor = new_power_factor
            
        self._calculate_reactive_power()
        
        # Update network if connected and network manager available
        if self.is_connected and self.network_manager:
            try:
                self.network_manager.update_load(self.bus_name, self.p_demand_rate, self.q_demand_rate)
            except Exception as e:
                self.logger(f"Failed to update network demand: {str(e)}")

    def get_status_summary(self):
        """
        Get a summary of the consumer's current status.
        
        Returns:
            dict: Status information including power demands and connection state
        """
        return {
            'consumer_type': self.consumer_type,
            'is_connected': self.is_connected,
            'p_demand_rate': self.p_demand_rate,
            'q_demand_rate': self.q_demand_rate,
            'power_factor': self.power_factor,
            'apparent_power': self.get_apparent_power(),
            'actual_power_factor': self.get_power_factor_actual(),
            'connected_to': self.connected_power_station.bus_name if self.connected_power_station else None,
            'voltage_pu': self.connected_power_station.voltage_pu if self.connected_power_station else None
        }
