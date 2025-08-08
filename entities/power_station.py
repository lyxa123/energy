"""
PowerStation entity for electrical power generation

This module contains the PowerStation class which represents electrical
power generation units in the simulation. PowerStations can connect to
multiple consumers and manage power flow, voltage regulation, and loading.
"""

from .base_entity import Entity
from constants import (
    POWER_STATION_SIZE, GREEN, RED, YELLOW, 
    DEFAULT_POWER_STATION_P_CAPACITY
)


class PowerStation(Entity):
    """
    Electrical power generation unit that supplies power to consumers.
    
    Features:
    - Voltage regulation based on loading
    - Multiple consumer connections
    - Real-time power flow monitoring
    - Visual status indication through color changes
    """
    
    def __init__(self, grid_x, grid_y, bus_name, config_manager=None, logger=None):
        """
        Initialize a new PowerStation.
        
        Args:
            grid_x (int): Grid X coordinate
            grid_y (int): Grid Y coordinate  
            bus_name (str): Name of the electrical bus
            config_manager (ConfigurationManager, optional): Configuration source
            logger (callable, optional): Logging function for messages
        """
        super().__init__(grid_x, grid_y, POWER_STATION_SIZE, GREEN, "PS", bus_name, "power_station")
        
        # Connection management
        self.connected_consumers = []
        
        # Electrical state
        self.total_p_demand = 0
        self.total_q_demand = 0
        self.voltage_pu = 1.0
        
        # Configuration and logging
        self.config_manager = config_manager
        self.logger = logger or self._default_logger
        
        # Load configured values
        self._load_configuration()

    def _load_configuration(self):
        """Load configuration values from config manager"""
        if self.config_manager:
            try:
                self.p_nom = self.config_manager.current_configs["POWER_STATION"]["p_nom_mw"]
                self.v_nom = self.config_manager.current_configs["POWER_STATION"]["v_nom_kv"]
            except (KeyError, AttributeError):
                self._set_default_configuration()
        else:
            self._set_default_configuration()
    
    def _set_default_configuration(self):
        """Set default configuration values"""
        self.p_nom = 1000.0  # MW
        self.v_nom = 110.0   # kV
    
    def _default_logger(self, message):
        """Default logger that does nothing (for testing)"""
        pass

    def update(self):
        """
        Update power station state including:
        - Total power demands from connected consumers
        - Voltage calculation based on loading
        - Status color updates based on operating conditions
        """
        # Calculate total demands from connected consumers
        self.total_p_demand = sum(
            c.p_demand_rate for c in self.connected_consumers if c.is_connected
        )
        self.total_q_demand = sum(
            c.q_demand_rate for c in self.connected_consumers if c.is_connected
        )
        
        # Calculate loading percentage based on real power
        loading_percent = self.total_p_demand / DEFAULT_POWER_STATION_P_CAPACITY
        
        # Voltage calculation: voltage drops with loading and reactive power
        self.voltage_pu = 1.0 - (loading_percent * 0.1) - (abs(self.total_q_demand) * 0.02)
        
        # Update status color based on operating conditions
        self._update_status_based_on_conditions(loading_percent)
        
        # Redraw with new status color
        self.redraw()

    def _update_status_based_on_conditions(self, loading_percent):
        """
        Update status color and log warnings based on operating conditions.
        
        Args:
            loading_percent (float): Current loading as percentage of capacity
        """
        # Critical conditions (red)
        if loading_percent > 0.9 or self.voltage_pu < 0.95:
            self.update_status_color(RED)
            if loading_percent > 0.9:
                self.logger(f"Warning: High loading at power station: {loading_percent*100:.1f}%")
            if self.voltage_pu < 0.95:
                self.logger(f"Warning: Low voltage at power station: {self.voltage_pu:.2f} pu")
        
        # Warning conditions (yellow)
        elif loading_percent > 0.7 or self.voltage_pu < 0.98:
            self.update_status_color(YELLOW)
        
        # Normal conditions (green)
        else:
            self.update_status_color(GREEN)

    def connect_consumer(self, consumer):
        """
        Connect a consumer to this power station.
        
        Args:
            consumer (PowerConsumer): The consumer to connect
            
        Returns:
            bool: True if connection was successful, False if already connected
        """
        if consumer not in self.connected_consumers:
            self.connected_consumers.append(consumer)
            self.logger(
                f"Power Station connected to {consumer.label_text} "
                f"(P={consumer.p_demand_rate:.1f}MW, Q={consumer.q_demand_rate:.1f}MVAr)"
            )
            self.update()
            return True
        return False
    
    def disconnect_consumer(self, consumer):
        """
        Disconnect a consumer from this power station.
        
        Args:
            consumer (PowerConsumer): The consumer to disconnect
            
        Returns:
            bool: True if disconnection was successful, False if not connected
        """
        if consumer in self.connected_consumers:
            self.connected_consumers.remove(consumer)
            self.logger(f"Power Station disconnected from {consumer.label_text}")
            self.update()
            return True
        return False
    
    def get_loading_percent(self):
        """
        Get current loading percentage.
        
        Returns:
            float: Loading percentage (0.0 to 1.0+)
        """
        return self.total_p_demand / DEFAULT_POWER_STATION_P_CAPACITY
    
    def get_available_capacity(self):
        """
        Get available power capacity.
        
        Returns:
            float: Available capacity in MW
        """
        return max(0, DEFAULT_POWER_STATION_P_CAPACITY - self.total_p_demand)
    
    def is_overloaded(self):
        """
        Check if power station is overloaded.
        
        Returns:
            bool: True if overloaded (loading > 100%)
        """
        return self.get_loading_percent() > 1.0
    
    def get_status_summary(self):
        """
        Get a summary of the power station's current status.
        
        Returns:
            dict: Status information including loading, voltage, and capacity
        """
        return {
            'loading_percent': self.get_loading_percent(),
            'voltage_pu': self.voltage_pu,
            'total_p_demand': self.total_p_demand,
            'total_q_demand': self.total_q_demand,
            'available_capacity': self.get_available_capacity(),
            'connected_consumers': len(self.connected_consumers),
            'is_overloaded': self.is_overloaded()
        }
