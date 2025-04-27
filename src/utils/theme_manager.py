import os
import json
from typing import Dict, Any, Optional, Tuple, List
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication
from .settings import Settings
from config import Icon

class ThemeManager(QObject):
    """
    Manager for application themes with support for custom themes and component-specific styling
    """
    _instance = None
    _initialized = False
    
    # 主题变更信号
    theme_changed = pyqtSignal(str)
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, parent=None):
        """Initialize theme manager"""
        super().__init__(parent)
        if ThemeManager._initialized:
            return
            
        self.themes = {}
        self.default_theme = "light"
        self.current_theme = self.default_theme
        self.themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "themes")
        self.settings = Settings()
        self.current_theme = self.settings.settings.value("theme", self.default_theme)
        
        # Load all available themes
        self._load_all_themes()
        
        # Apply current theme
        self.apply_theme(self.current_theme)
        
        ThemeManager._initialized = True
    
    def _load_all_themes(self) -> None:
        """Load all theme files from the themes directory"""
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir, exist_ok=True)
            self._create_default_themes()
            
        # Load all .json files from the themes directory
        for file in os.listdir(self.themes_dir):
            if file.endswith('.json'):
                theme_name = os.path.splitext(file)[0]
                theme_path = os.path.join(self.themes_dir, file)
                self._load_theme(theme_name, theme_path)
    
    def _load_theme(self, theme_name: str, theme_path: str) -> bool:
        """Load a single theme from a file"""
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                
            # Validate theme structure
            if not self._validate_theme(theme_data):
                print(f"Warning: Theme '{theme_name}' has invalid structure and was not loaded")
                return False
                
            # Store the theme
            self.themes[theme_name] = theme_data
            return True
        except Exception as e:
            print(f"Error loading theme '{theme_name}': {str(e)}")
            return False
    
    def _validate_theme(self, theme_data: Dict[str, Any]) -> bool:
        """Validate theme data structure"""
        # 支持新的主题格式 (style字符串格式) 和旧的主题格式 (colors字典格式)
        if "style" in theme_data:
            # 新的主题格式 - 只需要名称和样式
            return "name" in theme_data
        else:
            # 旧的主题格式 - 需要名称和颜色
            required_fields = ["name", "colors"]
            required_colors = ["bg_color", "text_color", "accent_color"]
            
            # Check for required fields
            for field in required_fields:
                if field not in theme_data:
                    return False
            
            # Check for required colors
            if not all(color in theme_data["colors"] for color in required_colors):
                return False
                
            return True
    
    def _create_default_themes(self) -> None:
        """Create default theme files if they don't exist"""
        default_themes = {
            "dark": {
                "name": "dark",
                "display_name": {
                    "en": "Dark",
                    "zh": "深色"
                },
                "colors": {
                    "bg_color": "#1e1e1e",
                    "text_color": "#e0e0e0",
                    "accent_color": "#555555",
                    "bg_lighter": "#252525",
                    "bg_darker": "#1a1a1a"
                },
                "component_specific": {
                    "button": {
                        "primary_bg": "#555555",
                        "primary_text": "#ffffff",
                        "primary_hover": "#666666",
                        "primary_pressed": "#444444"
                    },
                    "progressbar": {
                        "chunk_color": "#555555"
                    }
                }
            },
            "light": {
                "name": "light",
                "display_name": {
                    "en": "Light",
                    "zh": "浅色"
                },
                "colors": {
                    "bg_color": "#f0f0f0",
                    "text_color": "#333333",
                    "accent_color": "#777777",
                    "bg_lighter": "#f5f5f5",
                    "bg_darker": "#e0e0e0"
                },
                "component_specific": {
                    "button": {
                        "primary_bg": "#777777",
                        "primary_text": "#ffffff",
                        "primary_hover": "#888888",
                        "primary_pressed": "#666666"
                    },
                    "progressbar": {
                        "chunk_color": "#777777"
                    }
                }
            },
            "blue": {
                "name": "blue",
                "display_name": {
                    "en": "Blue",
                    "zh": "蓝色"
                },
                "colors": {
                    "bg_color": "#0d1117",
                    "text_color": "#e6edf3",
                    "accent_color": "#58a6ff",
                    "bg_lighter": "#161b22",
                    "bg_darker": "#0a0d12"
                },
                "component_specific": {
                    "button": {
                        "primary_bg": "#58a6ff",
                        "primary_text": "#ffffff",
                        "primary_hover": "#6cb6ff",
                        "primary_pressed": "#4896ef"
                    },
                    "progressbar": {
                        "chunk_color": "#58a6ff"
                    }
                }
            },
            "green": {
                "name": "green",
                "display_name": {
                    "en": "Green",
                    "zh": "绿色"
                },
                "colors": {
                    "bg_color": "#0f1610",
                    "text_color": "#e6edf3",
                    "accent_color": "#4caf50",
                    "bg_lighter": "#151c16",
                    "bg_darker": "#0a0f0b"
                },
                "component_specific": {
                    "button": {
                        "primary_bg": "#4caf50",
                        "primary_text": "#ffffff",
                        "primary_hover": "#5cbf60",
                        "primary_pressed": "#3d9f40"
                    },
                    "progressbar": {
                        "chunk_color": "#4caf50"
                    }
                }
            },
            "purple": {
                "name": "purple",
                "display_name": {
                    "en": "Purple",
                    "zh": "紫色"
                },
                "colors": {
                    "bg_color": "#13111d",
                    "text_color": "#e6edf3",
                    "accent_color": "#9c27b0",
                    "bg_lighter": "#1b1825",
                    "bg_darker": "#0f0d18"
                },
                "component_specific": {
                    "button": {
                        "primary_bg": "#9c27b0",
                        "primary_text": "#ffffff",
                        "primary_hover": "#ac37c0",
                        "primary_pressed": "#8c17a0"
                    },
                    "progressbar": {
                        "chunk_color": "#9c27b0"
                    }
                }
            },
            "custom": {
                "name": "custom",
                "display_name": {
                    "en": "Custom",
                    "zh": "自定义"
                },
                "colors": {
                    "bg_color": "#1e1e1e",
                    "text_color": "#e0e0e0",
                    "accent_color": "#555555",
                    "bg_lighter": "#252525",
                    "bg_darker": "#1a1a1a"
                },
                "component_specific": {
                    "button": {
                        "primary_bg": "#555555",
                        "primary_text": "#ffffff",
                        "primary_hover": "#666666",
                        "primary_pressed": "#444444"
                    },
                    "progressbar": {
                        "chunk_color": "#555555"
                    }
                }
            }
        }
        
        # Create theme files
        for name, data in default_themes.items():
            theme_path = os.path.join(self.themes_dir, f"{name}.json")
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
    
    def get_theme_names(self):
        """获取所有主题名称列表"""
        return list(self.themes.keys())
        
    def get_theme_display_names(self, language="en"):
        """获取主题的显示名称"""
        display_names = {}
        for theme_name, theme_data in self.themes.items():
            if "name" in theme_data:
                display_names[theme_name] = theme_data["name"]
            else:
                # 如果没有名称，使用主题名的首字母大写版本
                display_names[theme_name] = theme_name.capitalize()
        return display_names
    
    def set_current_theme(self, theme_name: str) -> bool:
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.settings.settings.setValue("theme", theme_name)
            self.theme_changed.emit(theme_name)
            return True
        return False
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self.current_theme
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get color values for the specified theme"""
        theme = theme_name or self.current_theme
        
        # If theme doesn't exist, use default
        if theme not in self.themes:
            theme = self.default_theme
        
        if theme in self.themes and "colors" in self.themes[theme]:
            return self.themes[theme]["colors"]
        
        # Return default colors if theme not found
        return {
            "bg_color": "#1e1e1e",
            "text_color": "#e0e0e0",
            "accent_color": "#555555",
            "bg_lighter": "#252525",
            "bg_darker": "#1a1a1a"
        }
    
    def get_component_colors(self, component: str, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get component-specific colors for the specified theme"""
        theme = theme_name or self.current_theme
        
        # If theme doesn't exist, use default
        if theme not in self.themes:
            theme = self.default_theme
            
        theme_data = self.themes[theme]
        
        if "component_specific" in theme_data and component in theme_data["component_specific"]:
            return theme_data["component_specific"][component]
        
        # Return empty dict if component settings not found
        return {}
    
    def update_custom_theme(self, colors: Dict[str, str]) -> None:
        """Update the custom theme with new colors"""
        if "custom" not in self.themes:
            self.themes["custom"] = {
                "name": "custom",
                "display_name": {
                    "en": "Custom",
                    "zh": "自定义"
                },
                "colors": {},
                "component_specific": {}
            }
        
        # Update colors
        self.themes["custom"]["colors"].update(colors)
        
        # Generate lighter and darker variants if not provided
        if "bg_lighter" not in colors and "bg_color" in colors:
            self.themes["custom"]["colors"]["bg_lighter"] = self.lighten_color(colors["bg_color"], 10)
        
        if "bg_darker" not in colors and "bg_color" in colors:
            self.themes["custom"]["colors"]["bg_darker"] = self.lighten_color(colors["bg_color"], -10)
        
        # Update component-specific colors
        if "accent_color" in colors:
            if "component_specific" not in self.themes["custom"]:
                self.themes["custom"]["component_specific"] = {}
                
            if "button" not in self.themes["custom"]["component_specific"]:
                self.themes["custom"]["component_specific"]["button"] = {}
                
            button = self.themes["custom"]["component_specific"]["button"]
            button["primary_bg"] = colors["accent_color"]
            button["primary_hover"] = self.lighten_color(colors["accent_color"], 10)
            button["primary_pressed"] = self.lighten_color(colors["accent_color"], -10)
            
            if "progressbar" not in self.themes["custom"]["component_specific"]:
                self.themes["custom"]["component_specific"]["progressbar"] = {}
                
            self.themes["custom"]["component_specific"]["progressbar"]["chunk_color"] = colors["accent_color"]
        
        # Save custom theme to file
        self._save_theme("custom")
    
    def _save_theme(self, theme_name: str) -> bool:
        """Save a theme to file"""
        if theme_name not in self.themes:
            return False
            
        theme_path = os.path.join(self.themes_dir, f"{theme_name}.json")
        try:
            with open(theme_path, 'w', encoding='utf-8') as f:
                json.dump(self.themes[theme_name], f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving theme '{theme_name}': {str(e)}")
            return False
    
    def lighten_color(self, color: str, amount: int = 20) -> str:
        """Lighten or darken a hex color
        
        Args:
            color: Hex color code (e.g. "#1e1e1e")
            amount: Lightness adjustment amount (-100 to 100)
        
        Returns:
            New hex color code
        """
        try:
            c = QColor(color)
            h, s, l, a = c.getHslF()
            
            # Adjust lightness
            l = max(0, min(1, l + amount / 100.0))
            
            c.setHslF(h, s, l, a)
            return c.name()
        except:
            return color
    
    def generate_style_sheet(self, theme_name: Optional[str] = None) -> str:
        """Generate a complete stylesheet for the specified theme"""
        theme = theme_name or self.current_theme
        colors = self.get_theme_colors(theme)
        
        bg_color = colors.get("bg_color", "#1e1e1e")
        text_color = colors.get("text_color", "#e0e0e0")
        accent_color = colors.get("accent_color", "#555555")
        bg_lighter = colors.get("bg_lighter", self.lighten_color(bg_color, 10))
        bg_darker = colors.get("bg_darker", self.lighten_color(bg_color, -10))
        
        return f"""
            QMainWindow {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 12px;
            }}
            QWidget {{
                background-color: transparent;
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            #titleBar {{
                background-color: {bg_darker};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            #minButton, #maxButton, #closeButton {{
                background-color: transparent;
                border: none;
                border-radius: 7px;
            }}
            #minButton {{
                background-color: #ffbd44;
                border-radius: 7px;
            }}
            #minButton:hover {{
                background-color: #ffce5b;
            }}
            #maxButton {{
                background-color: #00ca56;
                border-radius: 7px;
            }}
            #maxButton:hover {{
                background-color: #5dde8a;
            }}
            #closeButton {{
                background-color: #ff5f57;
                border-radius: 7px;
            }}
            #closeButton:hover {{
                background-color: #ff8a84;
            }}
            QPushButton {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 8px;
                padding: 6px 12px;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(bg_lighter, 15)};
                border: 1px solid {self.lighten_color(accent_color, 15)};
            }}
            QPushButton:pressed {{
                background-color: {self.lighten_color(bg_lighter, -5)};
            }}
            QPushButton:disabled {{
                background-color: {bg_darker};
                color: {self.lighten_color(bg_color, 30)};
                border: 1px solid {self.lighten_color(bg_color, 20)};
            }}
            QGroupBox {{
                color: {self.lighten_color(text_color, -10)};
                font-weight: bold;
                border: 1px solid {accent_color};
                border-radius: 8px;
                margin-top: 1.2em;
                padding-top: 12px;
                padding-bottom: 6px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                background-color: {bg_color};
            }}
            QCheckBox, QRadioButton {{
                color: {text_color};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                background-color: {bg_lighter};
                border: 1px solid {accent_color};
                border-radius: 4px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                background-color: {bg_lighter};
                border: 1px solid {accent_color};
                border-radius: 9px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {accent_color};
                image: url("{Icon.Check.Path}");
            }}
            QRadioButton::indicator:checked {{
                background-color: {accent_color};
                border: 1px solid {accent_color};
            }}
            QLineEdit, QTextEdit, QPlainTextEdit, QListWidget, QTableWidget, QComboBox {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 8px;
                padding: 6px;
                selection-background-color: {self.lighten_color(accent_color, 10)};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
                border: 1px solid {self.lighten_color(accent_color, 20)};
            }}
            QTextEdit, QPlainTextEdit {{
                background-color: {bg_lighter};
                color: {text_color};
            }}
            QTableWidget {{
                background-color: {bg_lighter};
                alternate-background-color: {self.lighten_color(bg_lighter, 5)};
                gridline-color: {self.lighten_color(accent_color, -20)};
                border: 1px solid {accent_color};
                border-radius: 8px;
            }}
            QTableWidget QHeaderView::section {{
                background-color: {bg_darker};
                color: {text_color};
                border: 1px solid {accent_color};
                padding: 5px;
                font-weight: bold;
            }}
            QProgressBar {{
                border: 1px solid {accent_color};
                border-radius: 8px;
                background-color: {bg_lighter};
                text-align: center;
                color: {text_color};
                padding: 1px;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {accent_color};
                border-radius: 7px;
            }}
            QTabWidget::pane {{
                border: 1px solid {accent_color};
                background-color: {bg_color};
                border-radius: 8px;
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: {bg_lighter};
                color: {self.lighten_color(text_color, -10)};
                border: 1px solid {accent_color};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 14px;
                margin-right: 5px;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background-color: {bg_color};
                color: {text_color};
                border-bottom-color: {bg_color};
            }}
            QTabBar::tab:hover {{
                background-color: {self.lighten_color(bg_lighter, 15)};
            }}
            QScrollBar {{
                background-color: {bg_color};
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: 2px;
            }}
            QScrollBar::handle {{
                background-color: {self.lighten_color(bg_color, 30)};
                border-radius: 6px;
                min-height: 40px;
            }}
            QScrollBar::handle:hover {{
                background-color: {accent_color};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0px;
                height: 0px;
            }}
            QScrollBar::add-page, QScrollBar::sub-page {{
                background-color: {bg_color};
                border-radius: 6px;
            }}
            QStatusBar {{
                background-color: {accent_color};
                color: white;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                min-height: 24px;
            }}
            QToolBar {{
                background-color: {self.lighten_color(bg_color, 5)};
                border-bottom: 1px solid {accent_color};
                spacing: 6px;
                padding: 6px;
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: {text_color};
                padding: 6px;
                min-width: 24px;
                min-height: 24px;
            }}
            QToolButton:hover {{
                background-color: {self.lighten_color(bg_color, 15)};
            }}
            QToolButton:pressed {{
                background-color: {accent_color};
            }}
            QMenuBar {{
                background-color: {bg_color};
                color: {text_color};
                border-bottom: 1px solid {accent_color};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 6px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.lighten_color(bg_color, 10)};
            }}
            QMenu {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 8px 25px 8px 20px;
                border-radius: 4px;
                margin: 2px 6px;
            }}
            QMenu::item:selected {{
                background-color: {self.lighten_color(bg_color, 15)};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {accent_color};
                margin: 6px 10px;
            }}
            QComboBox {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 8px;
                padding: 6px 12px;
                min-height: 28px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border-left: 1px solid {accent_color};
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }}
            QComboBox::down-arrow {{
                image: url({Icon.DownArrow.Path});
                width: 16px;
                height: 16px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg_lighter};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 8px;
                selection-background-color: {self.lighten_color(accent_color, 10)};
            }}
            QSplitter::handle {{
                background-color: {accent_color};
                width: 2px;
                height: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {self.lighten_color(accent_color, 15)};
            }}
            #sidebarScrollArea {{
                background-color: {bg_darker};
                border: none;
                border-bottom-left-radius: 12px;
            }}
            #sidebar {{
                background-color: {bg_darker};
                border-right: 1px solid {accent_color};
                padding: 10px;
            }}
            #sidebarButton {{
                background-color: transparent;
                color: {text_color};
                border: none;
                text-align: left;
                padding: 12px;
                border-radius: 8px;
                font-size: 14px;
            }}
            #sidebarButton:hover {{
                background-color: {self.lighten_color(bg_darker, 10)};
            }}
            #sidebarButton:checked {{
                background-color: {accent_color};
                color: white;
                font-weight: bold;
            }}
            #contentArea {{
                background-color: {bg_color};
                border-bottom-right-radius: 12px;
            }}
            QHeaderView {{
                background-color: {bg_darker};
                color: {text_color};
            }}
            QHeaderView::section {{
                background-color: {bg_darker};
                color: {text_color};
                padding: 5px;
                border: 1px solid {accent_color};
                border-radius: 0px;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 8px;
                border-bottom-left-radius: 0px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 8px;
                border-bottom-right-radius: 0px;
            }}
            QListWidget {{
                background-color: {bg_lighter};
                border: 1px solid {accent_color};
                border-radius: 8px;
                padding: 5px;
            }}
            QListWidget::item {{
                background-color: transparent;
                color: {text_color};
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {accent_color};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {self.lighten_color(bg_lighter, 10)};
            }}
            QDockWidget {{
                titlebar-close-icon: url({Icon.Close.Path});
                titlebar-normal-icon: url({Icon.Undock.Path});
            }}
            QDockWidget::title {{
                text-align: center;
                background-color: {bg_darker};
                padding: 6px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QDockWidget::close-button, QDockWidget::float-button {{
                background-color: {bg_darker};
                border: none;
                padding: 2px;
                border-radius: 4px;
            }}
            QDockWidget::close-button:hover, QDockWidget::float-button:hover {{
                background-color: {self.lighten_color(bg_darker, 15)};
            }}
        """ 
    
    def apply_theme(self, theme_name):
        """Apply a theme to the application"""
        # 如果主题不存在，使用默认主题
        if theme_name not in self.themes:
            theme_name = self.default_theme
            
        self.current_theme = theme_name
        self.settings.settings.setValue("theme", theme_name)
        
        # 获取主题数据
        theme_data = self.themes[theme_name]
        
        # 应用主题
        if "style" in theme_data:
            # 新的主题格式 - 直接应用样式表
            QApplication.instance().setStyleSheet(theme_data["style"])
        else:
            # 旧的主题格式 - 生成样式表
            style_sheet = self.generate_style_sheet(theme_name)
            QApplication.instance().setStyleSheet(style_sheet)
        
        # 发射主题变更信号
        self.theme_changed.emit(theme_name)
    
    def create_theme(self, theme_name, theme_data):
        """创建新主题
        
        Args:
            theme_name (str): 主题名称
            theme_data (dict): 主题数据
            
        Returns:
            bool: 是否成功创建主题
        """
        # 确保主题目录存在
        themes_dir = os.path.join(self.settings.get_config_dir(), "themes")
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
        
        # 保存主题文件
        theme_file = os.path.join(themes_dir, f"{theme_name}.json")
        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"创建主题失败: {e}")
            return False 
        