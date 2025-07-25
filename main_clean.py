#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Technical Fountain Series Support Tool - Entry Point"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window_qt6 import MainWindow
from utils.logger import get_logger


def main():
    """Application entry point"""
    # Initialize logger
    logger = get_logger(__name__)
    logger.info("Starting application")
    
    # High DPI support (automatic in Qt6)
    # These attributes were removed in Qt6, no need to set them
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Technical Fountain Series Support Tool")
    app.setOrganizationName("Technical Fountain")
    
    # Set style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    logger.info("Main window displayed")
    
    # Run application
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()