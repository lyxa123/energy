"""
Entities module - Electrical components for the energy simulation

This module contains the core electrical entities used in the simulation:
- Entity: Base class for all simulation entities  
- PowerStation: Electrical power generation units
- PowerConsumer: Electrical load units (inductive, capacitive, resistive)

The entities are designed to be testable, maintainable, and modular.
"""

from .base_entity import Entity
from .power_station import PowerStation  
from .power_consumer import PowerConsumer

__all__ = [
    'Entity',
    'PowerStation', 
    'PowerConsumer'
]
