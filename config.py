"""
Application configuration and constants
"""

import os
from pathlib import Path

# App info
APP_NAME = "Downloader Studio"
APP_VERSION = "2.16.0"
APP_AUTHOR = "BS Studio"
APP_GITHUB_REPO = "batsave/downloader-studio"
APP_RELEASES_URL = f"https://github.com/{APP_GITHUB_REPO}/releases"
APP_LATEST_RELEASE_API = f"https://api.github.com/repos/{APP_GITHUB_REPO}/releases/latest"

# Directories
APP_DIR = Path(__file__).parent
ASSETS_DIR = APP_DIR / "assets"
I18N_DIR = APP_DIR / "i18n"

USER_DATA_DIR = Path(
    os.environ.get("LOCALAPPDATA")
    or os.environ.get("APPDATA")
    or Path.home()
) / APP_NAME

# Settings
SETTINGS_FILE = str(USER_DATA_DIR / "downloader_settings.json")
LOG_FILE = str(USER_DATA_DIR / "downloader.log")

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
