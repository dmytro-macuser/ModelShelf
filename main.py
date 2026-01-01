#!/usr/bin/env python3
"""
ModelShelf - Main Entry Point
Download once. Organise forever.
"""

import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('modelshelf.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """
    Main application entry point.
    """
    logger.info("Starting ModelShelf...")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("ModelShelf")
        app.setOrganizationName("ModelShelf")
        app.setApplicationVersion("0.1.0-dev")
        
        # TODO: Load main window
        logger.info("ModelShelf initialized successfully")
        logger.info("Application ready (skeleton mode - M0)")
        
        # For now, just show a message
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            None,
            "ModelShelf",
            "ModelShelf v0.1.0-dev\n\nSkeleton initialized successfully!\n\nNext: Implement UI shell (M0)"
        )
        
        return 0
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please install requirements: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
