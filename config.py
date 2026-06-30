"""
Application configuration and constants
"""

import os
from pathlib import Path

# App info
APP_NAME = "Downloader Studio"
APP_VERSION = "2.11"
APP_AUTHOR = "BS Studio"

# Directories
APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR / "assets"
I18N_DIR = APP_DIR / "i18n"

# Settings
SETTINGS_FILE = "downloader_settings.json"
LOG_FILE = "downloader.log"

# UI Constants
SIDEBAR_EXPANDED_WIDTH = 200
SIDEBAR_COMPACT_WIDTH = 80
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 700
MINIMAL_WINDOW_WIDTH = 550
MINIMAL_WINDOW_HEIGHT = 110

# Default settings
DEFAULT_LANGUAGE = "fr"
DEFAULT_THEME = "dark"
DEFAULT_OUTPUT_DIR = str(Path.home() / "Downloads")

# Supported languages
LANGUAGES = {
    "fr": "Français",
    "en": "English",
    "de": "Deutsch",
    "es": "Español"
}

# Themes
THEMES_AVAILABLE = ["dark", "light"]
