# -*- coding: utf-8 -*-
"""
Game Progress Tracker - Modular Main Executor

This file serves as the main entry point for the modular Game Progress Tracker application.
It imports and initializes the main application from the src module.
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon

from src.app import GameTrackerApp

def resource_path(relative_path: str) -> str:
    """Resolve resource paths for development and PyInstaller bundles."""
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return str(Path(base_path) / relative_path)


def main():
    """Main entry point for the Game Progress Tracker application"""
    app = QApplication(sys.argv)
    
    # Set application-wide font
    app.setFont(QFont("Segoe UI", 10))
    app.setApplicationName("NextStep")
    app.setApplicationDisplayName("NextStep")

    icon_path = resource_path("GG_Icon.png")
    app.setWindowIcon(QIcon(icon_path))
    
    # Create and show the main window
    window = GameTrackerApp(app_icon_path=icon_path)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())
if __name__ == "__main__":
    main()