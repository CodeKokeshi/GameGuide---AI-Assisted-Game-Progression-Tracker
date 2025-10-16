import sys
import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QLabel, 
                             QTextEdit, QLineEdit, QDialog, QMessageBox,
                             QSplitter, QFrame, QListWidgetItem, QComboBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon


class AddGameDialog(QDialog):
    """Dialog for adding a new game to the library"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Game")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title label
        title_label = QLabel("Enter Game Title:")
        title_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(title_label)
        
        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., The Legend of Zelda: Ocarina of Time")
        self.title_input.setFont(QFont("Segoe UI", 10))
        self.title_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                color: #202020;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        layout.addWidget(self.title_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Segoe UI", 10))
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
                color: #202020;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setAutoDefault(False)
        
        add_btn = QPushButton("Add Game")
        add_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        add_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                background-color: #0078d4;
                color: white;
            }
            QPushButton:hover {
                background-color: #006cbd;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        add_btn.clicked.connect(self.accept)
        add_btn.setDefault(True)  # Make this the default button for Enter key
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Apply dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #f3f3f3;
            }
            QLabel {
                color: #202020;
            }
        """)
    
    def get_title(self):
        return self.title_input.text().strip()


class GameTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Progress Tracker")
        self.setMinimumSize(1000, 600)  # Increased for new UI elements
        
        # Data storage
        self.data_file = "game_progress.json"
        self.settings_file = "settings.json"
        self.games = self.load_games()
        self.current_game = None
        
        # Encryption key (derived from a fixed salt - in production, use a more secure method)
        self.encryption_key = self._get_encryption_key()
        
        # Load settings (including theme)
        self.settings = self.load_settings()
        self.is_dark_mode = self.settings.get("dark_mode", True)  # Default is dark
        
        # View/Edit mode
        self.is_edit_mode = False
        
        self.init_ui()
        self.apply_styles()
        self.update_theme_button()
        self.load_api_settings()
    
    def _get_encryption_key(self):
        """Generate encryption key from a fixed salt"""
        # In production, you might want to store this more securely
        salt = b'game_tracker_salt_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(b'game_progress_tracker_key'))
        return Fernet(key)
    
    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key"""
        if not api_key:
            return ""
        encrypted = self.encryption_key.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt API key"""
        if not encrypted_key:
            return ""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted = self.encryption_key.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting API key: {e}")
            return ""
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bar with AI settings and theme toggle
        theme_bar = QWidget()
        theme_bar.setFixedHeight(60)
        theme_bar_layout = QHBoxLayout()
        theme_bar_layout.setContentsMargins(15, 10, 15, 10)
        theme_bar_layout.setSpacing(10)
        
        # AI Provider dropdown
        ai_label = QLabel("AI Provider:")
        ai_label.setFont(QFont("Segoe UI", 10))
        theme_bar_layout.addWidget(ai_label)
        
        self.ai_provider_combo = QComboBox()
        self.ai_provider_combo.addItems(["Gemini", "ChatGPT", "Claude", "Other"])
        self.ai_provider_combo.setFont(QFont("Segoe UI", 10))
        self.ai_provider_combo.setFixedWidth(120)
        self.ai_provider_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ai_provider_combo.currentTextChanged.connect(self.on_ai_provider_changed)
        theme_bar_layout.addWidget(self.ai_provider_combo)
        
        # API Key field
        api_label = QLabel("API Key:")
        api_label.setFont(QFont("Segoe UI", 10))
        theme_bar_layout.addWidget(api_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key...")
        self.api_key_input.setFont(QFont("Segoe UI", 10))
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)  # Hide API key
        self.api_key_input.setFixedWidth(250)
        self.api_key_input.textChanged.connect(self.on_api_key_changed)
        theme_bar_layout.addWidget(self.api_key_input)
        
        theme_bar_layout.addStretch()
        
        # Theme toggle button
        self.theme_button = QPushButton()
        self.theme_button.setFont(QFont("Segoe UI", 10))
        self.theme_button.setFixedWidth(100)
        self.theme_button.setFixedHeight(35)
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self.toggle_theme)
        theme_bar_layout.addWidget(self.theme_button)
        
        theme_bar.setLayout(theme_bar_layout)
        main_layout.addWidget(theme_bar)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel - Game Library
        left_panel = self.create_library_panel()
        splitter.addWidget(left_panel)
        
        # Right Panel - Game Details
        right_panel = self.create_details_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes (30% left, 70% right)
        splitter.setSizes([350, 850])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
    def create_library_panel(self):
        """Create the left panel with game library"""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(250)  # Minimum width to prevent crushing
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Header
        header_label = QLabel("📚 Game Library")
        header_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_label.setWordWrap(True)
        layout.addWidget(header_label)
        
        # Game list - will expand to fill available space
        self.game_list = QListWidget()
        self.game_list.setFont(QFont("Segoe UI", 10))
        self.game_list.itemClicked.connect(self.on_game_selected)
        self.game_list.itemDoubleClicked.connect(self.rename_game)
        self.populate_game_list()
        layout.addWidget(self.game_list, stretch=1)  # Give it stretch factor
        
        # Add game button
        add_button = QPushButton("➕ Add New Game")
        add_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        add_button.setMinimumHeight(40)
        add_button.clicked.connect(self.add_new_game)
        layout.addWidget(add_button)
        
        panel.setLayout(layout)
        return panel
    
    def create_details_panel(self):
        """Create the right panel with game details"""
        panel = QFrame()
        panel.setFrameShape(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(400)  # Minimum width to prevent crushing
        
        # Create a scroll area for the content
        from PyQt6.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Game title
        self.game_title_label = QLabel("")
        self.game_title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.game_title_label.setWordWrap(True)
        layout.addWidget(self.game_title_label)
        
        # Divider
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.Shape.HLine)
        self.divider.setStyleSheet("background-color: #e0e0e0;")
        self.divider.setMaximumHeight(2)
        layout.addWidget(self.divider)
        
        # ===== VIEW MODE WIDGETS =====
        # Current Situation (View)
        self.view_situation_label = QLabel("📝 Current Situation")
        self.view_situation_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.view_situation_label.setWordWrap(True)
        self.view_situation_label.setContentsMargins(0, 10, 0, 5)
        layout.addWidget(self.view_situation_label)
        
        self.view_situation_text = QLabel("")
        self.view_situation_text.setFont(QFont("Segoe UI", 10))
        self.view_situation_text.setWordWrap(True)
        self.view_situation_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.view_situation_text.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(self.view_situation_text)
        
        # Next Objective (View)
        self.view_objective_label = QLabel("🎯 Next Objective")
        self.view_objective_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.view_objective_label.setWordWrap(True)
        self.view_objective_label.setContentsMargins(0, 10, 0, 5)
        layout.addWidget(self.view_objective_label)
        
        self.view_objective_text = QLabel("")
        self.view_objective_text.setFont(QFont("Segoe UI", 10))
        self.view_objective_text.setWordWrap(True)
        self.view_objective_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.view_objective_text.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(self.view_objective_text)
        
        # Guide Hint (View)
        self.view_guide_label = QLabel("💡 Guide Hint")
        self.view_guide_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.view_guide_label.setWordWrap(True)
        self.view_guide_label.setContentsMargins(0, 10, 0, 5)
        layout.addWidget(self.view_guide_label)
        
        self.view_guide_text = QLabel("")
        self.view_guide_text.setFont(QFont("Segoe UI", 10))
        self.view_guide_text.setWordWrap(True)
        self.view_guide_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.view_guide_text.setContentsMargins(0, 0, 0, 10)
        layout.addWidget(self.view_guide_text)
        
        layout.addStretch()
        
        # Edit button
        self.edit_button = QPushButton("✏️ Edit")
        self.edit_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_button.setMinimumHeight(40)
        self.edit_button.clicked.connect(self.enter_edit_mode)
        layout.addWidget(self.edit_button)
        
        # ===== EDIT MODE WIDGETS =====
        # Current Situation section (Edit)
        self.edit_situation_label = QLabel("📝 Current Situation / What I Last Did:")
        self.edit_situation_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_situation_label.setWordWrap(True)
        layout.addWidget(self.edit_situation_label)
        
        self.situation_input = QTextEdit()
        self.situation_input.setPlaceholderText("Describe where you are in the game and what you last remember doing...")
        self.situation_input.setFont(QFont("Segoe UI", 10))
        self.situation_input.setMinimumHeight(80)
        self.situation_input.setMaximumHeight(120)
        self.situation_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.situation_input)
        
        # Next Objective section (Edit)
        self.edit_objective_label = QLabel("🎯 Next Objective (Optional):")
        self.edit_objective_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_objective_label.setWordWrap(True)
        layout.addWidget(self.edit_objective_label)
        
        self.objective_input = QTextEdit()
        self.objective_input.setPlaceholderText("What do you want to accomplish next? (Optional)")
        self.objective_input.setFont(QFont("Segoe UI", 10))
        self.objective_input.setMinimumHeight(60)
        self.objective_input.setMaximumHeight(80)
        self.objective_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.objective_input)
        
        # Output Behavior section (Edit)
        self.edit_behavior_label = QLabel("⚙️ Output Behavior (Optional):")
        self.edit_behavior_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_behavior_label.setWordWrap(True)
        layout.addWidget(self.edit_behavior_label)
        
        self.behavior_input = QTextEdit()
        self.behavior_input.setPlaceholderText("How should the guide respond? e.g., 'Tell me how to prepare' or 'Focus on earning money first' (Optional)")
        self.behavior_input.setFont(QFont("Segoe UI", 10))
        self.behavior_input.setMinimumHeight(60)
        self.behavior_input.setMaximumHeight(80)
        self.behavior_input.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.behavior_input)
        
        # See Next Step button (Edit)
        self.guide_button = QPushButton("🔍 See Next Step")
        self.guide_button.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.guide_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.guide_button.setMinimumHeight(40)
        self.guide_button.clicked.connect(self.generate_guide)
        layout.addWidget(self.guide_button)
        
        # Guide output section (Edit)
        self.edit_guide_output_label = QLabel("💡 Guide Hint:")
        self.edit_guide_output_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.edit_guide_output_label.setWordWrap(True)
        layout.addWidget(self.edit_guide_output_label)
        
        self.guide_output = QTextEdit()
        self.guide_output.setReadOnly(True)
        self.guide_output.setFont(QFont("Segoe UI", 10))
        self.guide_output.setPlaceholderText("Your guide hint will appear here after clicking 'See Next Step'...")
        self.guide_output.setMinimumHeight(120)
        layout.addWidget(self.guide_output, stretch=1)  # Give it stretch factor
        
        # Buttons row (Edit mode)
        button_row = QHBoxLayout()
        
        self.done_button = QPushButton("✓ Done")
        self.done_button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.done_button.setMinimumHeight(35)
        self.done_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.done_button.clicked.connect(self.exit_edit_mode)
        button_row.addWidget(self.done_button)
        
        button_row.addStretch()
        
        self.delete_button = QPushButton("🗑️ Delete Game")
        self.delete_button.setFont(QFont("Segoe UI", 10))
        self.delete_button.setMinimumHeight(35)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.clicked.connect(self.delete_current_game)
        button_row.addWidget(self.delete_button)
        
        layout.addLayout(button_row)
        
        # Initially disable all inputs
        self.set_details_enabled(False)
        
        content_widget.setLayout(layout)
        scroll_area.setWidget(content_widget)
        
        # Main panel layout
        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll_area)
        panel.setLayout(panel_layout)
        
        return panel
    
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.is_dark_mode = not self.is_dark_mode
        self.settings["dark_mode"] = self.is_dark_mode
        self.save_settings()
        self.apply_styles()
        self.update_theme_button()
    
    def update_theme_button(self):
        """Update the theme button text based on current mode"""
        if self.is_dark_mode:
            self.theme_button.setText("🌙 Dark")
        else:
            self.theme_button.setText("☀️ Light")
    
    def apply_styles(self):
        """Apply Windows 11 inspired styling with theme support"""
        if self.is_dark_mode:
            # Dark mode colors
            bg_main = "#1e1e1e"
            bg_panel = "#252526"
            bg_input = "#2d2d30"
            bg_list = "#2d2d30"
            text_primary = "#e0e0e0"
            text_secondary = "#ffffff"
            border_color = "#3e3e42"
            hover_bg = "#3e3e42"
            selected_bg = "#094771"
            selected_text = "#60cdff"
            scrollbar_bg = "#3e3e42"
            scrollbar_handle = "#686868"
            scrollbar_hover = "#9e9e9e"
        else:
            # Light mode colors
            bg_main = "#f9f9f9"
            bg_panel = "#ffffff"
            bg_input = "#ffffff"
            bg_list = "#fafafa"
            text_primary = "#202020"
            text_secondary = "#202020"
            border_color = "#e0e0e0"
            hover_bg = "#f0f0f0"
            selected_bg = "#e3f2fd"
            selected_text = "#0078d4"
            scrollbar_bg = "#f0f0f0"
            scrollbar_handle = "#c0c0c0"
            scrollbar_hover = "#a0a0a0"
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_main};
            }}
            QWidget {{
                background-color: {bg_main};
                color: {text_primary};
            }}
            QFrame {{
                background-color: {bg_panel};
                border: 1px solid {border_color};
            }}
            QLabel {{
                color: {text_primary};
                background-color: transparent;
                border: none;
            }}
            QListWidget {{
                background-color: {bg_list};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 5px;
                outline: none;
                color: {text_primary};
            }}
            QListWidget::item {{
                padding: 12px;
                border-radius: 4px;
                margin: 2px;
                color: {text_primary};
            }}
            QListWidget::item:selected {{
                background-color: {selected_bg};
                color: {selected_text};
            }}
            QListWidget::item:hover {{
                background-color: {hover_bg};
                color: {text_primary};
            }}
            QTextEdit {{
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 10px;
                background-color: {bg_input};
                color: {text_primary};
            }}
            QTextEdit:focus {{
                border: 2px solid #0078d4;
            }}
            QScrollArea {{
                border: none;
                background-color: {bg_panel};
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: {bg_panel};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {scrollbar_bg};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {scrollbar_handle};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {scrollbar_hover};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QPushButton {{
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #006cbd;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
            QPushButton#deleteButton {{
                background-color: #d32f2f;
            }}
            QPushButton#deleteButton:hover {{
                background-color: #b71c1c;
            }}
            QPushButton#themeButton {{
                background-color: {bg_input};
                color: {text_primary};
                border: 1px solid {border_color};
            }}
            QPushButton#themeButton:hover {{
                background-color: {hover_bg};
            }}
            QComboBox {{
                background-color: {bg_input};
                color: {text_primary};
                border: 2px solid {border_color};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox:hover {{
                border: 2px solid #0078d4;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {text_primary};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg_input};
                color: {text_primary};
                selection-background-color: {selected_bg};
                selection-color: {selected_text};
                border: 1px solid {border_color};
            }}
            QLineEdit {{
                background-color: {bg_input};
                color: {text_primary};
                border: 2px solid {border_color};
                border-radius: 4px;
                padding: 5px;
            }}
            QLineEdit:focus {{
                border: 2px solid #0078d4;
            }}
        """)
        
        # Special styling for delete button
        self.delete_button.setObjectName("deleteButton")
    
    def populate_game_list(self):
        """Populate the game list widget"""
        self.game_list.clear()
        for game_title in sorted(self.games.keys()):
            item = QListWidgetItem(game_title)
            self.game_list.addItem(item)
    
    def add_new_game(self):
        """Open dialog to add a new game"""
        dialog = AddGameDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = dialog.get_title()
            if title:
                if title in self.games:
                    QMessageBox.warning(self, "Game Exists", 
                                      f"'{title}' is already in your library!")
                else:
                    self.games[title] = {
                        "situation": "",
                        "objective": "",
                        "behavior": "",
                        "guide": ""
                    }
                    self.save_games()
                    self.populate_game_list()
                    
                    # Select the newly added game
                    items = self.game_list.findItems(title, Qt.MatchFlag.MatchExactly)
                    if items:
                        self.game_list.setCurrentItem(items[0])
                        self.on_game_selected(items[0])
            else:
                QMessageBox.warning(self, "Invalid Input", 
                                  "Please enter a game title!")
    
    def rename_game(self, item):
        """Rename a game by double-clicking it"""
        if not item:
            return
        
        old_title = item.text()
        
        # Create a dialog similar to AddGameDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Rename Game")
        dialog.setModal(True)
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title label
        title_label = QLabel("Enter New Game Title:")
        title_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(title_label)
        
        # Title input
        title_input = QLineEdit()
        title_input.setText(old_title)
        title_input.selectAll()  # Select all text for easy editing
        title_input.setFont(QFont("Segoe UI", 10))
        title_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
                color: #202020;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        layout.addWidget(title_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Segoe UI", 10))
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
                color: #202020;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        cancel_btn.setAutoDefault(False)
        
        rename_btn = QPushButton("Rename")
        rename_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        rename_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                background-color: #0078d4;
                color: white;
            }
            QPushButton:hover {
                background-color: #006cbd;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        rename_btn.clicked.connect(dialog.accept)
        rename_btn.setDefault(True)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(rename_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # Apply dialog style
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f3f3f3;
            }
            QLabel {
                color: #202020;
            }
        """)
        
        # Execute dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_title = title_input.text().strip()
            
            if not new_title:
                QMessageBox.warning(self, "Invalid Input", 
                                  "Please enter a game title!")
                return
            
            if new_title == old_title:
                return  # No change
            
            if new_title in self.games:
                QMessageBox.warning(self, "Game Exists", 
                                  f"'{new_title}' is already in your library!")
                return
            
            # Rename the game
            self.games[new_title] = self.games.pop(old_title)
            self.save_games()
            
            # Update current game if it was selected
            if self.current_game == old_title:
                self.current_game = new_title
                self.game_title_label.setText(new_title)
            
            # Refresh the list and reselect
            self.populate_game_list()
            items = self.game_list.findItems(new_title, Qt.MatchFlag.MatchExactly)
            if items:
                self.game_list.setCurrentItem(items[0])
                self.on_game_selected(items[0])
    
    def on_game_selected(self, item):
        """Handle game selection from the list"""
        if item:
            game_title = item.text()
            self.current_game = game_title
            self.is_edit_mode = False  # Reset to view mode when switching games
            self.load_game_details(game_title)
            self.set_details_enabled(True)
    
    def load_game_details(self, game_title):
        """Load and display game details"""
        if game_title in self.games:
            game_data = self.games[game_title]
            self.game_title_label.setText(game_title)
            
            # Block signals to prevent auto-save while loading
            self.situation_input.blockSignals(True)
            self.objective_input.blockSignals(True)
            self.behavior_input.blockSignals(True)
            
            self.situation_input.setPlainText(game_data.get("situation", ""))
            self.objective_input.setPlainText(game_data.get("objective", ""))
            self.behavior_input.setPlainText(game_data.get("behavior", ""))
            self.guide_output.setPlainText(game_data.get("guide", ""))
            
            # Unblock signals
            self.situation_input.blockSignals(False)
            self.objective_input.blockSignals(False)
            self.behavior_input.blockSignals(False)
    
    def enter_edit_mode(self):
        """Switch to edit mode"""
        self.is_edit_mode = True
        self.update_view_mode()
    
    def exit_edit_mode(self):
        """Switch back to view mode"""
        self.is_edit_mode = False
        self.update_view_mode()
    
    def update_view_mode(self):
        """Update UI based on view/edit mode"""
        if not self.current_game:
            return
        
        # Get current data
        game_data = self.games.get(self.current_game, {})
        situation = game_data.get("situation", "")
        objective = game_data.get("objective", "")
        guide = game_data.get("guide", "")
        
        if self.is_edit_mode:
            # Hide view mode widgets
            self.view_situation_label.setVisible(False)
            self.view_situation_text.setVisible(False)
            self.view_objective_label.setVisible(False)
            self.view_objective_text.setVisible(False)
            self.view_guide_label.setVisible(False)
            self.view_guide_text.setVisible(False)
            self.edit_button.setVisible(False)
            
            # Show edit mode widgets
            self.edit_situation_label.setVisible(True)
            self.situation_input.setVisible(True)
            self.edit_objective_label.setVisible(True)
            self.objective_input.setVisible(True)
            self.edit_behavior_label.setVisible(True)
            self.behavior_input.setVisible(True)
            self.guide_button.setVisible(True)
            self.edit_guide_output_label.setVisible(True)
            self.guide_output.setVisible(True)
            self.done_button.setVisible(True)
            self.delete_button.setVisible(True)
        else:
            # Hide edit mode widgets
            self.edit_situation_label.setVisible(False)
            self.situation_input.setVisible(False)
            self.edit_objective_label.setVisible(False)
            self.objective_input.setVisible(False)
            self.edit_behavior_label.setVisible(False)
            self.behavior_input.setVisible(False)
            self.guide_button.setVisible(False)
            self.edit_guide_output_label.setVisible(False)
            self.guide_output.setVisible(False)
            self.done_button.setVisible(False)
            self.delete_button.setVisible(False)
            
            # Show view mode widgets (only if content exists)
            if situation:
                self.view_situation_label.setVisible(True)
                self.view_situation_text.setVisible(True)
                self.view_situation_text.setText(situation)
            else:
                self.view_situation_label.setVisible(False)
                self.view_situation_text.setVisible(False)
            
            if objective:
                self.view_objective_label.setVisible(True)
                self.view_objective_text.setVisible(True)
                self.view_objective_text.setText(objective)
            else:
                self.view_objective_label.setVisible(False)
                self.view_objective_text.setVisible(False)
            
            if guide:
                self.view_guide_label.setVisible(True)
                self.view_guide_text.setVisible(True)
                self.view_guide_text.setText(guide)
            else:
                self.view_guide_label.setVisible(False)
                self.view_guide_text.setVisible(False)
            
            self.edit_button.setVisible(True)
    
    def set_details_enabled(self, enabled):
        """Enable or disable the details panel"""
        # Show or hide all elements
        self.game_title_label.setVisible(enabled)
        self.divider.setVisible(enabled)
        
        if not enabled:
            # Hide everything
            self.view_situation_label.setVisible(False)
            self.view_situation_text.setVisible(False)
            self.view_objective_label.setVisible(False)
            self.view_objective_text.setVisible(False)
            self.view_guide_label.setVisible(False)
            self.view_guide_text.setVisible(False)
            self.edit_button.setVisible(False)
            
            self.edit_situation_label.setVisible(False)
            self.situation_input.setVisible(False)
            self.edit_objective_label.setVisible(False)
            self.objective_input.setVisible(False)
            self.edit_behavior_label.setVisible(False)
            self.behavior_input.setVisible(False)
            self.guide_button.setVisible(False)
            self.edit_guide_output_label.setVisible(False)
            self.guide_output.setVisible(False)
            self.done_button.setVisible(False)
            self.delete_button.setVisible(False)
            
            self.game_title_label.setText("")
            self.situation_input.clear()
            self.objective_input.clear()
            self.behavior_input.clear()
            self.guide_output.clear()
            self.is_edit_mode = False
        else:
            # Start in view mode
            self.is_edit_mode = False
            self.update_view_mode()
    
    def on_text_changed(self):
        """Auto-save when text changes"""
        if self.current_game and self.current_game in self.games:
            self.games[self.current_game]["situation"] = self.situation_input.toPlainText()
            self.games[self.current_game]["objective"] = self.objective_input.toPlainText()
            self.games[self.current_game]["behavior"] = self.behavior_input.toPlainText()
            self.save_games()
    
    def generate_guide(self):
        """Generate guide hint using AI API"""
        if not self.current_game:
            return
        
        situation = self.situation_input.toPlainText().strip()
        
        if not situation:
            QMessageBox.warning(self, "Missing Information", 
                              "Please fill in the 'Current Situation' field first!")
            return
        
        # Get API settings
        api_key = self.decrypt_api_key(self.settings.get("api_key", ""))
        ai_provider = self.settings.get("ai_provider", "Gemini")
        
        if not api_key:
            QMessageBox.warning(self, "API Key Missing", 
                              "Please enter your API key in the top bar!")
            return
        
        # Disable button and show loading state
        self.guide_button.setEnabled(False)
        self.guide_button.setText("⏳ Generating...")
        self.guide_output.setPlainText("Searching game guides for your next move...")
        QApplication.processEvents()  # Update UI
        
        try:
            # Get optional fields
            objective = self.objective_input.toPlainText().strip()
            behavior = self.behavior_input.toPlainText().strip()
            
            # Generate the guide
            guide_text = self.call_ai_api(
                game_title=self.current_game,
                situation=situation,
                objective=objective,
                behavior=behavior,
                api_key=api_key,
                provider=ai_provider
            )
            
            self.guide_output.setPlainText(guide_text)
            self.games[self.current_game]["guide"] = guide_text
            self.save_games()
            
            # Update view mode display
            if not self.is_edit_mode:
                self.update_view_mode()
                
        except Exception as e:
            error_msg = f"Error generating guide: {str(e)}\n\nPlease check your API key and internet connection."
            QMessageBox.critical(self, "API Error", error_msg)
            self.guide_output.setPlainText(f"Failed to generate hint.\n\nError: {str(e)}")
        
        finally:
            # Re-enable button
            self.guide_button.setEnabled(True)
            self.guide_button.setText("🔍 See Next Step")
    
    def call_ai_api(self, game_title, situation, objective, behavior, api_key, provider):
        """Call AI API to generate guide hint"""
        import requests
        
        # Build a more specific prompt for better search results
        if objective:
            # If we have an objective, focus on that
            search_query = f"{game_title} walkthrough guide {situation} {objective}"
            main_question = f"In the game '{game_title}', the player's current situation is: {situation}. Their immediate objective is: {objective}."
        else:
            # If no objective, just use the situation
            search_query = f"{game_title} walkthrough guide {situation}"
            main_question = f"In the game '{game_title}', the player's current situation is: {situation}."
        
        # Build the user prompt
        prompt_parts = [main_question]
        
        if behavior:
            # If there's special behavior instruction, add it
            prompt_parts.append(f"Special request: {behavior}")
            prompt_parts.append("Taking this request into account, what is the next step?")
        else:
            # Standard question
            prompt_parts.append("Search online game guides and walkthroughs to find: What is the EXACT next step the player should take right now?")
        
        prompt_parts.append("Provide ONLY the immediate, actionable next step. Be specific and concise. If you find conflicting information, provide the most commonly recommended solution.")
        
        user_prompt = " ".join(prompt_parts)
        
        # Enhanced system prompt for accuracy
        system_prompt = f"""You are an expert video game guide assistant. Your task is to provide accurate, actionable guidance based on REAL game walkthroughs and guides found online.

IMPORTANT INSTRUCTIONS:
1. Search the internet for "{search_query}" to find accurate walkthrough information
2. Use ONLY information from actual game guides, walkthroughs, and wikis
3. Provide the IMMEDIATE next step - not general advice
4. Be specific with locations, items, or actions
5. If multiple solutions exist, mention the most common one
6. Do NOT make up information - only use what you find in guides
7. Keep your response concise (2-3 sentences max)

Focus on accuracy over creativity. The player needs reliable information."""
        
        if provider == "Gemini":
            return self._call_gemini_api(user_prompt, system_prompt, api_key)
        elif provider == "ChatGPT":
            return self._call_openai_api(user_prompt, system_prompt, api_key)
        elif provider == "Claude":
            return self._call_claude_api(user_prompt, system_prompt, api_key)
        else:
            return "Please select a supported AI provider (Gemini, ChatGPT, or Claude)."
    
    def _call_gemini_api(self, user_prompt, system_prompt, api_key):
        """Call Google Gemini API with Google Search grounding"""
        import requests
        
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "tools": [{"google_search": {}}],  # Enable Google Search grounding
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "temperature": 0.3,  # Lower temperature for more factual responses
                "topP": 0.8,
                "topK": 20,
                "maxOutputTokens": 500
            }
        }
        
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        
        # Extract the text from response
        candidate = result.get("candidates", [{}])[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [{}])
        text = parts[0].get("text", "Could not generate a hint. Please try again.")
        
        # Extract sources if available
        grounding_metadata = candidate.get("groundingMetadata", {})
        attributions = grounding_metadata.get("groundingAttributions", [])
        
        if attributions:
            text += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📚 Sources Consulted:\n"
            # Get unique sources
            seen_uris = set()
            unique_attrs = []
            for attr in attributions:
                web = attr.get("web", {})
                uri = web.get("uri", "")
                if uri and uri not in seen_uris:
                    seen_uris.add(uri)
                    unique_attrs.append(attr)
            
            for attr in unique_attrs[:5]:  # Limit to 5 sources
                web = attr.get("web", {})
                title = web.get("title", "")
                uri = web.get("uri", "")
                if title and uri:
                    text += f"• {title}\n  {uri}\n"
        
        return text
    
    def _call_openai_api(self, user_prompt, system_prompt, api_key):
        """Call OpenAI ChatGPT API"""
        import requests
        
        api_url = "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            api_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        text = result.get("choices", [{}])[0].get("message", {}).get("content", "Could not generate a hint.")
        
        return text
    
    def _call_claude_api(self, user_prompt, system_prompt, api_key):
        """Call Anthropic Claude API"""
        import requests
        
        api_url = "https://api.anthropic.com/v1/messages"
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 500,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }
        
        response = requests.post(
            api_url,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned status {response.status_code}: {response.text}")
        
        result = response.json()
        text = result.get("content", [{}])[0].get("text", "Could not generate a hint.")
        
        return text
    
    def delete_current_game(self):
        """Delete the currently selected game"""
        if not self.current_game:
            return
        
        reply = QMessageBox.question(
            self, 
            "Delete Game",
            f"Are you sure you want to delete '{self.current_game}' from your library?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.games[self.current_game]
            self.save_games()
            self.populate_game_list()
            self.current_game = None
            self.set_details_enabled(False)
    
    def load_games(self):
        """Load games from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading games: {e}")
                return {}
        return {}
    
    def save_games(self):
        """Save games to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving games: {e}")
    
    def load_settings(self):
        """Load settings from JSON file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return {"dark_mode": True, "ai_provider": "Gemini", "api_key": ""}
        return {"dark_mode": True, "ai_provider": "Gemini", "api_key": ""}
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_api_settings(self):
        """Load AI provider and API key from settings"""
        ai_provider = self.settings.get("ai_provider", "Gemini")
        encrypted_api_key = self.settings.get("api_key", "")
        
        # Set AI provider
        index = self.ai_provider_combo.findText(ai_provider)
        if index >= 0:
            self.ai_provider_combo.setCurrentIndex(index)
        
        # Decrypt and set API key
        if encrypted_api_key:
            decrypted_key = self.decrypt_api_key(encrypted_api_key)
            self.api_key_input.setText(decrypted_key)
    
    def on_ai_provider_changed(self, provider):
        """Handle AI provider change"""
        self.settings["ai_provider"] = provider
        self.save_settings()
    
    def on_api_key_changed(self):
        """Handle API key change and encrypt it"""
        api_key = self.api_key_input.text()
        encrypted_key = self.encrypt_api_key(api_key)
        self.settings["api_key"] = encrypted_key
        self.save_settings()


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont("Segoe UI", 10))
    
    window = GameTrackerApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
