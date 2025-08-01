import pygame
import sqlite3
import json
from datetime import datetime

# Colors (matching pyPSA_db.py style)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)
CONFIG_BG = (93, 194, 237)  # Sky blue background
CONFIG_ITEM_BG = (60, 60, 60)  # Lighter gray for parameters
CONFIG_ITEM_HOVER = (80, 80, 80)  # Hover state
CONFIG_HIGHLIGHT = (0, 200, 0)  # Keep green highlight
PANEL_BG = (30, 30, 30)  # Dark panel background
COMPONENT_BG = (40, 40, 40)  # Darker gray for components
COMPONENT_HOVER = (55, 55, 55)  # Component hover state
VALUE_COLOR = (220, 220, 220)  # Lighter color for values
UNIT_COLOR = (160, 160, 160)  # Subtle color for units

# Screen settings
SCREEN_WIDTH = 1600  # Changed from 1050 to match pyPSA_db.py
SCREEN_HEIGHT = 900  # Changed from 750 to match pyPSA_db.py
CONFIG_ITEM_HEIGHT = 60
CONFIG_ITEM_PADDING = 15
CONFIG_SECTION_MARGIN = 40

# Button dimensions
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 180
BUTTON_MARGIN = 20

DEFAULT_CONFIGS = {
    "SUPPLIER": {
        "p_nom_mw": {
            "default": 1000.0,
            "min": 100.0,
            "max": 5000.0,
            "description": "Nominal Power Capacity",
            "units": "MW"
        },
        "v_nom_kv": {
            "default": 110.0,
            "min": 11.0,
            "max": 400.0,
            "description": "Nominal Voltage",
            "units": "kV"
        }
    },
    "INDUCTIVE_CONSUMER": {
        "p_demand_rate": {
            "default": 5.0,
            "min": 0.1,
            "max": 100.0,
            "description": "Power Demand",
            "units": "MW"
        },
        "power_factor": {
            "default": 0.8,
            "min": 0.5,
            "max": 0.95,
            "description": "Power Factor",
            "units": "pu"
        }
    },
    "CAPACITIVE_CONSUMER": {
        "p_demand_rate": {
            "default": 5.0,
            "min": 0.1,
            "max": 100.0,
            "description": "Power Demand",
            "units": "MW"
        },
        "power_factor": {
            "default": 0.9,
            "min": 0.85,
            "max": 1.0,
            "description": "Power Factor",
            "units": "pu"
        }
    },
    "RESISTIVE_CONSUMER": {
        "p_demand_rate": {
            "default": 5.0,
            "min": 0.1,
            "max": 100.0,
            "description": "Power Demand",
            "units": "MW"
        },
        "power_factor": {
            "default": 1.0,
            "min": 0.98,
            "max": 1.0,
            "description": "Power Factor",
            "units": "pu"
        }
    }
}

class ConfigChangeObserver:
    def on_config_change(self, change_type):
        pass

class ConfigurationManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.observers = []
        self.create_tables()
        self.load_configs()

    def create_tables(self):
        c = self.conn.cursor()
        
        # Component default configurations
        c.execute('''
            CREATE TABLE IF NOT EXISTS ComponentConfigs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_type TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                default_value REAL NOT NULL,
                min_value REAL,
                max_value REAL,
                description TEXT,
                units TEXT,
                UNIQUE(component_type, parameter_name)
            )
        ''')
        
        # User-defined configurations
        c.execute('''
            CREATE TABLE IF NOT EXISTS UserConfigs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_type TEXT NOT NULL,
                parameter_name TEXT NOT NULL,
                value REAL NOT NULL,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(component_type, parameter_name)
            )
        ''')
        
        # Saved instances
        c.execute('''
            CREATE TABLE IF NOT EXISTS SavedInstances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                component_type TEXT NOT NULL,
                parameters TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()

    def load_configs(self):
        """Load configurations from database, falling back to defaults if not found"""
        self.current_configs = {}
        c = self.conn.cursor()
        
        for component_type, params in DEFAULT_CONFIGS.items():
            self.current_configs[component_type] = {}
            for param_name, param_data in params.items():
                # Try to get user config
                c.execute('''
                    SELECT value FROM UserConfigs 
                    WHERE component_type = ? AND parameter_name = ?
                ''', (component_type, param_name))
                result = c.fetchone()
                
                if result:
                    self.current_configs[component_type][param_name] = result[0]
                else:
                    self.current_configs[component_type][param_name] = param_data['default']

    def add_observer(self, observer):
        """Add an observer to be notified of configuration changes"""
        self.observers.append(observer)

    def remove_observer(self, observer):
        """Remove an observer"""
        if observer in self.observers:
            self.observers.remove(observer)

    def notify_change(self, change_type):
        """Notify all observers of a configuration change"""
        for observer in self.observers:
            observer.on_config_change(change_type)

    def save_config(self, component_type, parameter_name, value):
        """Save user configuration to database"""
        param_data = DEFAULT_CONFIGS[component_type][parameter_name]
        if value < param_data['min'] or value > param_data['max']:
            return False, f"Value must be between {param_data['min']} and {param_data['max']} {param_data['units']}"
        
        c = self.conn.cursor()
        try:
            c.execute('''
                INSERT OR REPLACE INTO UserConfigs (component_type, parameter_name, value)
                VALUES (?, ?, ?)
            ''', (component_type, parameter_name, value))
            self.conn.commit()
            self.load_configs()
            return True, "Configuration saved successfully"
        except Exception as e:
            return False, f"Error saving configuration: {str(e)}"

    def save_instance(self, name, component_type, description=""):
        """Save current configuration as a named instance"""
        if not name:
            return False, "Name is required"
            
        parameters = self.current_configs[component_type]
        
        c = self.conn.cursor()
        try:
            c.execute('''
                INSERT INTO SavedInstances (name, description, component_type, parameters)
                VALUES (?, ?, ?, ?)
            ''', (name, description, component_type, json.dumps(parameters)))
            self.conn.commit()
            self.notify_change("instance_saved")
            return True, f"Saved instance '{name}' successfully"
        except sqlite3.IntegrityError:
            return False, f"An instance named '{name}' already exists"
        except Exception as e:
            return False, f"Error saving instance: {str(e)}"

    def get_saved_instances(self, component_type=None):
        """Get all saved instances, optionally filtered by component type"""
        c = self.conn.cursor()
        if component_type:
            c.execute('SELECT * FROM SavedInstances WHERE component_type = ?', (component_type,))
        else:
            c.execute('SELECT * FROM SavedInstances')
        return c.fetchall()

    def load_instance(self, instance_id):
        """Load a saved instance's parameters"""
        c = self.conn.cursor()
        c.execute('SELECT parameters FROM SavedInstances WHERE id = ?', (instance_id,))
        result = c.fetchone()
        if result:
            return json.loads(result[0])
        return None

    def delete_instance(self, instance_id):
        """Delete a saved instance"""
        c = self.conn.cursor()
        try:
            c.execute('DELETE FROM SavedInstances WHERE id = ?', (instance_id,))
            self.conn.commit()
            self.notify_change("instance_deleted")
            return True, "Instance deleted successfully"
        except Exception as e:
            return False, f"Error deleting instance: {str(e)}"

    def reset_to_default(self, component_type, parameter_name=None):
        """Reset specific or all parameters for a component type to defaults"""
        c = self.conn.cursor()
        if parameter_name:
            c.execute('''
                DELETE FROM UserConfigs 
                WHERE component_type = ? AND parameter_name = ?
            ''', (component_type, parameter_name))
        else:
            c.execute('DELETE FROM UserConfigs WHERE component_type = ?', (component_type,))
        self.conn.commit()
        self.load_configs()

class ConfigurationScreen:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.selected_component = None
        self.selected_parameter = None
        self.editing_value = None
        self.message = None
        self.message_timer = 0
        self.save_dialog = None
        self.active_tab = "Parameters"  # "Parameters" or "Instances"
        self.selected_instance = None
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 36)
        self.header_font = pygame.font.SysFont("Arial", 28)
        self.item_font = pygame.font.SysFont("Arial", 20)
        
        # Calculate positions for title and tabs
        title_y = 20  # Top margin
        title_height = 40  # Height for title area
        tabs_y = title_y + title_height + 20  # Space between title and tabs
        tab_width = 150  # Width for each tab
        tab_height = 40  # Height for tabs
        left_margin = 20  # Left margin for all elements
        
        # Tab buttons
        self.parameters_tab = pygame.Rect(
            left_margin,  # Left align with title
            tabs_y,
            tab_width,
            tab_height
        )
        
        self.instances_tab = pygame.Rect(
            self.parameters_tab.right + 10,  # 10px spacing between tabs
            tabs_y,
            tab_width,
            tab_height
        )
        
        # Action buttons - align with tabs
        self.save_as_button = pygame.Rect(
            SCREEN_WIDTH - 200 - 10,  # Right margin
            tabs_y,  # Align with tabs
            150,
            tab_height
        )
        
        self.reset_all_button = pygame.Rect(
            SCREEN_WIDTH - 350 - 20,  # Left of save button
            tabs_y,  # Align with tabs
            150,
            tab_height
        )
        
        # Main menu button - move to very bottom of screen
        self.main_menu_button = pygame.Rect(
            left_margin,
            SCREEN_HEIGHT - 50,  # Changed from 120 to 50 (moved down 70px to bottom)
            150,
            BUTTON_HEIGHT
        )

    def draw(self, surface):
        """Draw the configuration screen"""
        # First fill with solid color to prevent background bleed-through
        surface.fill(CONFIG_BG)
        
        # Try to load and draw background image
        try:
            background_image = pygame.image.load("assets/config_background.png")
            # Scale to fit screen exactly
            background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            surface.blit(background_image, (0, 0))
        except (pygame.error, FileNotFoundError):
            # Keep the solid color background if image not found
            pass
        
        # Draw title with shadow for better visibility over background
        title_shadow = self.title_font.render("Configuration", True, BLACK)
        surface.blit(title_shadow, (22, 22))  # Shadow offset
        title_surface = self.title_font.render("Configuration", True, WHITE)
        surface.blit(title_surface, (20, 20))  # Main title
        
        # Create semi-transparent content panel for better readability
        content_panel_rect = pygame.Rect(10, 60, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 180)
        panel_surface = pygame.Surface((content_panel_rect.width, content_panel_rect.height))
        panel_surface.set_alpha(180)  # Semi-transparent (70% opacity)
        panel_surface.fill(PANEL_BG)  # Dark background
        surface.blit(panel_surface, content_panel_rect.topleft)
        
        # Draw tabs
        for tab, rect, text in [
            ("Parameters", self.parameters_tab, "Parameters"),
            ("Instances", self.instances_tab, "Instances")
        ]:
            color = CONFIG_HIGHLIGHT if self.active_tab == tab else CONFIG_ITEM_BG
            pygame.draw.rect(surface, color, rect, border_radius=8)  # More rounded corners
            # Add white border like main menu
            pygame.draw.rect(surface, WHITE, rect, width=2, border_radius=8)
            text_surface = self.header_font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)
        
        # Draw action buttons - only show on Parameters tab
        if self.active_tab == "Parameters":
            pygame.draw.rect(surface, CONFIG_ITEM_BG, self.save_as_button, border_radius=8)  # More rounded corners
            # Add white border like main menu
            pygame.draw.rect(surface, WHITE, self.save_as_button, width=2, border_radius=8)
            save_text = self.item_font.render("Save As...", True, WHITE)
            save_rect = save_text.get_rect(center=self.save_as_button.center)
            surface.blit(save_text, save_rect)
            
            pygame.draw.rect(surface, CONFIG_ITEM_BG, self.reset_all_button, border_radius=8)  # More rounded corners
            # Add white border like main menu
            pygame.draw.rect(surface, WHITE, self.reset_all_button, width=2, border_radius=8)
            reset_text = self.item_font.render("Reset All", True, WHITE)
            reset_rect = reset_text.get_rect(center=self.reset_all_button.center)
            surface.blit(reset_text, reset_rect)
        
        # Draw content based on active tab
        content_start_y = self.parameters_tab.bottom + 20  # Start content below tabs
        
        if self.active_tab == "Parameters":
            # Draw component list with side-by-side parameters
            y = content_start_y
            for component_type in DEFAULT_CONFIGS:
                # Component section - compact width on the left
                component_width = 250
                item_height = CONFIG_ITEM_HEIGHT
                
                # Component background - only for the component name area
                component_rect = pygame.Rect(20, y, component_width, item_height)
                color = CONFIG_HIGHLIGHT if component_type == self.selected_component else COMPONENT_BG
                pygame.draw.rect(surface, color, component_rect, border_radius=8)  # More rounded corners
                
                # Component name with better styling
                name_surface = self.item_font.render(component_type.replace("_", " "), True, WHITE)
                surface.blit(name_surface, (30, y + (item_height - name_surface.get_height()) // 2))
                
                # Draw parameters side by side to the right of component (always show them)
                param_x = component_width + 30  # Start parameters after component with small gap
                param_width = 200  # Fixed width for each parameter
                
                for param_name, param_data in DEFAULT_CONFIGS[component_type].items():
                    param_rect = pygame.Rect(param_x, y, param_width, item_height)
                    param_color = CONFIG_HIGHLIGHT if (component_type == self.selected_component and param_name == self.selected_parameter) else CONFIG_ITEM_BG
                    pygame.draw.rect(surface, param_color, param_rect, border_radius=8)  # More rounded corners
                    
                    # Parameter name and value with improved typography
                    if component_type == self.selected_component and param_name == self.selected_parameter and self.editing_value is not None:
                        value_text = self.editing_value + "_"  # Show cursor
                        value_color = WHITE
                    else:
                        current_value = self.config_manager.current_configs[component_type][param_name]
                        value_text = f"{current_value:.2f}"
                        units_text = param_data['units']
                        value_color = VALUE_COLOR
                    
                    # Draw parameter name (smaller, subtle)
                    param_name_surface = self.item_font.render(param_name.replace("_", " "), True, WHITE)
                    surface.blit(param_name_surface, (param_x + 10, y + 8))
                    
                    # Draw parameter value and units with better styling
                    if component_type == self.selected_component and param_name == self.selected_parameter and self.editing_value is not None:
                        # Editing mode - show cursor
                        value_surface = self.item_font.render(value_text, True, WHITE)
                        surface.blit(value_surface, (param_x + 10, y + item_height - 25))
                    else:
                        # Normal mode - show value and units separately
                        value_surface = self.item_font.render(value_text, True, VALUE_COLOR)
                        units_surface = self.item_font.render(units_text, True, UNIT_COLOR)
                        
                        # Position value and units
                        value_width = value_surface.get_width()
                        surface.blit(value_surface, (param_x + 10, y + item_height - 25))
                        surface.blit(units_surface, (param_x + 15 + value_width, y + item_height - 25))
                    
                    param_x += param_width + 10  # Move to next parameter position
                
                y += item_height + CONFIG_ITEM_PADDING
        
        else:  # Instances tab
            # Draw saved instances list in table format
            y = content_start_y
            instances = self.config_manager.get_saved_instances()  # Add this missing line
            
            # Table headers - make table wider
            header_height = 30
            table_width = SCREEN_WIDTH - 20  # Use almost full screen width
            header_rect = pygame.Rect(10, y, table_width, header_height)
            pygame.draw.rect(surface, CONFIG_ITEM_HOVER, header_rect, border_radius=5)
            
            # Column widths - made much wider to prevent overlap
            name_col_width = 140
            type_col_width = 280  # Much wider for full type names
            desc_col_width = 180  # Increased for descriptions
            params_col_width = 480  # Much wider for parameter strings
            actions_col_width = 100
            
            # Draw column headers
            headers = [
                ("Name", 20, name_col_width),
                ("Type", 20 + name_col_width, type_col_width),
                ("Description", 20 + name_col_width + type_col_width, desc_col_width),
                ("Parameters", 20 + name_col_width + type_col_width + desc_col_width, params_col_width),
                ("Actions", 20 + name_col_width + type_col_width + desc_col_width + params_col_width, actions_col_width)
            ]
            
            for header_text, x_pos, col_width in headers:
                header_surface = self.item_font.render(header_text, True, WHITE)
                surface.blit(header_surface, (x_pos, y + 8))
                
                # Draw column separator lines
                if x_pos > 20:  # Don't draw line before first column
                    pygame.draw.line(surface, GREY, (x_pos - 5, y), (x_pos - 5, y + header_height), 1)
            
            y += header_height + 5
            
            if instances:
                for instance in instances:
                    # Row background - use wider table
                    row_rect = pygame.Rect(10, y, table_width, CONFIG_ITEM_HEIGHT)
                    color = CONFIG_HIGHLIGHT if instance == self.selected_instance else COMPONENT_BG
                    pygame.draw.rect(surface, color, row_rect, border_radius=5)
                    
                    # Instance name
                    name_text = instance[1][:16] + "..." if len(instance[1]) > 16 else instance[1]
                    name_surface = self.item_font.render(name_text, True, WHITE)
                    surface.blit(name_surface, (20, y + (CONFIG_ITEM_HEIGHT - name_surface.get_height()) // 2))
                    
                    # Component type - no truncation now
                    type_text = instance[3].replace("_", " ")
                    type_surface = self.item_font.render(type_text, True, GREY)
                    surface.blit(type_surface, (20 + name_col_width, y + (CONFIG_ITEM_HEIGHT - type_surface.get_height()) // 2))
                    
                    # Description
                    desc_text = instance[2] if instance[2] else "No description"
                    desc_text = desc_text[:22] + "..." if len(desc_text) > 22 else desc_text
                    desc_surface = self.item_font.render(desc_text, True, GREY)
                    surface.blit(desc_surface, (20 + name_col_width + type_col_width, y + (CONFIG_ITEM_HEIGHT - desc_surface.get_height()) // 2))
                    
                    # Parameters - show more parameters with wider column
                    try:
                        params = json.loads(instance[4])  # parameters column
                        param_text = ""
                        for key, value in params.items():  # Show all parameters
                            param_text += f"{key}: {value:.1f} "
                        param_text = param_text[:55] + "..." if len(param_text) > 55 else param_text
                    except:
                        param_text = "Invalid data"
                    
                    params_surface = self.item_font.render(param_text, True, GREY)
                    surface.blit(params_surface, (20 + name_col_width + type_col_width + desc_col_width, y + (CONFIG_ITEM_HEIGHT - params_surface.get_height()) // 2))
                    
                    # Actions (Delete button)
                    delete_button_rect = pygame.Rect(
                        20 + name_col_width + type_col_width + desc_col_width + params_col_width + 10,
                        y + (CONFIG_ITEM_HEIGHT - 25) // 2,
                        80,
                        25
                    )
                    button_color = RED if instance == self.selected_instance else CONFIG_ITEM_BG
                    pygame.draw.rect(surface, button_color, delete_button_rect, border_radius=3)
                    delete_text = self.item_font.render("Delete", True, WHITE)
                    delete_rect = delete_text.get_rect(center=delete_button_rect.center)
                    surface.blit(delete_text, delete_rect)
                    
                    # Draw column separator lines for data rows
                    for header_text, x_pos, col_width in headers[1:]:  # Skip first column
                        pygame.draw.line(surface, GREY, (x_pos - 5, y), (x_pos - 5, y + CONFIG_ITEM_HEIGHT), 1)
                    
                    y += CONFIG_ITEM_HEIGHT + 5
            else:
                # No instances message
                no_instances_rect = pygame.Rect(10, y, table_width, 60)
                pygame.draw.rect(surface, CONFIG_ITEM_BG, no_instances_rect, border_radius=5)
                text_surface = self.item_font.render("No saved instances", True, GREY)
                text_rect = text_surface.get_rect(center=no_instances_rect.center)
                surface.blit(text_surface, text_rect)
        
        # Draw Main Menu button
        pygame.draw.rect(surface, CONFIG_ITEM_BG, self.main_menu_button, border_radius=8)  # More rounded corners
        # Add white border like main menu
        pygame.draw.rect(surface, WHITE, self.main_menu_button, width=2, border_radius=8)
        menu_text = self.item_font.render("Main Menu", True, WHITE)
        menu_rect = menu_text.get_rect(center=self.main_menu_button.center)
        surface.blit(menu_text, menu_rect)
        
        # Draw save dialog if active
        if self.save_dialog:
            self.save_dialog.draw(surface)
        
        # Draw message if active (includes helpful parameter instructions)
        if self.message and self.message_timer > 0:
            msg_surface = self.item_font.render(self.message, True, WHITE)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(surface, PANEL_BG, bg_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, bg_rect, width=1, border_radius=8)
            surface.blit(msg_surface, msg_rect)

    def handle_event(self, event):
        """Handle events for the configuration screen"""
        # Handle save dialog events first if it's active
        if self.save_dialog:
            result = self.save_dialog.handle_event(event)
            if result:
                name, description = result
                if self.selected_component:
                    success, message = self.config_manager.save_instance(
                        name,
                        self.selected_component,
                        description
                    )
                    self.message = message
                    self.message_timer = 120
                self.save_dialog = None
            return
        
        # Handle mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Check tab clicks
                for tab, rect in [
                    ("Parameters", self.parameters_tab),
                    ("Instances", self.instances_tab)
                ]:
                    if rect.collidepoint(event.pos):
                        self.active_tab = tab
                        self.selected_component = None
                        self.selected_parameter = None
                        self.selected_instance = None
                        self.editing_value = None
                        return
                
                # Check main menu button
                if self.main_menu_button.collidepoint(event.pos):
                    return "menu"
                
                # Check Save As and Reset All buttons - only on Parameters tab
                if self.active_tab == "Parameters":
                    # Check Save As button
                    if self.save_as_button.collidepoint(event.pos):
                        if self.selected_component:
                            self.save_dialog = SaveInstanceDialog(
                                SCREEN_WIDTH // 2 - 200,
                                SCREEN_HEIGHT // 2 - 100
                            )
                        return
                    
                    # Check Reset All button
                    if self.reset_all_button.collidepoint(event.pos):
                        if self.selected_component:
                            self.config_manager.reset_to_default(self.selected_component)
                            self.message = "Reset all parameters to default values"
                            self.message_timer = 120
                        return
                
                content_start_y = self.parameters_tab.bottom + 20
                
                if self.active_tab == "Parameters":
                    # Check component list clicks
                    y = content_start_y
                    for component_type in DEFAULT_CONFIGS:
                        component_width = 250
                        item_height = CONFIG_ITEM_HEIGHT
                        
                        # Check component name click
                        component_rect = pygame.Rect(20, y, component_width, item_height)
                        if component_rect.collidepoint(event.pos):
                            self.selected_component = component_type
                            self.selected_parameter = None
                            self.editing_value = None
                            return
                        
                        # Check parameter clicks
                        param_x = component_width + 30
                        param_width = 200
                        
                        for param_name in DEFAULT_CONFIGS[component_type]:
                            param_rect = pygame.Rect(param_x, y, param_width, item_height)
                            if param_rect.collidepoint(event.pos):
                                self.selected_component = component_type
                                self.selected_parameter = param_name
                                current_value = self.config_manager.current_configs[component_type][param_name]
                                self.editing_value = str(current_value)
                                
                                # Show helpful message about parameter editing
                                param_data = DEFAULT_CONFIGS[component_type][param_name]
                                self.message = f"Type new value for {param_name.replace('_', ' ')} (Range: {param_data['min']:.1f} - {param_data['max']:.1f} {param_data['units']}). Press Enter to save."
                                self.message_timer = 300  # Show for 5 seconds
                                return
                            param_x += param_width + 10
                        
                        y += item_height + CONFIG_ITEM_PADDING
                
                else:  # Instances tab
                    # Check instance list clicks in table format
                    header_height = 30
                    y = content_start_y + header_height + 5  # Start after header
                    instances = self.config_manager.get_saved_instances()
                    
                    # Column widths (same as in draw method)
                    name_col_width = 140
                    type_col_width = 280  # Much wider for full type names
                    desc_col_width = 180  # Increased for descriptions
                    params_col_width = 480  # Much wider for parameter strings
                    actions_col_width = 100
                    
                    if instances:
                        for instance in instances:
                            # Check delete button click first (for any instance, not just selected)
                            delete_button_rect = pygame.Rect(
                                20 + name_col_width + type_col_width + desc_col_width + params_col_width + 10,
                                y + (CONFIG_ITEM_HEIGHT - 25) // 2,
                                80,
                                25
                            )
                            if delete_button_rect.collidepoint(event.pos):
                                success, message = self.config_manager.delete_instance(instance[0])
                                self.message = message
                                self.message_timer = 120
                                if success:
                                    self.selected_instance = None
                                return
                            
                            # Check row click (excluding delete button area)
                            table_width = SCREEN_WIDTH - 20
                            row_rect = pygame.Rect(10, y, table_width - actions_col_width, CONFIG_ITEM_HEIGHT)
                            if row_rect.collidepoint(event.pos):
                                self.selected_instance = instance
                                return
                            
                            y += CONFIG_ITEM_HEIGHT + 5
        
        # Handle key events for parameter editing
        elif event.type == pygame.KEYDOWN:
            if self.selected_component and self.selected_parameter:
                param_data = DEFAULT_CONFIGS[self.selected_component][self.selected_parameter]
                
                if self.editing_value is not None:
                    if event.key == pygame.K_RETURN:
                        try:
                            new_value = float(self.editing_value)
                            success, message = self.config_manager.save_config(
                                self.selected_component,
                                self.selected_parameter,
                                new_value
                            )
                            self.message = message
                            if success:
                                self.editing_value = None
                        except ValueError:
                            self.message = "Invalid number format"
                        self.message_timer = 120
                        return
                    
                    elif event.key == pygame.K_ESCAPE:
                        self.editing_value = None
                        return
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.editing_value = self.editing_value[:-1]
                        return
                    
                    elif event.unicode:
                        if event.unicode.isnumeric() or (event.unicode == '.' and '.' not in self.editing_value):
                            self.editing_value += event.unicode
                        return
                
                elif event.key == pygame.K_UP:
                    current_value = self.config_manager.current_configs[self.selected_component][self.selected_parameter]
                    value_range = param_data['max'] - param_data['min']
                    new_value = min(current_value + value_range * 0.1, param_data['max'])
                    success, message = self.config_manager.save_config(
                        self.selected_component,
                        self.selected_parameter,
                        new_value
                    )
                    if success:
                        self.message = f"Updated {self.selected_parameter} to {new_value:.2f}"
                    else:
                        self.message = message
                    self.message_timer = 120
                
                elif event.key == pygame.K_DOWN:
                    current_value = self.config_manager.current_configs[self.selected_component][self.selected_parameter]
                    value_range = param_data['max'] - param_data['min']
                    new_value = max(current_value - value_range * 0.1, param_data['min'])
                    success, message = self.config_manager.save_config(
                        self.selected_component,
                        self.selected_parameter,
                        new_value
                    )
                    if success:
                        self.message = f"Updated {self.selected_parameter} to {new_value:.2f}"
                    else:
                        self.message = message
                    self.message_timer = 120
                
                elif event.key == pygame.K_r:
                    self.config_manager.reset_to_default(self.selected_component, self.selected_parameter)
                    self.message = f"Reset {self.selected_parameter} to default value"
                    self.message_timer = 120
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0:
                self.message = None

class SaveInstanceDialog:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 400, 200)
        self.name_input = ""
        self.description_input = ""
        self.active_input = "name"  # "name" or "description"
        self.font = pygame.font.SysFont("Arial", 20)
    
    def draw(self, surface):
        # Draw dialog background
        pygame.draw.rect(surface, CONFIG_BG, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=5)
        
        # Draw title
        title_surface = self.font.render("Save Instance", True, WHITE)
        surface.blit(title_surface, (self.rect.x + 20, self.rect.y + 20))
        
        # Draw name input
        name_label = self.font.render("Name:", True, WHITE)
        surface.blit(name_label, (self.rect.x + 20, self.rect.y + 60))
        
        name_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 85, 360, 30)
        color = CONFIG_HIGHLIGHT if self.active_input == "name" else CONFIG_ITEM_BG
        pygame.draw.rect(surface, color, name_rect, border_radius=3)
        name_surface = self.font.render(self.name_input + ("_" if self.active_input == "name" else ""), True, WHITE)
        surface.blit(name_surface, (name_rect.x + 5, name_rect.y + 5))
        
        # Draw description input
        desc_label = self.font.render("Description (optional):", True, WHITE)
        surface.blit(desc_label, (self.rect.x + 20, self.rect.y + 120))
        
        desc_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 145, 360, 30)
        color = CONFIG_HIGHLIGHT if self.active_input == "description" else CONFIG_ITEM_BG
        pygame.draw.rect(surface, color, desc_rect, border_radius=3)
        desc_surface = self.font.render(self.description_input + ("_" if self.active_input == "description" else ""), True, WHITE)
        surface.blit(desc_surface, (desc_rect.x + 5, desc_rect.y + 5))
    
    def handle_event(self, event):
        """Handle events for the save dialog. Returns (name, description) tuple if save confirmed."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Check name input click
                name_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 85, 360, 30)
                if name_rect.collidepoint(event.pos):
                    self.active_input = "name"
                    return None
                
                # Check description input click
                desc_rect = pygame.Rect(self.rect.x + 20, self.rect.y + 145, 360, 30)
                if desc_rect.collidepoint(event.pos):
                    self.active_input = "description"
                    return None
                
                # Click outside dialog cancels
                if not self.rect.collidepoint(event.pos):
                    return None
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.name_input:  # Only save if name is not empty
                    return (self.name_input, self.description_input)
                return None
            
            elif event.key == pygame.K_ESCAPE:
                return None
            
            elif event.key == pygame.K_TAB:
                self.active_input = "description" if self.active_input == "name" else "name"
            
            elif event.key == pygame.K_BACKSPACE:
                if self.active_input == "name":
                    self.name_input = self.name_input[:-1]
                else:
                    self.description_input = self.description_input[:-1]
            
            elif event.unicode and event.unicode.isprintable():
                if self.active_input == "name":
                    if len(self.name_input) < 30:  # Limit name length
                        self.name_input += event.unicode
                else:
                    if len(self.description_input) < 100:  # Limit description length
                        self.description_input += event.unicode
        
        return None 