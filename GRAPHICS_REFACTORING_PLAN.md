# Graphics/UI Refactoring Plan - Phase 2

## Overview
Extract all graphics, rendering, and UI components from the main application into separate, testable modules. This will complete the modular architecture by separating visual presentation from business logic.

## 🎯 Graphics Module Structure
```
graphics/
├── __init__.py              # Public interface: Renderer3D, ColorManager, etc.
├── renderer_3d.py           # 3D isometric rendering engine  
├── ui_components.py         # Reusable UI components (Button, Panel, etc.)
├── color_manager.py         # Color utilities and theming
├── layout_manager.py        # Screen layout and positioning
└── visual_effects.py       # Shadows, highlights, transitions
```

## 🧩 Components to Extract

### 1. **3D Rendering Engine** (`renderer_3d.py`)
**Current Locations**: 
- `pyPSA_db.py`: Lines 258-315 (`Entity.redraw()`)
- `pyPSA_db.py`: Lines 317-338 (`Entity.draw()`)
- `constants.py`: Lines 218-249 (`create_trapezoid_points()`)
- `constants.py`: Lines 183-196 (`to_isometric()`, `darken_color()`, `lighten_color()`)

**Extracted Classes**:
- `Renderer3D`: Main 3D rendering engine
- `IsometricProjection`: Coordinate conversion utilities
- `TrapezoidRenderer`: 3D trapezoid/box shape rendering
- `ShadowRenderer`: Drop shadow effects

### 2. **UI Components** (`ui_components.py`)
**Current Locations**:
- `pyPSA_db.py`: Lines 192-216 (`Button` class)
- `pyPSA_db.py`: Lines 834-873 (`SelectionHighlight` class)
- `pyPSA_db.py`: Lines 876-1159 (`SidebarComponent` and `Sidebar` classes)
- `pyPSA_db.py`: Lines 818-832 (`draw_log_panel()`)

**Extracted Classes**:
- `Button`: Interactive button with hover states
- `Panel`: Generic panel container
- `SelectionHighlight`: Grid selection visualization
- `LogPanel`: Log message display
- `Sidebar`: Component sidebar container
- `Menu`: Main menu system

### 3. **Color Management** (`color_manager.py`)
**Current Locations**:
- `constants.py`: Lines 15-45 (All color constants)
- `constants.py`: Lines 183-190 (`darken_color()`, `lighten_color()`)

**Extracted Classes**:
- `ColorManager`: Central color management
- `Theme`: Color theme definitions
- `ColorUtils`: Color manipulation utilities

### 4. **Layout Manager** (`layout_manager.py`)
**Current Locations**:
- `constants.py`: Lines 1-13 (Screen dimensions)
- `constants.py`: Lines 54-82 (UI positioning constants)

**Extracted Classes**:
- `LayoutManager`: Screen layout calculations
- `Positioning`: Element positioning utilities
- `Dimensions`: Size and spacing management

## 🔄 Migration Strategy

### Phase 2A: 3D Rendering Engine
1. Create `Renderer3D` class with trapezoid rendering
2. Extract isometric projection utilities
3. Update Entity classes to use new renderer
4. Test rendering consistency

### Phase 2B: UI Components  
1. Extract `Button` and `Panel` base classes
2. Migrate `SelectionHighlight` and `LogPanel`
3. Refactor `Sidebar` and `Menu` systems
4. Test UI interactions

### Phase 2C: Color & Layout Management
1. Create centralized color management
2. Extract layout positioning logic
3. Implement theme support
4. Test visual consistency

## 🧪 Testing Strategy

### Graphics Tests
- **3D Rendering**: Trapezoid point generation, isometric conversion
- **Color Management**: Color manipulation, theme switching
- **UI Components**: Button interactions, panel layouts
- **Visual Effects**: Shadow rendering, highlight effects

### Integration Tests
- **Entity Rendering**: Entities use graphics module correctly
- **UI Interactions**: Components respond to events properly
- **Layout Responsiveness**: Elements position correctly at different resolutions

## 📊 Benefits Expected

### For Developers
- **Reusable Components**: UI elements can be used across different screens
- **Testable Graphics**: Isolated testing of visual components
- **Theme Support**: Easy color scheme changes
- **Performance**: Optimized rendering pipeline

### For Multi-Connection Architecture
- **Scalable UI**: Support for complex grid layouts
- **Visual Consistency**: Uniform appearance across all components  
- **Interactive Elements**: Enhanced user interaction capabilities
- **Real-time Updates**: Efficient visual updates for changing electrical states

## 🚀 Implementation Priority

1. **High Priority**: 3D Rendering (core visual engine)
2. **Medium Priority**: UI Components (user interaction)
3. **Low Priority**: Color/Layout Management (polish and maintainability)

This phase will complete the separation of concerns, making the codebase more maintainable and enabling rich visual features for the multi-connection electrical architecture.
