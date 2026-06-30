"""
Downloader Studio - Main Entry Point
Multi-language media downloader with PyQt5 GUI
"""

import sys
import os

# Add app directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ui.main_window import Downloader, show_splash
from app.utils.icons import create_svg_icon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    splash = show_splash()
    app.processEvents()

    window = Downloader()

    def show_main_window():
        window.show()
        if splash:
            splash.finish(window)

    QTimer.singleShot(2000, show_main_window)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
