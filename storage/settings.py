"""
ModelShelf Settings Manager
Persistent application settings.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional
from app.config import SETTINGS_FILE, DEFAULT_DOWNLOAD_DIR

logger = logging.getLogger(__name__)


class Settings:
    """
    Application settings manager.
    Handles loading, saving, and accessing user preferences.
    """
    
    # Default settings
    DEFAULTS = {
        "download_folder": str(DEFAULT_DOWNLOAD_DIR),
        "cache_size_mb": 500,
        "max_concurrent_downloads": 3,
        "theme": "light",
        "language": "en-GB",
        "check_for_updates": True,
        "anonymous_telemetry": False,
    }
    
    def __init__(self, settings_file: Optional[Path] = None):
        """
        Initialise settings manager.
        
        Args:
            settings_file: Path to settings file (defaults to config location)
        """
        self.settings_file = settings_file or SETTINGS_FILE
        self._settings = self.DEFAULTS.copy()
        self.load()
    
    def load(self) -> None:
        """
        Load settings from file.
        Creates default settings file if it doesn't exist.
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults (in case new settings were added)
                    self._settings.update(loaded)
                    logger.info(f"Settings loaded from {self.settings_file}")
            else:
                # Create default settings file
                self.save()
                logger.info(f"Created default settings at {self.settings_file}")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}", exc_info=True)
            logger.warning("Using default settings")
    
    def save(self) -> None:
        """
        Save current settings to file.
        """
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2)
            
            logger.info(f"Settings saved to {self.settings_file}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}", exc_info=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
        
        Returns:
            Setting value or default
        """
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value and save.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self._settings[key] = value
        self.save()
    
    def reset(self) -> None:
        """
        Reset all settings to defaults.
        """
        self._settings = self.DEFAULTS.copy()
        self.save()
        logger.info("Settings reset to defaults")
    
    @property
    def download_folder(self) -> Path:
        """Get download folder as Path object."""
        return Path(self.get("download_folder"))
    
    @download_folder.setter
    def download_folder(self, path: Path) -> None:
        """Set download folder."""
        self.set("download_folder", str(path))


# Global settings instance
_settings_instance: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get the global settings instance.
    Creates it if it doesn't exist.
    
    Returns:
        Global Settings instance
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
