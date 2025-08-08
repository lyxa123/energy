# Energy Simulation System - Refactoring Plan

## Current State Analysis

### Files:
- `pyPSA_db.py` (1,400+ lines) - Main simulation engine
- `config_manager.py` (1,100+ lines) - Configuration management
- `constants.py` (180 lines) - Shared constants
- `requirements.txt` - Dependencies
- `test_entities.py` - Initial unit tests

### Issues:
1. **Monolithic Structure**: pyPSA_db.py contains too many responsibilities
2. **Tight Coupling**: UI, game logic, and electrical simulation mixed together
3. **Global State**: Many global variables make testing difficult
4. **Code Duplication**: Similar patterns repeated across classes

## Proposed Modular Architecture

### Phase 1: Core Electrical Components (Immediate)
```
entities/
├── __init__.py
├── base_entity.py      # Entity base class
├── power_station.py    # PowerStation class
├── power_consumer.py   # PowerConsumer class
└── electrical_grid.py  # Grid and connection management
```

### Phase 2: Game Engine Separation
```
game/
├── __init__.py
├── graphics.py         # 3D rendering, UI elements
├── input_handler.py    # Mouse/keyboard input management
├── game_state.py       # Game state management
└── main_loop.py        # Main game loop
```

### Phase 3: Network & Simulation
```
simulation/
├── __init__.py
├── pypsa_network.py    # PyPSA network management
├── power_flow.py       # Power flow calculations
└── simulation_runner.py # Simulation orchestration
```

### Phase 4: UI Components
```
ui/
├── __init__.py
├── sidebar.py          # Sidebar components
├── menu.py            # Menu system
├── dialogs.py         # Configuration dialogs
└── help_system.py     # Help screens
```

### Phase 5: Configuration & Data
```
data/
├── __init__.py
├── database.py        # Database operations
├── config_loader.py   # Configuration loading
└── saved_instances.py # Saved instance management
```

## Benefits of This Structure

### 1. **Single Responsibility Principle**
- Each module has one clear purpose
- Easier to understand and maintain
- Simpler testing

### 2. **Dependency Injection**
- Remove global variables
- Pass dependencies explicitly
- Better testability

### 3. **Separation of Concerns**
- Graphics separated from business logic
- Network simulation isolated
- UI components decoupled

### 4. **Enhanced Testability**
- Each module can be tested independently
- Mock dependencies easily
- Faster test execution

## Implementation Strategy

### Step 1: Extract Entity Classes (This Week)
- Move Entity, PowerStation, PowerConsumer to separate files
- Maintain backward compatibility
- Add comprehensive unit tests

### Step 2: Separate Graphics Engine (Next Week)
- Extract pygame-specific code
- Create graphics abstraction layer
- Enable headless testing

### Step 3: Network Management (Week 3)
- Isolate PyPSA network code
- Create network manager class
- Add network simulation tests

### Step 4: UI Refactoring (Week 4)
- Extract sidebar, menu, dialog code
- Create UI component framework
- Add UI interaction tests

### Step 5: Configuration System (Week 5)
- Improve configuration management
- Add configuration validation
- Create configuration tests

## Testing Strategy

### Unit Tests (Immediate)
- ✅ Entity creation and behavior
- ✅ Electrical calculations
- ✅ Configuration management
- Power flow simulation
- Grid connection logic

### Integration Tests (Phase 2)
- Entity-to-entity interactions
- UI-to-backend communication
- Database operations
- Full simulation scenarios

### End-to-End Tests (Phase 3)
- Complete user workflows
- Configuration management flows
- Save/load functionality
- Error handling scenarios

## Migration Path

### Backward Compatibility
- Keep existing imports working
- Gradual migration of functionality
- Deprecation warnings for old patterns

### Performance Considerations
- Maintain current performance levels
- Optimize import structures
- Reduce module loading overhead

### Documentation
- Document new module interfaces
- Create architecture diagrams
- Update developer guides

## Next Immediate Steps

1. **Create entities/ module** with base classes
2. **Add comprehensive unit tests** for each component
3. **Extract PowerStation and PowerConsumer** to separate files
4. **Update imports** in main files
5. **Run full test suite** to ensure no regressions

This modular approach will make implementing multi-connection architecture much easier and maintainable.
