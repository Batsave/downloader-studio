import sys
import os
import logging
import ctypes
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QSplashScreen, QProgressBar, QShortcut
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QKeySequence
import yt_dlp

# Logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('downloader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import des pages
from app.ui.pages.search_page import SearchPage
from app.ui.pages.queue_page import QueuePage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.logs_page import LogsPage
from app.core.download_engine import DownloadEngine
from app.utils.icons import create_svg_icon, create_colored_svg_icon
from app.utils.resources import resource_path
from config import DEFAULT_OUTPUT_DIR

logger.info("Application démarrée")


def get_nav_labels():
    """Get navigation labels in current language"""
    from i18n import t
    return [
        (t("search"), 0, "search"),
        (t("queue"), 1, "queue"),
        (t("settings"), 2, "settings"),
        (t("logs"), 3, "logs"),
    ]


def settings_path():
    return os.path.join(os.path.abspath("."), "downloader_settings.json")


def _colorref(hex_color):
    value = hex_color.lstrip("#")
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return red | (green << 8) | (blue << 16)


def set_windows_title_bar_theme(widget, dark_enabled, bg_color, text_color):
    if sys.platform != "win32":
        return

    try:
        hwnd = int(widget.winId())
        enabled = ctypes.c_int(1 if dark_enabled else 0)
        for attr in (20, 19):  # Windows 10/11 builds differ.
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                attr,
                ctypes.byref(enabled),
                ctypes.sizeof(enabled),
            )

        caption = ctypes.c_int(_colorref(bg_color))
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            35,  # DWMWA_CAPTION_COLOR, Windows 11+
            ctypes.byref(caption),
            ctypes.sizeof(caption),
        )

        text = ctypes.c_int(_colorref(text_color))
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            36,  # DWMWA_TEXT_COLOR, Windows 11+
            ctypes.byref(text),
            ctypes.sizeof(text),
        )
    except Exception:
        pass

# Handler d'exception global
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


def create_colored_svg_icon(name, color="#ffffff"):
    """Create an SVG icon with a specific color"""
    icons = {
        "chevron_left": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
        </svg>''',
        "chevron_right": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"></polyline>
        </svg>''',
    }

    svg_template = icons.get(name, "")
    if not svg_template:
        return QIcon()

    svg = svg_template.format(color=color)
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    pixmap.loadFromData(svg.encode(), "SVG")
    return QIcon(pixmap)


