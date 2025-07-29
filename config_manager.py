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
CONFIG_BG = (40, 40, 40)
CONFIG_ITEM_BG = (60, 60, 60)
CONFIG_ITEM_HOVER = (75, 75, 75)
CONFIG_HIGHLIGHT = (0, 200, 0)

# Screen settings
SCREEN_WIDTH = 1050
SCREEN_HEIGHT = 750
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
        
        # Tab buttons
        tab_width = 150  # Reduced width
        self.parameters_tab = pygame.Rect(
            20,  # Left margin
            20,  # Top margin
            tab_width,
            40   # Height
        )
        
        self.instances_tab = pygame.Rect(
            self.parameters_tab.right + 10,  # Next to Parameters tab
            20,  # Same top margin as Parameters tab
            tab_width,
            40
        )
        
        # Action buttons
        self.save_as_button = pygame.Rect(
            SCREEN_WIDTH - 400,  # Further left to avoid overlap
            20,                  # Top margin
            150,                 # Slightly smaller width
            BUTTON_HEIGHT
        )
        
        self.reset_all_button = pygame.Rect(
            SCREEN_WIDTH - 200,  # Position on right side
            20,                  # Top margin
            150,                 # Slightly smaller width
            BUTTON_HEIGHT
        )
        
        # Instance action buttons
        self.delete_instance_button = pygame.Rect(
            SCREEN_WIDTH - 200,  # Right side
            80,                  # Below top buttons
            150,                 # Match other button widths
            BUTTON_HEIGHT
        )
        
        # Main menu button
        self.main_menu_button = pygame.Rect(
            20,  # Left side
            SCREEN_HEIGHT - 60,  # Bottom margin
            150,  # Match other button widths
            BUTTON_HEIGHT
        )

    def draw(self, surface):
        """Draw the configuration screen"""
        # Draw background
        surface.fill(CONFIG_BG)
        
        # Draw title
        title_surface = self.title_font.render("Configuration", True, WHITE)
        title_x = (SCREEN_WIDTH - title_surface.get_width()) // 2
        surface.blit(title_surface, (title_x, 20))
        
        # Draw tabs
        for tab, rect, text in [
            ("Parameters", self.parameters_tab, "Parameters"),
            ("Instances", self.instances_tab, "Instances")
        ]:
            color = CONFIG_HIGHLIGHT if self.active_tab == tab else GREY
            pygame.draw.rect(surface, color, rect, border_radius=5)
            text_surface = self.header_font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)
        
        if self.active_tab == "Parameters":
            # Draw component list
            y = 100
            for component_type in DEFAULT_CONFIGS:
                item_rect = pygame.Rect(20, y, 300, CONFIG_ITEM_HEIGHT)
                color = CONFIG_HIGHLIGHT if component_type == self.selected_component else CONFIG_ITEM_BG
                pygame.draw.rect(surface, color, item_rect, border_radius=5)
                
                text_surface = self.item_font.render(component_type.replace("_", " "), True, WHITE)
                surface.blit(text_surface, (30, y + (CONFIG_ITEM_HEIGHT - text_surface.get_height()) // 2))
                
                y += CONFIG_ITEM_HEIGHT + CONFIG_ITEM_PADDING
            
            # Draw parameter list if component selected
            if self.selected_component:
                y = 100
                x = 340  # Start parameters list to the right of components
                for param_name, param_data in DEFAULT_CONFIGS[self.selected_component].items():
                    item_rect = pygame.Rect(x, y, 400, CONFIG_ITEM_HEIGHT)
                    color = CONFIG_HIGHLIGHT if param_name == self.selected_parameter else CONFIG_ITEM_BG
                    pygame.draw.rect(surface, color, item_rect, border_radius=5)
                    
                    # Parameter name
                    name_surface = self.item_font.render(param_name.replace("_", " "), True, WHITE)
                    surface.blit(name_surface, (x + 10, y + 10))
                    
                    # Parameter value
                    if param_name == self.selected_parameter and self.editing_value is not None:
                        # Show editing value with cursor
                        value_text = self.editing_value + "_"
                    else:
                        current_value = self.config_manager.current_configs[self.selected_component][param_name]
                        value_text = f"{current_value:.2f} {param_data['units']}"
                    
                    value_surface = self.item_font.render(value_text, True, GREY)
                    surface.blit(value_surface, (x + 10, y + CONFIG_ITEM_HEIGHT - 30))
                    
                    # Show min/max if parameter selected
                    if param_name == self.selected_parameter:
                        range_text = f"Range: {param_data['min']:.1f} - {param_data['max']:.1f} {param_data['units']}"
                        range_surface = self.item_font.render(range_text, True, GREY)
                        surface.blit(range_surface, (x + 200, y + CONFIG_ITEM_HEIGHT - 30))
                    
                    y += CONFIG_ITEM_HEIGHT + CONFIG_ITEM_PADDING
            
            # Draw Save As and Reset All buttons
            pygame.draw.rect(surface, CONFIG_ITEM_BG, self.save_as_button, border_radius=5)
            save_text = self.item_font.render("Save As...", True, WHITE)
            save_rect = save_text.get_rect(center=self.save_as_button.center)
            surface.blit(save_text, save_rect)
            
            pygame.draw.rect(surface, CONFIG_ITEM_BG, self.reset_all_button, border_radius=5)
            reset_text = self.item_font.render("Reset All", True, WHITE)
            reset_rect = reset_text.get_rect(center=self.reset_all_button.center)
            surface.blit(reset_text, reset_rect)
        
        else:  # Instances tab
            # Draw saved instances list
            y = 100
            instances = self.config_manager.get_saved_instances()
            if instances:
                for instance in instances:
                    # Create instance rectangle that's slightly smaller to accommodate delete button
                    item_rect = pygame.Rect(20, y, SCREEN_WIDTH - 200, CONFIG_ITEM_HEIGHT)
                    color = CONFIG_HIGHLIGHT if instance == self.selected_instance else CONFIG_ITEM_BG
                    pygame.draw.rect(surface, color, item_rect, border_radius=5)
                    
                    # Instance name
                    name_surface = self.item_font.render(instance[1], True, WHITE)  # name column
                    surface.blit(name_surface, (30, y + 10))
                    
                    # Instance type and description
                    type_text = instance[3].replace("_", " ")  # component_type column
                    if instance[2]:  # description column
                        type_text += f" - {instance[2]}"
                    type_surface = self.item_font.render(type_text, True, GREY)
                    surface.blit(type_surface, (30, y + CONFIG_ITEM_HEIGHT - 30))
                    
                    # Draw Delete button if this instance is selected
                    if instance == self.selected_instance:
                        delete_button_rect = pygame.Rect(
                            SCREEN_WIDTH - 180,  # Position to the right of instance
                            y + (CONFIG_ITEM_HEIGHT - BUTTON_HEIGHT) // 2,  # Center vertically
                            150,  # Width
                            BUTTON_HEIGHT  # Height
                        )
                        pygame.draw.rect(surface, CONFIG_ITEM_BG, delete_button_rect, border_radius=5)
                        delete_text = self.item_font.render("Delete", True, WHITE)
                        delete_rect = delete_text.get_rect(center=delete_button_rect.center)
                        surface.blit(delete_text, delete_rect)
                    
                    y += CONFIG_ITEM_HEIGHT + CONFIG_ITEM_PADDING
            else:
                text_surface = self.item_font.render("No saved instances", True, GREY)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 150))
                surface.blit(text_surface, text_rect)
        
        # Draw Main Menu button
        pygame.draw.rect(surface, CONFIG_ITEM_BG, self.main_menu_button, border_radius=5)
        menu_text = self.item_font.render("Main Menu", True, WHITE)
        menu_rect = menu_text.get_rect(center=self.main_menu_button.center)
        surface.blit(menu_text, menu_rect)
        
        # Draw save dialog if active
        if self.save_dialog:
            self.save_dialog.draw(surface)
        
        # Draw message if active
        if self.message and self.message_timer > 0:
            msg_surface = self.item_font.render(self.message, True, WHITE)
            msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40))
            bg_rect = msg_rect.inflate(20, 10)
            pygame.draw.rect(surface, CONFIG_ITEM_BG, bg_rect, border_radius=5)
            surface.blit(msg_surface, msg_rect)

    def handle_event(self, event):
        """Handle events for the configuration screen"""
        # Handle save dialog events first if it's active
        if self.save_dialog:
            result = self.save_dialog.handle_event(event)
            if result:
                name, description = result
                if self.selected_component:  # Changed condition to only require selected_component
                    success, message = self.config_manager.save_instance(
                        name,
                        self.selected_component,
                        description
                    )
                    self.message = message
                    self.message_timer = 120  # Show message for 2 seconds
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
                        self.editing_value = None  # Reset editing state
                        return
                
                # Check main menu button
                if self.main_menu_button.collidepoint(event.pos):
                    return "menu"
                
                if self.active_tab == "Parameters":
                    # Check component list clicks
                    y = 100
                    for component_type in DEFAULT_CONFIGS:
                        item_rect = pygame.Rect(20, y, 300, CONFIG_ITEM_HEIGHT)
                        if item_rect.collidepoint(event.pos):
                            self.selected_component = component_type
                            self.selected_parameter = None
                            self.editing_value = None  # Reset editing state
                            return
                        y += CONFIG_ITEM_HEIGHT + CONFIG_ITEM_PADDING
                    
                    # Check parameter list clicks if component selected
                    if self.selected_component:
                        y = 100
                        x = 340
                        for param_name in DEFAULT_CONFIGS[self.selected_component]:
                            item_rect = pygame.Rect(x, y, 400, CONFIG_ITEM_HEIGHT)
                            if item_rect.collidepoint(event.pos):
                                self.selected_parameter = param_name
                                # Start editing when clicking parameter
                                current_value = self.config_manager.current_configs[self.selected_component][param_name]
                                self.editing_value = str(current_value)
                                return
                            y += CONFIG_ITEM_HEIGHT + CONFIG_ITEM_PADDING
                    
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
                
                else:  # Instances tab
                    # Check instance list clicks
                    y = 100
                    instances = self.config_manager.get_saved_instances()
                    if instances:
                        for instance in instances:
                            # Instance rectangle
                            item_rect = pygame.Rect(20, y, SCREEN_WIDTH - 200, CONFIG_ITEM_HEIGHT)
                            if item_rect.collidepoint(event.pos):
                                self.selected_instance = instance
                                return
                            
                            # Delete button for selected instance
                            if instance == self.selected_instance:
                                delete_button_rect = pygame.Rect(
                                    SCREEN_WIDTH - 180,
                                    y + (CONFIG_ITEM_HEIGHT - BUTTON_HEIGHT) // 2,
                                    150,
                                    BUTTON_HEIGHT
                                )
                                if delete_button_rect.collidepoint(event.pos):
                                    success, message = self.config_manager.delete_instance(instance[0])
                                    self.message = message
                                    self.message_timer = 120
                                    if success:
                                        self.selected_instance = None
                                    return
                            
                            y += CONFIG_ITEM_HEIGHT + CONFIG_ITEM_PADDING
        
        # Handle key events for parameter editing
        elif event.type == pygame.KEYDOWN:
            if self.selected_component and self.selected_parameter:
                param_data = DEFAULT_CONFIGS[self.selected_component][self.selected_parameter]
                
                if self.editing_value is not None:
                    if event.key == pygame.K_RETURN:
                        # Try to save the edited value
                        try:
                            new_value = float(self.editing_value)
                            success, message = self.config_manager.save_config(
                                self.selected_component,
                                self.selected_parameter,
                                new_value
                            )
                            self.message = message
                            if success:
                                self.editing_value = None  # Exit editing mode
                        except ValueError:
                            self.message = "Invalid number format"
                        self.message_timer = 120
                        return
                    
                    elif event.key == pygame.K_ESCAPE:
                        self.editing_value = None  # Cancel editing
                        return
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.editing_value = self.editing_value[:-1]
                        return
                    
                    elif event.unicode:
                        # Allow only numbers and decimal point
                        if event.unicode.isnumeric() or (event.unicode == '.' and '.' not in self.editing_value):
                            self.editing_value += event.unicode
                        return
                
                # Handle up/down arrows and reset key when not editing
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