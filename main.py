#!/usr/bin/env python3
"""
ModelShelf - Main Entry Point
Download once. Organise forever.
"""

import sys
import logging
from pathlib import Path

# Configure logging
from app.config import LOG_FILE

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE)
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
        from PySide6.QtQml import QQmlApplicationEngine
        from PySide6.QtCore import QUrl
        from app.config import APP_NAME, APP_VERSION
        
        # Import bridge to register QML types
        import ui.bridge
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setOrganizationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        
        # Create QML engine
        engine = QQmlApplicationEngine()
        
        # Add QML import paths
        qml_dir = Path(__file__).parent / "ui" / "qml"
        engine.addImportPath(str(qml_dir))
        
        # Load main QML file
        qml_file = qml_dir / "main.qml"
        
        if not qml_file.exists():
            logger.error(f"QML file not found: {qml_file}")
            return 1
        
        engine.load(QUrl.fromLocalFile(str(qml_file)))
        
        if not engine.rootObjects():
            logger.error("Failed to load QML interface")
            return 1
        
        logger.info(f"{APP_NAME} v{APP_VERSION} initialized successfully")
        logger.info("M1: Discover functionality ready")
        
        # Run application event loop
        return app.exec()
        
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error("Please install requirements: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        
        # Show error dialog if possible
        try:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                None,
                "ModelShelf Error",
                f"An error occurred:\n\n{str(e)}\n\nCheck {LOG_FILE} for details."
            )
        except:
            pass
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
