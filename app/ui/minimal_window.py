from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QFrame
)
from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QDrag
from PyQt5.QtWidgets import QApplication
from app.utils.resources import resource_path
from app.utils.icons import create_svg_icon, create_colored_svg_icon
from i18n import t
import os
import sys


def create_svg_icon(name):
    icons = {
        "expand": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
        </svg>''',
        "download": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>''',
    }

    svg = icons.get(name, "")
    if not svg:
        return QIcon()

    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    pixmap.loadFromData(svg.encode(), "SVG")
    return QIcon(pixmap)


class MinimalWindow(QMainWindow):
    back_to_desktop = pyqtSignal()
    download_requested = pyqtSignal(str)

    def __init__(self, parent, theme):
        super().__init__()
        self.parent_window = parent
        self.theme = theme
        self.drag_position = None
        self.setWindowTitle(f"Downloader - {t('minimal_mode')}")
        self.setWindowIcon(QIcon(resource_path(os.path.join("assets", "downloader-studio-logo.ico"))))
        self.setGeometry(100, 100, 550, 110)
        self.setMinimumSize(450, 100)
        self.setMaximumHeight(110)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        # Style
        self.apply_theme()

        # Central widget
        central = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        # Title bar custom
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 8)
        title_layout.setSpacing(8)

        title_label = QLabel(t("download"))
        # Grabber for dragging (left side)
        grabber = QLabel("⋮⋮")
        grabber.setStyleSheet(f"font-size: 8px; color: {self.theme['muted']}; cursor: move;")
        grabber.setMaximumWidth(16)
        title_layout.addWidget(grabber)

        title_label.setStyleSheet(f"font-weight: 700; font-size: 12px; color: {self.theme['accent']};")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Dynamic icon color based on theme for close button
        # Detect if it's dark theme by checking text color
        icon_color = "#ffffff" if self.theme.get("text") == "#fafafa" else "#1a1a1a"

        expand_btn = QPushButton()
        # Use colored SVG icon based on theme
        expand_btn.setIcon(create_colored_svg_icon("chevron_right", icon_color))
        expand_btn.setIconSize(QSize(16, 16))
        expand_btn.setToolTip(t("back_to_desktop"))
        expand_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                padding: 4px;
            }}
            QPushButton:hover {{
                background: {self.theme['panel_alt']};
                border-radius: 4px;
            }}
        """)
        expand_btn.setMinimumSize(24, 24)
        expand_btn.setMaximumSize(24, 24)
        expand_btn.clicked.connect(self.back_to_desktop.emit)
        title_layout.addWidget(expand_btn)

        layout.addLayout(title_layout)

        # Input and download button row
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)

        # URL input with drag & drop
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(t("drag_or_paste"))
        self.url_input.setMinimumHeight(40)
        self.url_input.returnPressed.connect(self.on_download_clicked)
        self.setAcceptDrops(True)
        input_layout.addWidget(self.url_input, 1)

        # Download button
        self.download_btn = QPushButton()
        self.download_btn.setIcon(create_svg_icon("download"))
        self.download_btn.setIconSize(QSize(18, 18))
        self.download_btn.setText(t("download"))
        self.download_btn.setMinimumHeight(40)
        self.download_btn.setMinimumWidth(120)
        self.download_btn.clicked.connect(self.on_download_clicked)
        input_layout.addWidget(self.download_btn)

        layout.addLayout(input_layout)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def on_download_clicked(self):
        url = self.url_input.text().strip()
        if url:
            self.download_requested.emit(url)
            self.url_input.clear()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            url = mime_data.urls()[0].toString()
            self.url_input.setText(url)
        elif mime_data.hasText():
            self.url_input.setText(mime_data.text())

    def mousePressEvent(self, event):
        if event.y() < 40:  # Title bar area
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position is not None and (event.buttons() & Qt.LeftButton):
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

    def apply_theme(self):
        t = self.theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {t['surface']};
                border: 1px solid {t['border']};
                border-radius: 8px;
            }}
            QLineEdit {{
                background: {t['input']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 12px;
                selection-background-color: {t['accent']};
            }}
            QLineEdit:focus {{
                border: 2px solid {t['accent']};
                background: {t['surface']};
            }}
            QLineEdit::placeholder {{
                color: {t['muted']};
            }}
            QPushButton {{
                background: {t['accent']};
                color: {t['accent_text']};
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {t['accent_hover']};
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
        """)
