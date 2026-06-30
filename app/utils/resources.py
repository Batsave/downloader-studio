"""Resource path utilities for Inno Setup compatibility"""

import sys
import os
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource.
    Works with both PyInstaller and regular Python execution.
    Compatible with Inno Setup compiled executables.
    """
    # When running as PyInstaller executable
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    # When running as Inno Setup compiled exe
    elif getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    # When running as normal Python script
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return os.path.join(base_path, relative_path)


def get_assets_dir() -> str:
    """Get assets directory path"""
    return resource_path("assets")


def get_icon_path(icon_name: str) -> str:
    """Get path to icon file"""
    return os.path.join(get_assets_dir(), f"{icon_name}.svg")
