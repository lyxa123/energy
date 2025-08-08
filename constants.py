# Constants file - centralized configuration for the entire application

import pygame
import math

# === SCREEN DIMENSIONS ===
SIDEBAR_WIDTH = 250
MAIN_AREA_WIDTH = 1350
SCREEN_WIDTH = MAIN_AREA_WIDTH + SIDEBAR_WIDTH  # 1600
SCREEN_HEIGHT = 900
MAIN_AREA_WIDTH = 1350
SIDEBAR_WIDTH = 250
FPS = 60

# === COLORS ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)
YELLOW = (255, 255, 0)

# UI Colors
LOG_PANEL_BG = (30, 30, 30)
LOG_TEXT_COLOR = (220, 220, 220)
ENTITY_LABEL_COLOR = BLACK
MENU_BG = (50, 50, 50)
MENU_TEXT = (220, 220, 220)
HELP_BG = (40, 40, 40)
CONFIG_BG = (93, 194, 237)
CONFIG_ITEM_BG = (60, 60, 60)
CONFIG_ITEM_HOVER = (80, 80, 80)
CONFIG_HIGHLIGHT = (0, 200, 0)
PANEL_BG = (30, 30, 30)
COMPONENT_BG = (40, 40, 40)
COMPONENT_HOVER = (55, 55, 55)
VALUE_COLOR = (220, 220, 220)
UNIT_COLOR = (160, 160, 160)

# Sidebar Colors
SIDEBAR_BG = (45, 45, 45)
SIDEBAR_ITEM_BG = (60, 60, 60)
SIDEBAR_ITEM_HOVER = (75, 75, 75)
SIDEBAR_TEXT = (220, 220, 220)
SIDEBAR_SHADOW_COLOR = (0, 0, 0)

# === MENU SETTINGS ===
MENU_HEIGHT = 40
MENU_TITLE_SIZE = 48
MENU_ITEM_SIZE = 36
MENU_START_Y = SCREEN_HEIGHT // 3
MENU_SPACING = 80
MENU_BUTTON_WIDTH = 300
MENU_BUTTON_HEIGHT = 60

# === BUTTON SETTINGS ===
BUTTON_SIZE = 30
BUTTON_PADDING = 10
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 180
BUTTON_MARGIN = 20
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = WHITE

# === ENTITY SETTINGS ===
SUPPLIER_SIZE = 60
CONSUMER_SIZE = 45
CONNECTION_COLOR = GREY
CONNECTION_THICKNESS = 3
ENTITY_FONT_SIZE = 16

# === 3D ISOMETRIC SETTINGS ===
CUBE_SIZE = 64
TILE_WIDTH = CUBE_SIZE
TILE_HEIGHT = int(CUBE_SIZE * math.sin(math.radians(30)))
TILE_DEPTH = CUBE_SIZE
CONNECTION_OFFSET = 16

# === SIDEBAR SETTINGS ===
SIDEBAR_ANIMATION_SPEED = 15
SIDEBAR_SHADOW_WIDTH = 10
SIDEBAR_SHADOW_ALPHA = 128
SIDEBAR_ITEM_HEIGHT = 80
SIDEBAR_ITEM_PADDING = 20
SIDEBAR_ITEM_MARGIN = 10
SIDEBAR_TITLE_HEIGHT = 50
SIDEBAR_ITEM_WIDTH = SIDEBAR_WIDTH - (2 * SIDEBAR_ITEM_PADDING)

# === LOG PANEL SETTINGS ===
LOG_PANEL_HEIGHT = 150
MAX_LOG_MESSAGES = 8

# === CONFIG SCREEN SETTINGS ===
CONFIG_ITEM_HEIGHT = 60
CONFIG_ITEM_PADDING = 15
CONFIG_SECTION_MARGIN = 40

# === PYPSA SIMULATION SETTINGS ===
SIM_STEP_INTERVAL = 1
DEFAULT_SUPPLIER_P_GENERATION = 20
DEFAULT_SUPPLIER_Q_CAPABILITY = 15
DEFAULT_SUPPLIER_P_CAPACITY = 1000
SUPPLIER_LOW_THRESHOLD_PERCENT = 0.2

# Consumer Settings
DEFAULT_CONSUMER_P_DEMAND = 5
CONSUMER_TYPE_INDUCTIVE = "inductive"
CONSUMER_TYPE_CAPACITIVE = "capacitive"
CONSUMER_TYPE_RESISTIVE = "resistive"

DEFAULT_INDUCTIVE_PF = 0.8
DEFAULT_CAPACITIVE_PF = 0.9
DEFAULT_RESISTIVE_PF = 1.0

# === COMPONENT TYPES ===
COMPONENT_TYPES = {
    "DEFAULT_COMPONENTS": {
        "label": "▼",
        "description": "Default",
        "icon_color": WHITE,
        "is_section": True
    },
    "SUPPLIER": {
        "label": "S",
        "description": "Power Supplier",
        "icon_color": GREEN,
        "is_section": False
    },
    "INDUCTIVE_CONSUMER": {
        "label": "CI",
        "description": "Inductive Load",
        "icon_color": BLUE,
        "is_section": False
    },
    "CAPACITIVE_CONSUMER": {
        "label": "CC",
        "description": "Capacitive Load",
        "icon_color": BLUE,
        "is_section": False
    },
    "RESISTIVE_CONSUMER": {
        "label": "CR",
        "description": "Resistive Load",
        "icon_color": BLUE,
        "is_section": False
    },
    "SAVED_INSTANCES": {
        "label": "▼",
        "description": "Saved",
        "icon_color": YELLOW,
        "is_section": True
    }
}

# === HELP TEXT ===
HELP_TEXT = """
Energy City Simulator Help:

Controls:
- Left Click on Grid: Select placement area
- Click Component: Place selected component at highlighted area
- Shift + Left Click: Select consumer to connect
- Left Click on Supplier: Complete connection
- Left Click Empty Space: Cancel connection
- ESC: Cancel selection or connection

Colors:
- Green: Normal operation
- Yellow: Warning (voltage/loading)
- Red: Critical (low voltage/overload)
- Blue: Unconnected consumer
- White: Selected placement area

Status:
- Check log panel for power flow info
- Voltage levels shown in real-time
- Connection status displayed
"""

# === UTILITY FUNCTIONS ===
def darken_color(color, factor=0.7):
    """Darken a color by a given factor"""
    return tuple(int(c * factor) for c in color)

def lighten_color(color, factor=1.3):
    """Lighten a color by a given factor"""
    return tuple(min(255, int(c * factor)) for c in color)

def to_isometric(grid_x, grid_y):
    """Convert grid coordinates to isometric screen coordinates"""
    iso_x = (grid_x - grid_y) * TILE_WIDTH
    iso_y = (grid_x + grid_y) * TILE_HEIGHT
    return iso_x, iso_y

# === PYGAME RECTS (computed once) ===
def get_menu_rect():
    return pygame.Rect(0, 0, SCREEN_WIDTH, MENU_HEIGHT)

def get_help_button_rect():
    return pygame.Rect(SCREEN_WIDTH - 100, 5, 90, 30)

def get_log_panel_rect():
    return pygame.Rect(0, SCREEN_HEIGHT - LOG_PANEL_HEIGHT, SCREEN_WIDTH, LOG_PANEL_HEIGHT)
