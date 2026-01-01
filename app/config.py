"""
ModelShelf Configuration
Application settings and constants.
"""

import os
from pathlib import Path
import appdirs

# Application metadata
APP_NAME = "ModelShelf"
APP_VERSION = "0.1.0-dev"
APP_AUTHOR = "ModelShelf"

# Directories
USER_DATA_DIR = Path(appdirs.user_data_dir(APP_NAME, APP_AUTHOR))
USER_CONFIG_DIR = Path(appdirs.user_config_dir(APP_NAME, APP_AUTHOR))
USER_CACHE_DIR = Path(appdirs.user_cache_dir(APP_NAME, APP_AUTHOR))

# Ensure directories exist
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
USER_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_PATH = USER_DATA_DIR / "modelshelf.db"

# Settings
SETTINGS_FILE = USER_CONFIG_DIR / "settings.ini"

# Downloads
DEFAULT_DOWNLOAD_DIR = Path.home() / "ModelShelf" / "models"

# Logging
LOG_FILE = USER_DATA_DIR / "modelshelf.log"