def create_colored_nav_icon(name, color="#ffffff"):
    """Create navigation icons with specific colors - not using currentColor"""
    icons = {
        "search": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>''',
        "queue": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round">
            <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><circle cx="3.5" cy="6" r="0.5" fill="{color}"/><circle cx="3.5" cy="12" r="0.5" fill="{color}"/><circle cx="3.5" cy="18" r="0.5" fill="{color}"/>
        </svg>''',
        "settings": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2">
            <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06A1.65 1.65 0 0 0 15 19.4a1.65 1.65 0 0 0-1 .6l-.04.06a2 2 0 0 1-3.92 0L10 20a1.65 1.65 0 0 0-1-.6 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-.6-1l-.06-.04a2 2 0 0 1 0-3.92L4 10a1.65 1.65 0 0 0 .6-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-.6l.04-.06a2 2 0 0 1 3.92 0L14 4a1.65 1.65 0 0 0 1 .6 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9c.14.34.35.65.6 1l.06.04a2 2 0 0 1 0 3.92L20 14c-.25.35-.46.66-.6 1z"/>
        </svg>''',
        "logs": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/>
        </svg>''',
        "minimize": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
        </svg>''',
    }

    svg_template = icons.get(name, "")
    if not svg_template:
        return QIcon()

    svg = svg_template.format(color=color)
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    pixmap.loadFromData(svg.encode(), "SVG")
    return QIcon(pixmap)


THEMES = {
    "dark": {
        "name": "Sombre",
        "bg": "#09090b",
        "surface": "#0f0f12",
        "panel": "#18181b",
        "panel_alt": "#27272a",
        "border": "#3f3f46",
        "input": "#111113",
        "text": "#fafafa",
        "muted": "#a1a1aa",
        "disabled_bg": "#27272a",
        "disabled_text": "#71717a",
        "accent": "#f59e0b",
        "accent_hover": "#d97706",
        "accent_text": "#18181b",
        "ring": "#f59e0b",
    },
    "light": {
        "name": "Clair",
        "bg": "#f5f5f5",
        "surface": "#ffffff",
        "panel": "#f0f0f0",
        "panel_alt": "#e8e8e8",
        "border": "#d0d0d0",
        "input": "#ffffff",
        "text": "#1a1a1a",
        "muted": "#666666",
        "disabled_bg": "#e8e8e8",
        "disabled_text": "#999999",
        "accent": "#f59e0b",
        "accent_hover": "#d97706",
        "accent_text": "#ffffff",
        "ring": "#d97706",
    },
}

# Import MinimalWindow here to avoid circular imports
from app.ui.minimal_window import MinimalWindow


class Downloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Downloader Studio")
        self.setWindowIcon(QIcon(resource_path(os.path.join("assets", "downloader-studio-logo.ico"))))
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 700)

        self.theme_name = "dark"
        self.theme = THEMES[self.theme_name]
        self.color_bg = self.theme["bg"]
        self.color_accent = self.theme["accent"]
        self.color_secondary = self.theme["panel"]
        self.nav_buttons = []
        self.sidebar_expanded = True
        self.minimal_window = None
        self.is_minimal_mode = False

        # Engine de téléchargement
        self.download_engine = DownloadEngine()
        self.load_app_settings()

        # Setup UI
        self.setup_ui()
        self.apply_theme(self.theme_name)

        # Logs
        from i18n import t
        self.logs_page.add_log(t("app_started"))

    def setup_ui(self):
        # Widget central avec layout
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Custom title bar with minimal mode button
        title_bar = self.create_title_bar()
        main_layout.addWidget(title_bar)

        # Main content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar container
        self.sidebar_container = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)

        # Sidebar navigation
        sidebar = self.create_sidebar()
        self.sidebar_layout.addWidget(sidebar)
        self.sidebar_container.setLayout(self.sidebar_layout)
        content_layout.addWidget(self.sidebar_container)

        # Pages stacked
        self.stacked = QStackedWidget()
        self.search_page = SearchPage(self.download_engine, self)
        self.queue_page = QueuePage(self.download_engine, self)
        self.settings_page = SettingsPage(self.download_engine, self)
        self.logs_page = LogsPage(self)

        self.stacked.addWidget(self.search_page)
        self.stacked.addWidget(self.queue_page)
        self.stacked.addWidget(self.settings_page)
        self.stacked.addWidget(self.logs_page)
        self.stacked.setCurrentIndex(0)

        content_layout.addWidget(self.stacked, 1)

        # Add content to main layout
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # Connexions
        self.download_engine.log_signal.connect(self.logs_page.add_log)
        self.download_engine.queue_updated.connect(self.update_queue_badge)
        self.download_engine.progress_updated.connect(self.update_progress_display)
        self.update_nav_state(0)
        self.update_queue_badge()

        # Raccourci clavier pour mode minimaliste
        QShortcut(QKeySequence("Ctrl+M"), self, self.toggle_minimal_mode)

    def create_title_bar(self):
        """Crée une barre de titre custom"""
        title_bar = QWidget()
        title_bar.setMaximumHeight(1)
        title_bar.setStyleSheet("background: transparent;")
        return title_bar

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        self.refresh_sidebar()

    def refresh_sidebar(self):
        self.nav_buttons = []
        self.queue_badges = {}

        # Nettoie le layout
        while self.sidebar_layout.count():
            widget = self.sidebar_layout.takeAt(0).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

        # Crée la nouvelle sidebar (cela remplira nav_buttons)
        sidebar = self.create_sidebar()
        self.sidebar_layout.addWidget(sidebar)

        # Met à jour l'état de navigation avec les nouveaux boutons
        if self.nav_buttons:
            self.update_nav_state(self.stacked.currentIndex())

    def create_sidebar(self):
        self.nav_buttons = []
        self.queue_badges = {}
        self.sidebar = QWidget()
        self.sidebar.setStyleSheet(f"background: {self.theme['panel']};")

        if self.sidebar_expanded:
            self.sidebar.setMaximumWidth(200)
            self.sidebar.setMinimumWidth(200)
        else:
            self.sidebar.setMaximumWidth(80)
            self.sidebar.setMinimumWidth(80)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(0)

        if self.sidebar_expanded:
            # Logo & Title Section (expanded) - horizontal layout
            header_layout = QHBoxLayout()
            header_layout.setSpacing(12)
            header_layout.setContentsMargins(0, 0, 0, 0)

            header_layout.addStretch()

            # Logo on the left
            self.logo_label = QLabel()
            self.logo_label.setAlignment(Qt.AlignCenter)
            logo = QPixmap(resource_path(os.path.join("assets", "downloader-studio-logo.png")))
            if not logo.isNull():
                self.logo_label.setPixmap(logo.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_label.setMinimumWidth(40)
            self.logo_label.setMaximumWidth(40)
            header_layout.addWidget(self.logo_label)

            # Separator line
            separator_vertical = QWidget()
            separator_vertical.setStyleSheet(f"background: {self.theme['border']};")
            separator_vertical.setMinimumWidth(1)
            separator_vertical.setMaximumWidth(1)
            header_layout.addWidget(separator_vertical)

            # Title section on the right
            title_layout = QVBoxLayout()
            title_layout.setSpacing(2)
            title_layout.setContentsMargins(0, 0, 0, 0)

            downloader_label = QLabel("Downloader")
            downloader_label.setStyleSheet(f"""
                color: {self.theme['text']};
                font-weight: 700;
                font-size: 12px;
                background: transparent;
            """)
            title_layout.addWidget(downloader_label)

            # STUDIO with letter spacing
            studio_label = QLabel("S T U D I O")
            studio_label.setStyleSheet(f"""
                color: {self.theme['accent']};
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 2px;
                background: transparent;
            """)
            title_layout.addWidget(studio_label)

            title_container = QWidget()
            title_container.setLayout(title_layout)
            header_layout.addWidget(title_container)

            header_layout.addStretch()

            layout.addLayout(header_layout)
            layout.addSpacing(12)

            # Separator line under logo
            separator_top = QWidget()
            separator_top.setStyleSheet(f"background: {self.theme['border']};")
            separator_top.setMinimumHeight(1)
            separator_top.setMaximumHeight(1)
            layout.addWidget(separator_top)
            layout.addSpacing(16)
        else:
            # Logo only (compact)
            self.logo_label = QLabel()
            self.logo_label.setAlignment(Qt.AlignCenter)
            logo = QPixmap(resource_path(os.path.join("assets", "downloader-studio-logo.png")))
            if not logo.isNull():
                self.logo_label.setPixmap(logo.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(self.logo_label)
            layout.addSpacing(16)

        # Navigation buttons
        buttons_info = get_nav_labels()

        nav_layout = QVBoxLayout()
        nav_layout.setSpacing(8)
        nav_layout.setContentsMargins(0, 0, 0, 0)

        # Factory function to create click handlers with proper closure
        def make_switch_handler(idx):
            return lambda: self.switch_page(idx)

        for text, page_idx, icon_name in buttons_info:
            btn_wrapper = QWidget()
            btn_wrapper.setMinimumHeight(44)
            btn_wrapper.setMaximumHeight(44)
            btn_wrapper.setStyleSheet("background: transparent;")

            if self.sidebar_expanded:
                btn_h_layout = QHBoxLayout()
                btn_h_layout.setContentsMargins(8, 6, 8, 6)
                btn_h_layout.setSpacing(12)

                btn = QPushButton()
                # Use gray color for inactive icons
                inactive_color = "#a8a8b0" if self.theme.get("text") == "#fafafa" else "#a8a8a8"
                btn.setIcon(create_colored_nav_icon(icon_name, inactive_color))
                btn.setIconSize(QSize(18, 18))
                btn.setText(text)
                btn.setStyleSheet(self.nav_button_style(active=False))
                btn.setCursor(Qt.PointingHandCursor)
                btn.setMinimumHeight(36)
                btn.clicked.connect(make_switch_handler(page_idx))
                self.nav_buttons.append(btn)

                btn_h_layout.addWidget(btn, 1)

                if page_idx == 1:
                    badge_container = QWidget()
                    badge_layout = QHBoxLayout()
                    badge_layout.setContentsMargins(0, 0, 0, 0)
                    badge_layout.setSpacing(0)
                    badge_layout.setAlignment(Qt.AlignCenter)

                    self.queue_badge = QLabel()
                    self.queue_badge.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    self.queue_badge.setVisible(False)
                    self.queue_badge.setMinimumWidth(26)
                    self.queue_badge.setMinimumHeight(26)
                    self.queue_badge.setMaximumWidth(26)
                    self.queue_badge.setMaximumHeight(26)
                    badge_layout.addWidget(self.queue_badge)
                    badge_container.setLayout(badge_layout)
                    btn_h_layout.addWidget(badge_container)
                    self.queue_badges[page_idx] = self.queue_badge

                btn_wrapper.setLayout(btn_h_layout)
            else:
                # Compact mode - just icons centered
                btn_h_layout = QHBoxLayout()
                btn_h_layout.setContentsMargins(0, 6, 0, 6)
                btn_h_layout.setSpacing(0)
                btn_h_layout.setAlignment(Qt.AlignCenter)

                btn = QPushButton()
                # Use gray color for inactive icons
                inactive_color = "#a8a8b0" if self.theme.get("text") == "#fafafa" else "#a8a8a8"
                btn.setIcon(create_colored_nav_icon(icon_name, inactive_color))
                btn.setIconSize(QSize(20, 20))
                btn.setText("")
                btn.setToolTip(text)
                btn.setStyleSheet(self.nav_button_style_compact(active=False))
                btn.setCursor(Qt.PointingHandCursor)
                btn.setMinimumSize(36, 36)
                btn.setMaximumSize(36, 36)
                btn.clicked.connect(make_switch_handler(page_idx))
                self.nav_buttons.append(btn)

                btn_h_layout.addWidget(btn)
                btn_wrapper.setLayout(btn_h_layout)

            nav_layout.addWidget(btn_wrapper)

        # Add minimal mode button to navigation
        minimal_wrapper = QWidget()
        minimal_wrapper.setMinimumHeight(44)
        minimal_wrapper.setMaximumHeight(44)
        minimal_wrapper.setStyleSheet("background: transparent;")

        if self.sidebar_expanded:
            minimal_h_layout = QHBoxLayout()
            minimal_h_layout.setContentsMargins(8, 6, 8, 6)
            minimal_h_layout.setSpacing(12)

            self.minimal_mode_btn = QPushButton()
            # Use gray color for inactive icon
            inactive_color = "#a8a8b0" if self.theme.get("text") == "#fafafa" else "#a8a8a8"
            self.minimal_mode_btn.setIcon(create_colored_nav_icon("minimize", inactive_color))
            self.minimal_mode_btn.setIconSize(QSize(20, 20))
            from i18n import t
            self.minimal_mode_btn.setText(t("minimal_mode"))
            self.minimal_mode_btn.setStyleSheet(self.nav_button_style(active=False))
            self.minimal_mode_btn.setCursor(Qt.PointingHandCursor)
            self.minimal_mode_btn.setMinimumHeight(36)
            self.minimal_mode_btn.clicked.connect(self.toggle_minimal_mode)

            minimal_h_layout.addWidget(self.minimal_mode_btn, 1)
            minimal_wrapper.setLayout(minimal_h_layout)
        else:
            minimal_h_layout = QHBoxLayout()
            minimal_h_layout.setContentsMargins(0, 6, 0, 6)
            minimal_h_layout.setSpacing(0)
            minimal_h_layout.setAlignment(Qt.AlignCenter)

            self.minimal_mode_btn = QPushButton()
            # Use gray color for inactive icon
            inactive_color = "#a8a8b0" if self.theme.get("text") == "#fafafa" else "#a8a8a8"
            self.minimal_mode_btn.setIcon(create_colored_nav_icon("minimize", inactive_color))
            self.minimal_mode_btn.setIconSize(QSize(22, 22))
            self.minimal_mode_btn.setText("")
            from i18n import t
            self.minimal_mode_btn.setToolTip(t("minimal_mode"))
            self.minimal_mode_btn.setStyleSheet(self.nav_button_style_compact(active=False))
            self.minimal_mode_btn.setCursor(Qt.PointingHandCursor)
            self.minimal_mode_btn.setMinimumSize(36, 36)
            self.minimal_mode_btn.setMaximumSize(36, 36)
            self.minimal_mode_btn.clicked.connect(self.toggle_minimal_mode)

            minimal_h_layout.addWidget(self.minimal_mode_btn)
            minimal_wrapper.setLayout(minimal_h_layout)

        nav_layout.addWidget(minimal_wrapper)

        layout.addLayout(nav_layout)
        layout.addSpacing(16)

        if self.sidebar_expanded:
            # Separator line
            separator = QWidget()
            separator.setStyleSheet(f"background: {self.theme['border']};")
            separator.setMinimumHeight(1)
            separator.setMaximumHeight(1)
            layout.addWidget(separator)

            layout.addSpacing(16)

        layout.addStretch()

        if self.sidebar_expanded:
            # Separator line before footer
            separator_bottom = QWidget()
            separator_bottom.setStyleSheet(f"background: {self.theme['border']};")
            separator_bottom.setMinimumHeight(1)
            separator_bottom.setMaximumHeight(1)
            layout.addWidget(separator_bottom)

            layout.addSpacing(12)

            # Toggle button at the bottom with padding
            toggle_btn_container = QWidget()
            toggle_btn_layout = QHBoxLayout()
            toggle_btn_layout.setContentsMargins(12, 0, 12, 0)
            toggle_btn_layout.setSpacing(0)

            # Store initial icon color for toggle
            self.toggle_icon_normal = "#ffffff" if self.theme_name == "dark" else "#1a1a1a"
            self.toggle_icon_hover = self.theme['accent_text']

            self.toggle_sidebar_btn = QPushButton()
            self.toggle_sidebar_btn.setIcon(create_colored_svg_icon("chevron_left", self.toggle_icon_normal))
            self.toggle_sidebar_btn.setIconSize(QSize(18, 18))
            from i18n import t
            self.toggle_sidebar_btn.setText(t("collapse"))
            self.toggle_sidebar_btn.setToolTip(t("collapse_sidebar"))

            self.toggle_sidebar_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.theme['panel_alt']};
                    color: {self.theme['text']};
                    border: none;
                    border-radius: 6px;
                    padding: 10px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background: {self.theme['accent']};
                    color: {self.theme['accent_text']};
                }}
            """)
            self.toggle_sidebar_btn.setMinimumHeight(36)
            self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)

            # Connect hover events to update icon color
            class ToggleButtonWithHover(QPushButton):
                def enterEvent(self, event):
                    self.main_window.toggle_sidebar_btn.setIcon(
                        create_colored_svg_icon("chevron_left", self.main_window.toggle_icon_hover)
                    )
                    super().enterEvent(event)

                def leaveEvent(self, event):
                    self.main_window.toggle_sidebar_btn.setIcon(
                        create_colored_svg_icon("chevron_left", self.main_window.toggle_icon_normal)
                    )
                    super().leaveEvent(event)

            # Replace the button with hover-aware version
            old_btn = self.toggle_sidebar_btn
            self.toggle_sidebar_btn = ToggleButtonWithHover()
            self.toggle_sidebar_btn.main_window = self
            self.toggle_sidebar_btn.setIcon(create_colored_svg_icon("chevron_left", self.toggle_icon_normal))
            self.toggle_sidebar_btn.setIconSize(QSize(18, 18))
            self.toggle_sidebar_btn.setText(t("collapse"))
            self.toggle_sidebar_btn.setToolTip(t("collapse_sidebar"))
            self.toggle_sidebar_btn.setStyleSheet(old_btn.styleSheet())
            self.toggle_sidebar_btn.setMinimumHeight(36)
            self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)

            toggle_btn_layout.addWidget(self.toggle_sidebar_btn)
            toggle_btn_container.setLayout(toggle_btn_layout)
            toggle_btn_container.setStyleSheet("background: transparent;")
            layout.addWidget(toggle_btn_container)

            layout.addSpacing(12)

            # Separator before credits
            separator_credits = QWidget()
            separator_credits.setStyleSheet(f"background: {self.theme['border']};")
            separator_credits.setMinimumHeight(1)
            separator_credits.setMaximumHeight(1)
            layout.addWidget(separator_credits)

            layout.addSpacing(8)

            # Footer section
            self.credit_label = QLabel("BS Studio - V2.11")
            self.credit_label.setAlignment(Qt.AlignCenter)
            self.credit_label.setStyleSheet(f"font-size: 10px; color: {self.theme['muted']}; background: transparent;")
            layout.addWidget(self.credit_label)
        else:
            # Compact mode - circular progress indicator
            self.progress_circle = QLabel()
            self.progress_circle.setAlignment(Qt.AlignCenter)
            self.progress_circle.setMinimumSize(44, 44)
            self.progress_circle.setMaximumSize(44, 44)
            self.progress_circle.setStyleSheet(f"""
                QLabel {{
                    background: transparent;
                    color: {self.theme['accent']};
                    font-weight: 700;
                    font-size: 10px;
                }}
            """)
            self.progress_circle.setVisible(False)
            layout.addWidget(self.progress_circle, alignment=Qt.AlignCenter)

            layout.addSpacing(12)

            # Toggle button at the bottom in compact mode - white icon
            toggle_btn_compact = QPushButton()
            toggle_btn_compact.setIcon(create_colored_svg_icon("chevron_right", "#ffffff"))
            toggle_btn_compact.setIconSize(QSize(16, 16))
            from i18n import t
            toggle_btn_compact.setToolTip(t("expand_sidebar"))
            toggle_btn_compact.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {self.theme['muted']};
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                }}
                QPushButton:hover {{
                    background: {self.theme['panel_alt']};
                    color: {self.theme['accent']};
                }}
            """)
            toggle_btn_compact.setMinimumSize(32, 32)
            toggle_btn_compact.setMaximumSize(32, 32)
            toggle_btn_compact.clicked.connect(self.toggle_sidebar)
            layout.addWidget(toggle_btn_compact, alignment=Qt.AlignCenter)

        self.sidebar.setLayout(layout)
        return self.sidebar

    def nav_button_style(self, active=False):
        t = self.theme
        border_left = f"4px solid {t['accent']}" if active else "4px solid transparent"
        # Inactive: lighter color, Active: full color
        color = t["text"] if active else "#a8a8b0" if t.get("text") == "#fafafa" else "#a8a8a8"
        return f"""
            QPushButton {{
                background: transparent;
                color: {color};
                border: none;
                border-left: {border_left};
                border-radius: 0px;
                padding: 10px 6px 10px 8px;
                font-size: 12px;
                font-weight: 600;
                text-align: left;
            }}
            QPushButton:hover {{
                background: transparent;
                color: {t["text"]};
            }}
            QPushButton:pressed {{
                color: {t["accent"]};
            }}
        """

    def nav_button_style_compact(self, active=False):
        t = self.theme
        color = t["accent"] if active else "#a8a8b0" if t.get("text") == "#fafafa" else "#a8a8a8"
        background = t["panel_alt"] if active else "transparent"
        return f"""
            QPushButton {{
                background: {background};
                color: {color};
                border: none;
                border-radius: 8px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background: {t["panel_alt"]};
                color: {t["accent"]};
            }}
            QPushButton:pressed {{
                color: {t["accent"]};
            }}
        """

    def update_nav_state(self, active_idx):
        icon_names = ["search", "queue", "settings", "logs"]
        for idx, button in enumerate(self.nav_buttons):
            is_active = idx == active_idx
            if self.sidebar_expanded:
                button.setStyleSheet(self.nav_button_style(active=is_active))
            else:
                button.setStyleSheet(self.nav_button_style_compact(active=is_active))

            # Update icon color based on active state
            if idx < len(icon_names):
                icon_name = icon_names[idx]
                if is_active:
                    icon_color = "#ffffff" if self.theme.get("text") == "#fafafa" else "#f59e0b"
                else:
                    icon_color = "#a8a8b0" if self.theme.get("text") == "#fafafa" else "#a8a8a8"
                button.setIcon(create_colored_nav_icon(icon_name, icon_color))

    def update_queue_badge(self):
        queue_count = len(self.download_engine.queue)
        if hasattr(self, 'queue_badge'):
            if queue_count > 0:
                t = self.theme
                if queue_count > 9:
                    badge_text = f"1/+{queue_count - 1}"
                    font_size = "8px"
                else:
                    badge_text = str(queue_count)
                    font_size = "10px"

                self.queue_badge.setText(badge_text)
                self.queue_badge.setStyleSheet(f"""
                    QLabel {{
                        background: {t['accent']};
                        color: {t['accent_text']};
                        border-radius: 12px;
                        font-weight: 700;
                        font-size: {font_size};
                        padding: 2px 0px;
                    }}
                """)
                self.queue_badge.setVisible(True)
            else:
                self.queue_badge.setVisible(False)

    def update_progress_display(self, current, _total):
        if self.sidebar_expanded:
            if hasattr(self, 'progress_bar'):
                if self.download_engine.current_task:
                    self.progress_bar.setValue(current)
                    self.progress_bar.setVisible(True)
                else:
                    self.progress_bar.setVisible(False)
        else:
            if hasattr(self, 'progress_circle'):
                if self.download_engine.current_task:
                    self.progress_circle.setText(f"{current}%")
                    self.progress_circle.setVisible(True)
                else:
                    self.progress_circle.setVisible(False)

    def switch_page(self, idx):
        self.stacked.setCurrentIndex(idx)
        self.update_nav_state(idx)
        if idx == 0 and hasattr(self, "search_page"):
            self.search_page.refresh_from_settings()

    def toggle_minimal_mode(self):
        if self.is_minimal_mode:
            self.exit_minimal_mode()
        else:
            self.enter_minimal_mode()

    def enter_minimal_mode(self):
        """Basculer vers le mode minimaliste"""
        self.is_minimal_mode = True
        self.hide()

        self.minimal_window = MinimalWindow(self, self.theme)
        self.minimal_window.back_to_desktop.connect(self.exit_minimal_mode)
        self.minimal_window.download_requested.connect(self.on_minimal_download)
        self.minimal_window.show()

    def exit_minimal_mode(self):
        """Revenir au mode Desktop"""
        self.is_minimal_mode = False
        if self.minimal_window:
            self.minimal_window.close()
            self.minimal_window = None
        self.show()
        self.raise_()
        self.activateWindow()

    def on_minimal_download(self, url):
        """Gérer le téléchargement depuis la fenêtre minimaliste"""
        self.search_page.search_input.setText(url)
        self.search_page.search()
        self.stacked.setCurrentIndex(0)
        self.exit_minimal_mode()

    def showEvent(self, event):
        super().showEvent(event)
        self.apply_title_bar_theme()

    def closeEvent(self, event):
        """Arrête les threads avant fermeture"""
        self.save_app_settings()
        try:
            if self.download_engine.current_worker:
                if self.download_engine.current_worker.isRunning():
                    self.download_engine.current_worker.quit()
                    self.download_engine.current_worker.wait(500)
        except:
            pass
        QApplication.quit()
        event.accept()

    def load_stylesheet(self):
        t = self.theme
        check_icon = resource_path(os.path.join("assets", "check-mark.svg")).replace("\\", "/")
        style = f"""
        QMainWindow {{
            background: {t["bg"]};
        }}
        QLabel {{
            color: {t["text"]};
            background: transparent;
        }}
        QLineEdit, QComboBox, QSpinBox {{
            background: {t["input"]};
            color: {t["text"]};
            border: 1px solid {t["border"]};
            border-radius: 6px;
            padding: 9px 10px;
            font-size: 12px;
        }}
        QLineEdit::placeholder {{
            color: {t["muted"]};
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {t["ring"]};
            background: {t["surface"]};
        }}
        QLineEdit:read-only {{
            background: {t["panel"]};
            color: {t["muted"]};
        }}
        QComboBox::drop-down {{
            width: 28px;
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background: {t["surface"]};
            color: {t["text"]};
            border: 1px solid {t["border"]};
            selection-background-color: {t["panel_alt"]};
            selection-color: {t["text"]};
        }}
        QPushButton {{
            background: {t["accent"]};
            color: {t["accent_text"]};
            border: 1px solid {t["accent"]};
            border-radius: 6px;
            padding: 10px 16px;
            font-weight: 700;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background: {t["accent_hover"]};
            border: 1px solid {t["accent_hover"]};
        }}
        QPushButton:disabled {{
            background: {t["disabled_bg"]};
            color: {t["disabled_text"]};
            border: 1px solid {t["border"]};
        }}
        QPushButton#selectAllBtn {{
            background: transparent;
            color: {t["accent"]};
            border: 1px solid {t["accent"]};
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 11px;
            font-weight: 600;
        }}
        QPushButton#selectAllBtn:hover {{
            background: {t["accent"]};
            color: {t["accent_text"]};
        }}
        QCheckBox {{
            color: {t["text"]};
            spacing: 9px;
            font-size: 12px;
            padding: 4px 0;
            background: transparent;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid {t["border"]};
            background: {t["input"]};
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {t["ring"]};
        }}
        QCheckBox::indicator:checked {{
            background: {t["accent"]};
            border: 1px solid {t["accent"]};
            image: url("{check_icon}");
        }}
        QCheckBox::indicator:checked:disabled {{
            background: {t["disabled_bg"]};
            border: 1px solid {t["border"]};
        }}
        QListWidget, QTextEdit {{
            background: {t["surface"]};
            color: {t["text"]};
            border: 1px solid {t["border"]};
            border-radius: 6px;
        }}
        QListWidget::item {{
            color: {t["text"]};
            padding: 8px;
            border-bottom: 1px solid {t["border"]};
        }}
        QListWidget::item:selected {{
            background: {t["panel_alt"]};
            color: {t["text"]};
        }}
        QListWidget::item:hover {{
            background: {t["panel"]};
        }}
        QProgressBar {{
            background: {t["panel"]};
            color: {t["text"]};
            border: 1px solid {t["border"]};
            border-radius: 6px;
            height: 20px;
            text-align: center;
            font-weight: 600;
            font-size: 11px;
        }}
        QProgressBar::chunk {{
            background: {t["accent"]};
            border-radius: 4px;
            margin: 1px;
        }}
        QScrollBar:vertical {{
            background: {t["panel"]};
            width: 12px;
            border: none;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {t["panel_alt"]};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {t["border"]};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            background: {t["panel"]};
            height: 12px;
            border: none;
            border-radius: 6px;
        }}
        QScrollBar::handle:horizontal {{
            background: {t["panel_alt"]};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {t["border"]};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
        self.setStyleSheet(style)

    def change_language(self, language_code):
        """Change language and update UI immediately"""
        from i18n import set_language
        from app.signals import signal_manager
        set_language(language_code)
        self.refresh_sidebar()
        # Recreate all pages with new language
        self.recreate_pages()
        # Notify all pages that language changed
        signal_manager.language_changed.emit(language_code)

    def recreate_pages(self):
        """Recreate all pages to apply language changes"""
        # Get current page index
        current_index = self.stacked.currentIndex()

        # Remove old pages
        old_pages = []
        while self.stacked.count():
            page = self.stacked.widget(0)
            self.stacked.removeWidget(page)
            old_pages.append(page)

        # Recreate pages with new language
        self.search_page = SearchPage(self.download_engine, self)
        self.queue_page = QueuePage(self.download_engine, self)
        self.settings_page = SettingsPage(self.download_engine, self)
        self.logs_page = LogsPage(self)

        # Add pages back to stacked widget
        self.stacked.addWidget(self.search_page)
        self.stacked.addWidget(self.queue_page)
        self.stacked.addWidget(self.settings_page)
        self.stacked.addWidget(self.logs_page)

        # Restore current page
        self.stacked.setCurrentIndex(current_index)

        # Apply theme to new pages
        self.search_page.apply_theme()
        self.queue_page.apply_theme()
        self.settings_page.apply_theme()
        self.logs_page.apply_theme()

        for page in old_pages:
            page.setParent(None)
            page.deleteLater()

    def update_nav_labels(self):
        """Update navigation button labels with current language"""
        if not hasattr(self, 'nav_buttons'):
            return

        buttons_info = get_nav_labels()
        for btn, info in zip(self.nav_buttons, buttons_info):
            btn.setText(info[0])

    def apply_theme(self, theme_name):
        if theme_name not in THEMES:
            return

        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.color_bg = self.theme["bg"]
        self.color_accent = self.theme["accent"]
        self.color_secondary = self.theme["panel"]

        self.load_stylesheet()
        self.apply_title_bar_theme()
        if hasattr(self, "sidebar"):
            self.sidebar.setStyleSheet(f"background: {self.theme['panel']};")
        if hasattr(self, "credit_label"):
            self.credit_label.setStyleSheet(f"color: {self.theme['muted']}; font-size: 10px; background: transparent;")

        if hasattr(self, "progress_card"):
            self.progress_card.setStyleSheet(f"""
                QWidget {{
                    background: {self.theme['panel']};
                    border: 1px solid {self.theme['border']};
                    border-radius: 8px;
                }}
            """)
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    background: {self.theme['panel_alt']};
                    border: none;
                    border-radius: 3px;
                    height: 6px;
                }}
                QProgressBar::chunk {{
                    background: {self.theme['accent']};
                    border-radius: 3px;
                }}
            """)
        if hasattr(self, "nav_buttons"):
            self.update_nav_state(self.stacked.currentIndex() if hasattr(self, "stacked") else 0)

        # Update toggle sidebar button icon color
        if hasattr(self, "toggle_sidebar_btn"):
            icon_color = "#ffffff" if self.theme_name == "dark" else "#1a1a1a"
            self.toggle_sidebar_btn.setIcon(create_colored_svg_icon("chevron_left", icon_color))

        for attr in ("search_page", "queue_page", "settings_page", "logs_page"):
            page = getattr(self, attr, None)
            if page and hasattr(page, "apply_theme"):
                page.apply_theme()

    def load_app_settings(self):
        path = settings_path()
        if not os.path.exists(path):
            return

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except Exception:
            return

        theme_name = data.get("theme")
        if theme_name in THEMES:
            self.theme_name = theme_name
            self.theme = THEMES[theme_name]

        saved_output_dir = data.get("output_dir")
        old_project_default = os.path.abspath(".")
        if saved_output_dir and os.path.abspath(saved_output_dir) != old_project_default:
            self.download_engine.output_dir = saved_output_dir
        else:
            self.download_engine.output_dir = DEFAULT_OUTPUT_DIR
        self.download_engine.quality = data.get("quality", self.download_engine.quality)
        self.download_engine.audio_quality = data.get("audio_quality", self.download_engine.audio_quality)

        sources = data.get("sources_enabled")
        if isinstance(sources, dict):
            self.download_engine.sources_enabled.update({
                key: bool(value)
                for key, value in sources.items()
                if key in self.download_engine.sources_enabled
            })

        formats = data.get("enabled_formats")
        allowed = {"mp3", "mp4", "wav", "m4a"}
        if isinstance(formats, list):
            cleaned = [fmt for fmt in formats if fmt in allowed]
            if cleaned:
                self.download_engine.enabled_formats = cleaned

        language = data.get("language")
        if language:
            from i18n import set_language
            set_language(language)

    def save_app_settings(self):
        from i18n import get_translator
        translator = get_translator()
        data = {
            "theme": self.theme_name,
            "language": translator.language,
            "output_dir": self.download_engine.output_dir,
            "sources_enabled": self.download_engine.sources_enabled,
            "enabled_formats": self.download_engine.enabled_formats,
            "quality": self.download_engine.quality,
            "audio_quality": self.download_engine.audio_quality,
        }
        try:
            with open(settings_path(), "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Unable to save settings: %s", exc)

    def apply_title_bar_theme(self):
        if not hasattr(self, "theme"):
            return

        if self.theme_name == "dark":
            set_windows_title_bar_theme(self, True, "#09090b", "#fafafa")
        else:
            set_windows_title_bar_theme(self, False, "#f8fafc", "#18181b")


def show_splash():
    pixmap = QPixmap(420, 300)
    pixmap.fill(QColor("#0a0a0a"))

    logo = QPixmap(resource_path(os.path.join("assets", "downloader-studio-logo.png")))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)

    if not logo.isNull():
        logo = logo.scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap((pixmap.width() - logo.width()) // 2, 46, logo)

    painter.setPen(QColor("#f59e0b"))
    title_font = QFont("Segoe UI", 18, QFont.Bold)
    painter.setFont(title_font)
    painter.drawText(0, 205, pixmap.width(), 34, Qt.AlignCenter, "Downloader Studio")

    painter.setPen(QColor("#888888"))
    meta_font = QFont("Segoe UI", 10)
    painter.setFont(meta_font)
    painter.drawText(0, 240, pixmap.width(), 24, Qt.AlignCenter, "BS Studio - V2.11")
    painter.end()

    splash = QSplashScreen(pixmap)
    splash.setWindowFlag(Qt.WindowStaysOnTopHint)
    splash.show()
    return splash


if __name__ == '__main__':
    app = QApplication(sys.argv)

    splash = show_splash()
    window = Downloader()

    def show_main_window():
        window.show()
        if splash:
            splash.finish(window)

    QTimer.singleShot(2000, show_main_window)

    sys.exit(app.exec_())
