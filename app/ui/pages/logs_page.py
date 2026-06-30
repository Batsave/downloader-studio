from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QDateTime, QSize
from PyQt5.QtGui import QTextCursor, QIcon, QPixmap
from i18n import t


def create_svg_icon(name):
    icons = {
        "trash": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line>
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


class LogsPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()
        # Connect language change signal
        from app.signals import signal_manager
        signal_manager.language_changed.connect(self.on_language_changed)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)

        self.title = QLabel(t("logs"))
        header_layout.addWidget(self.title)
        header_layout.addStretch()

        self.log_count = QLabel(t("log_entries").format(count=0))
        self.log_count.setStyleSheet("font-size: 11px; color: #888888;")
        header_layout.addWidget(self.log_count)

        layout.addLayout(header_layout)

        # Zone de logs avec meilleur styling
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        layout.addWidget(self.logs_text)

        # Contrôles améliorés
        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.clear_btn = QPushButton()
        self.clear_btn.setIcon(create_svg_icon("trash"))
        self.clear_btn.setIconSize(QSize(18, 18))
        self.clear_btn.setText(t("clear_logs"))
        self.clear_btn.setMinimumHeight(36)
        self.clear_btn.clicked.connect(self.clear_logs)

        self.export_btn = QPushButton()
        self.export_btn.setIcon(create_svg_icon("download"))
        self.export_btn.setIconSize(QSize(18, 18))
        self.export_btn.setText(t("export_logs"))
        self.export_btn.setMinimumHeight(36)
        self.export_btn.clicked.connect(self.export_logs)

        controls.addStretch()
        controls.addWidget(self.export_btn)
        controls.addWidget(self.clear_btn)
        layout.addLayout(controls)

        self.setLayout(layout)
        self.apply_theme()

    def apply_theme(self):
        t = self.parent.theme
        self.setStyleSheet(f"background: {t['bg']};")
        self.title.setStyleSheet(
            f"font-weight: 700; color: {t['accent']}; font-size: 18px; background: transparent;"
        )
        self.log_count.setStyleSheet(f"font-size: 11px; color: {t['muted']}; background: transparent;")
        self.logs_text.setStyleSheet(f"""
            QTextEdit {{
                background: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 8px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.5;
                padding: 12px;
            }}
        """)

        # Style for buttons
        button_style = f"""
            QPushButton {{
                background: {t['accent']};
                color: {t['accent_text']};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {t['accent_hover']};
            }}
            QPushButton:pressed {{
                background: {t['accent']};
                opacity: 0.8;
            }}
        """
        self.clear_btn.setStyleSheet(button_style)
        self.export_btn.setStyleSheet(button_style)

    def add_log(self, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        log_line = f"[{timestamp}] {message}"
        self.logs_text.append(log_line)

        # Update count
        line_count = self.logs_text.document().blockCount()
        self.log_count.setText(t("log_entries").format(count=line_count))

        # Scroll to bottom
        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.logs_text.setTextCursor(cursor)

    def clear_logs(self):
        self.logs_text.clear()
        self.log_count.setText(t("log_entries").format(count=0))

    def export_logs(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, t("export_logs_title"), "", "Text Files (*.txt)")
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.logs_text.toPlainText())
            self.add_log(t("logs_exported").format(path=path))

    def on_language_changed(self, language_code):
        """Handle language change - refresh UI texts"""
        self.refresh_ui_text()

    def refresh_ui_text(self):
        """Refresh all UI texts with current language"""
        from i18n import t
        self.title.setText(t("logs"))
        self.clear_btn.setText(t("clear_logs"))
        self.export_btn.setText(t("export_logs"))
        line_count = self.logs_text.document().blockCount()
        if not self.logs_text.toPlainText():
            line_count = 0
        self.log_count.setText(t("log_entries").format(count=line_count))
