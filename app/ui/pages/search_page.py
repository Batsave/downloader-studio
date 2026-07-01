from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QLabel, QCheckBox, QComboBox, QProgressBar, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap
from app.core.download_engine import DownloadTask, DownloadWorker
from i18n import t
import logging
import re

logger = logging.getLogger(__name__)


def create_svg_icon(name):
    icons = {
        "youtube": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FF0000">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
        </svg>''',
        "soundcloud": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FF7700">
            <path d="M2 13.5h1v3h-1zm2-2h1v5h-1zm2-2h1v7h-1zm2-2h1v9h-1zm2-1.5h1v10.5h-1zm2-1.5h1v12h-1zm2-1h1v13h-1zm2-.5h1v13.5h-1zm2-.5h1v14h-1zm2 1h1v12h-1zm2 1.5h1v10.5h-1zm2 2h1v9h-1zm2 2h1v7h-1zm2 2h1v5h-1zm2 2h1v3h-1z"/>
        </svg>''',
        "search": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>''',
        "plus": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>''',
        "download": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
        </svg>''',
        "settings": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06A1.65 1.65 0 0 0 15 19.4a1.65 1.65 0 0 0-1 .6l-.04.06a2 2 0 0 1-3.92 0L10 20a1.65 1.65 0 0 0-1-.6 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-.6-1l-.06-.04a2 2 0 0 1 0-3.92L4 10a1.65 1.65 0 0 0 .6-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-.6l.04-.06a2 2 0 0 1 3.92 0L14 4a1.65 1.65 0 0 0 1 .6 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9c.14.34.35.65.6 1l.06.04a2 2 0 0 1 0 3.92L20 14c-.25.35-.46.66-.6 1z"/>
        </svg>''',
        "queue": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><circle cx="3.5" cy="6" r="0.5" fill="currentColor"/><circle cx="3.5" cy="12" r="0.5" fill="currentColor"/><circle cx="3.5" cy="18" r="0.5" fill="currentColor"/>
        </svg>''',
        "logs": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="8" y1="13" x2="16" y2="13"/><line x1="8" y1="17" x2="16" y2="17"/>
        </svg>''',
        "chevron_left": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
        </svg>''',
        "chevron_right": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="9 18 15 12 9 6"></polyline>
        </svg>''',
        "minimize": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path>
        </svg>''',
    }

    svg = icons.get(name, "")
    if not svg:
        return QIcon()

    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    pixmap.loadFromData(svg.encode(), "SVG")
    return QIcon(pixmap)


class SearchThread(QThread):
    result_found = pyqtSignal(dict, str, int)
    search_finished = pyqtSignal(str, int)

    def __init__(self, engine, query, source, search_id):
        super().__init__()
        self.engine = engine
        self.query = query
        self.source = source
        self.search_id = search_id

    def run(self):
        try:
            if self.source == "YouTube":
                results = self.engine.search_youtube(self.query)
            elif self.source == "SoundCloud":
                results = self.engine.search_soundcloud(self.query)
            else:
                results = []

            for result in results:
                if result:
                    self.result_found.emit(result, self.source, self.search_id)

            self.search_finished.emit(self.source, self.search_id)
        except Exception as exc:
            logger.error("Search thread error %s: %s", self.source, exc)
            self.search_finished.emit(self.source, self.search_id)


class UrlExtractThread(QThread):
    entries_found = pyqtSignal(list, str, int)
    extract_finished = pyqtSignal(str, int)

    def __init__(self, engine, url, search_id):
        super().__init__()
        self.engine = engine
        self.url = url
        self.search_id = search_id

    def run(self):
        try:
            entries = self.engine.extract_playlist_entries(self.url)
            self.entries_found.emit(entries, self.url, self.search_id)
        except Exception as exc:
            logger.error("URL extract thread error: %s", exc)
            self.entries_found.emit([], self.url, self.search_id)
        finally:
            self.extract_finished.emit(self.url, self.search_id)


class SearchPage(QWidget):
    def __init__(self, engine, parent):
        super().__init__()
        self.engine = engine
        self.parent = parent
        self.current_results = []
        self.pending_sources = set()
        self.selected_url = None
        self.selected_title = None
        self.selected_source = None
        self.search_threads = []
        self.url_extract_thread = None
        self.active_search_id = 0
        self.search_running = False
        self.download_worker = None
        self.direct_task = None
        self.preview_selected = False
        self.setup_ui()
        self.engine.queue_updated.connect(self.update_queue_button_state)
        # Connect language change signal
        from app.signals import signal_manager
        signal_manager.language_changed.connect(self.on_language_changed)

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.create_search_panel(), 3)
        layout.addWidget(self.create_details_panel(), 2)
        self.setLayout(layout)
        self.apply_theme()

    def create_search_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.search_title = QLabel(t("search"))
        layout.addWidget(self.search_title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(t("search_placeholder"))
        self.search_input.returnPressed.connect(self.search)
        layout.addWidget(self.search_input)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(10)

        self.format_combo = QComboBox()
        self.format_combo.addItems(self.engine.enabled_formats)
        self.format_combo.setCurrentText("mp3")
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        options_layout.addWidget(self._field("format_label", self.format_combo), 1)

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["4K (2160p)", "Full HD (1080p)", "HD (720p)", "SD (480p)", "Auto"])
        self.quality_combo.setCurrentText(self.engine.quality)
        options_layout.addWidget(self._field("video_quality_label", self.quality_combo), 1)

        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems(["320kbps", "256kbps", "192kbps", "128kbps"])
        self.bitrate_combo.setCurrentText(self.engine.audio_quality)
        options_layout.addWidget(self._field("audio_bitrate_label", self.bitrate_combo), 1)
        layout.addLayout(options_layout)

        source_layout = QHBoxLayout()
        source_layout.setSpacing(12)
        self.yt_check = self._source_check(t("youtube"), "youtube", self.engine.sources_enabled.get("youtube", True))
        self.sc_check = self._source_check(t("soundcloud"), "soundcloud", self.engine.sources_enabled.get("soundcloud", True))
        source_layout.addWidget(self.yt_check)
        source_layout.addWidget(self.sc_check)
        source_layout.addStretch()
        layout.addLayout(source_layout)

        self.search_btn = QPushButton(t("search_btn"))
        self.search_btn.setMinimumHeight(38)
        self.search_btn.clicked.connect(self.search)
        layout.addWidget(self.search_btn)

        self.progress_label = QLabel(t("searching"))
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(10)
        self.progress.setTextVisible(False)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        results_header_layout = QHBoxLayout()
        results_header_layout.setSpacing(10)
        self.results_header = QLabel(t("results"))
        results_header_layout.addWidget(self.results_header)
        results_header_layout.addStretch()
        self.select_all_btn = QPushButton(t("select_all"))
        self.select_all_btn.setObjectName("selectAllBtn")
        self.select_all_btn.setMinimumWidth(120)
        self.select_all_btn.setMinimumHeight(32)
        self.select_all_btn.clicked.connect(self.select_all_results)
        self.select_all_btn.setVisible(False)
        results_header_layout.addWidget(self.select_all_btn)
        layout.addLayout(results_header_layout)

        self.results_empty = QLabel(t("no_search"))
        self.results_empty.setAlignment(Qt.AlignCenter)
        self.results_empty.setWordWrap(True)
        layout.addWidget(self.results_empty, 1)

        self.results_list = QListWidget()
        self.results_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.results_list.itemClicked.connect(self.on_result_selected)
        self.results_list.itemSelectionChanged.connect(self.on_result_selection_changed)
        self.results_list.setVisible(False)
        layout.addWidget(self.results_list, 1)

        self.on_format_changed(self.format_combo.currentText())
        panel.setLayout(layout)
        return panel

    def create_details_panel(self):
        self.details_panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.details_title = QLabel(t("details"))
        layout.addWidget(self.details_title)

        self.preview_info = QLabel(t("select_result"))
        self.preview_info.setWordWrap(True)
        layout.addWidget(self.preview_info)

        self.output_label = QLabel()
        self.output_label.setWordWrap(True)
        layout.addWidget(self.output_label)

        layout.addStretch()

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.add_btn = QPushButton(t("add_to_queue"))
        self.add_btn.setIcon(create_svg_icon("plus"))
        self.add_btn.setIconSize(QSize(18, 18))
        self.add_btn.setMinimumHeight(42)
        self.add_btn.setToolTip(t("add_selected_to_queue"))
        self.add_btn.clicked.connect(self.add_to_queue)
        self.add_btn.setEnabled(False)

        self.download_btn = QPushButton(t("download_now"))
        self.download_btn.setMinimumHeight(42)
        self.download_btn.clicked.connect(self.download_direct)
        self.download_btn.setEnabled(False)

        buttons_layout.addWidget(self.add_btn, 3)
        buttons_layout.addWidget(self.download_btn, 2)
        layout.addLayout(buttons_layout)

        self.details_panel.setLayout(layout)
        self.refresh_output_label()
        return self.details_panel

    def _field(self, label_key, control):
        wrapper = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        label = QLabel(t(label_key))
        label.setObjectName("fieldLabel")
        label.setProperty("i18n_key", label_key)
        label.setStyleSheet("font-weight: 600; font-size: 11px;")
        layout.addWidget(label)
        layout.addWidget(control)
        wrapper.setLayout(layout)
        return wrapper

    def _source_check(self, text, icon_name, checked):
        check = QCheckBox(text)
        check.setIcon(create_svg_icon(icon_name))
        check.setIconSize(QSize(20, 20))
        check.setChecked(checked)
        check.setStyleSheet("font-weight: 500;")
        return check

    def apply_theme(self):
        t = self.parent.theme
        self.setStyleSheet(f"background: {t['bg']};")
        self.search_title.setStyleSheet(
            f"font-weight: 700; color: {t['accent']}; font-size: 16px; background: transparent;"
        )
        self.results_header.setStyleSheet(
            f"font-weight: 600; color: {t['accent']}; font-size: 12px; margin-top: 8px; background: transparent;"
        )
        self.details_title.setStyleSheet(
            f"font-weight: 700; color: {t['accent']}; font-size: 16px; border: none; background: transparent;"
        )
        self.details_panel.setStyleSheet(
            f"background: {t['surface']}; border-left: 1px solid {t['border']};"
        )
        self.results_empty.setStyleSheet(f"""
            color: {t['muted']};
            background: {t['surface']};
            border: 1px dashed {t['border']};
            border-radius: 6px;
            padding: 24px;
            font-size: 12px;
        """)
        self.results_list.setStyleSheet(f"""
            QListWidget {{
                background: {t['panel']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 0px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {t['border']};
            }}
            QListWidget::item:selected {{
                background: {t['panel_alt']};
                color: {t['accent']};
            }}
            QListWidget::item:hover {{
                background: {t['panel_alt']};
            }}
            QScrollBar:vertical {{
                background: {t['panel']};
                width: 16px;
                margin: 0px;
                border-left: 1px solid {t['border']};
            }}
            QScrollBar::handle:vertical {{
                background: {t['accent']};
                border-radius: 8px;
                min-height: 40px;
                margin: 4px 2px 4px 2px;
                border: none;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['accent_hover']};
            }}
            QScrollBar::handle:vertical:pressed {{
                background: {t['accent']};
            }}
            QScrollBar::add-line:vertical {{
                height: 0px;
            }}
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical {{
                background: none;
            }}
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {t['panel']};
                height: 16px;
                margin: 0px;
                border-top: 1px solid {t['border']};
            }}
            QScrollBar::handle:horizontal {{
                background: {t['accent']};
                border-radius: 8px;
                min-width: 40px;
                margin: 2px 4px 2px 4px;
                border: none;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {t['accent_hover']};
            }}
            QScrollBar::handle:horizontal:pressed {{
                background: {t['accent']};
            }}
            QScrollBar::add-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::add-page:horizontal {{
                background: none;
            }}
            QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
        self.preview_info.setStyleSheet(self.preview_style(selected=self.preview_selected))
        self.output_label.setStyleSheet(f"""
            color: {t['muted']};
            font-size: 11px;
            font-family: monospace;
            border: none;
            background: transparent;
        """)
        self.progress_label.setStyleSheet(
            f"color: {t['muted']}; font-size: 11px; background: transparent;"
        )
        self.search_btn.setStyleSheet(f"""
            QPushButton {{
                background: {t['accent']};
                color: {t['accent_text']};
                border: 1px solid {t['accent']};
                border-radius: 6px;
                padding: 10px 14px;
                font-weight: 700;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {t['accent_hover']};
                border: 1px solid {t['accent_hover']};
            }}
            QPushButton:disabled {{
                background: {t['panel_alt']};
                color: {t['muted']};
                border: 1px solid {t['border']};
            }}
        """)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background: {t['panel_alt']};
                border: 1px solid {t['border']};
                border-radius: 5px;
                height: 10px;
                min-height: 10px;
                max-height: 10px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: {t['accent']};
                border-radius: 4px;
                margin: 1px;
                width: 42px;
            }}
        """)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {t['accent']};
                color: {t['accent_text']};
                border: none;
                border-radius: 6px;
                padding: 11px 14px;
                font-weight: 700;
                font-size: 12px;
                text-align: center;
            }}
            QPushButton:hover {{
                background: {t['accent_hover']};
            }}
            QPushButton:disabled {{
                background: {t['disabled_bg']};
                color: {t['disabled_text']};
                border: 1px solid {t['border']};
            }}
        """)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background: {t['panel_alt']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 10px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {t['panel']};
            }}
            QPushButton:disabled {{
                background: {t['disabled_bg']};
                color: {t['disabled_text']};
                border: 1px solid {t['border']};
            }}
        """)
        for label in self.findChildren(QLabel):
            if label.objectName() == "fieldLabel":
                label.setStyleSheet(
                    f"font-weight: 600; color: {t['text']}; font-size: 11px; background: transparent;"
                )

    def preview_style(self, selected=False):
        t = self.parent.theme
        border = t["accent"] if selected else t["border"]
        color = t["text"] if selected else t["muted"]
        return f"""
            color: {color};
            font-size: 12px;
            line-height: 1.35;
            background: {t['panel']};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 14px;
        """

    def refresh_from_settings(self):
        self.format_combo.blockSignals(True)
        current = self.format_combo.currentText()
        self.format_combo.clear()
        self.format_combo.addItems(self.engine.enabled_formats)
        if current in self.engine.enabled_formats:
            self.format_combo.setCurrentText(current)
        elif self.engine.enabled_formats:
            self.format_combo.setCurrentText(self.engine.enabled_formats[0])
        self.format_combo.blockSignals(False)

        self.yt_check.setChecked(self.engine.sources_enabled.get("youtube", True))
        self.sc_check.setChecked(self.engine.sources_enabled.get("soundcloud", True))
        self.quality_combo.setCurrentText(self.engine.quality)
        self.bitrate_combo.setCurrentText(self.engine.audio_quality)
        self.on_format_changed(self.format_combo.currentText())
        self.refresh_output_label()

    def refresh_output_label(self):
        self.output_label.setText(t("output_folder_path").format(path=self.engine.output_dir))

    @staticmethod
    def is_direct_url(text):
        return bool(re.match(r"^https?://", text.strip(), re.IGNORECASE))

    @staticmethod
    def source_from_url(url):
        lowered = url.lower()
        if "youtube.com" in lowered or "youtu.be" in lowered:
            return "YouTube"
        if "soundcloud.com" in lowered:
            return "SoundCloud"
        if "twitch.tv" in lowered:
            return "Twitch"
        if "tiktok.com" in lowered:
            return "TikTok"
        return t("link")

    def add_result_item(self, title, url, source, duration=""):
        item_label = str(title or url)[:85]
        if duration:
            item_label = f"{item_label}  |  {duration}"

        if source == "YouTube":
            icon_name = "youtube"
        elif source == "SoundCloud":
            icon_name = "soundcloud"
        else:
            icon_name = "search"

        item = QListWidgetItem(item_label)
        item.setIcon(create_svg_icon(icon_name))
        item.setData(Qt.UserRole, url)
        item.setData(Qt.UserRole + 1, title or url)
        item.setData(Qt.UserRole + 2, source)
        item.setData(Qt.UserRole + 3, duration)
        self.results_list.addItem(item)
        return item

    def show_direct_url_result(self, url):
        self.search_running = False
        self.selected_url = None
        self.preview_selected = False
        self.current_results = []
        self.pending_sources = set()
        self.results_list.clear()
        self.results_empty.setVisible(False)
        self.results_list.setVisible(True)
        self.select_all_btn.setVisible(False)
        self.progress_label.setVisible(False)
        self.progress.setVisible(False)
        self.search_btn.setEnabled(True)
        self.search_btn.setText(t("search_btn"))

        source = self.source_from_url(url)
        title = f"{t('direct_link')} - {source}"
        item = self.add_result_item(title, url, source)
        self.results_list.setCurrentItem(item)
        self.parent.logs_page.add_log(t("direct_url_ready"))

    def start_url_extraction(self, url):
        if self.search_running:
            self.parent.logs_page.add_log(t("search_already_running"))
            return

        self.search_running = True
        self.active_search_id += 1
        search_id = self.active_search_id
        self.selected_url = None
        self.selected_title = None
        self.selected_source = None
        self.preview_selected = False
        self.current_results = []
        self.pending_sources = set()
        self.results_list.clear()
        self.results_list.setVisible(False)
        self.results_empty.setText(t("analyzing_url_results"))
        self.results_empty.setVisible(True)
        self.preview_info.setText(t("detecting_playlist"))
        self.preview_info.setStyleSheet(self.preview_style(selected=False))
        self.update_queue_button_state()
        self.download_btn.setEnabled(False)

        self.search_btn.setEnabled(False)
        self.search_btn.setText(t("analyzing"))
        self.progress_label.setText(t("analyzing_url"))
        self.progress_label.setVisible(True)
        self.progress.setVisible(True)

        self.parent.logs_page.add_log(t("analyzing_url_log").format(url=url))
        self.url_extract_thread = UrlExtractThread(self.engine, url, search_id)
        self.url_extract_thread.entries_found.connect(self.on_url_entries_found)
        self.url_extract_thread.extract_finished.connect(self.on_url_extract_finished)
        self.url_extract_thread.finished.connect(self.url_extract_thread.deleteLater)
        self.url_extract_thread.start()

    def on_url_entries_found(self, entries, url, search_id):
        if search_id != self.active_search_id:
            return

        if not entries:
            self.show_direct_url_result(url)
            return

        self.current_results = entries
        self.results_list.clear()
        self.results_empty.setVisible(False)
        self.results_list.setVisible(True)
        self.select_all_btn.setVisible(True)

        for entry in entries:
            entry_url = entry.get("webpage_url") or entry.get("url", "")
            if not entry_url:
                continue
            source = self.source_from_url(entry_url)
            duration = entry.get("duration_string") or self._format_duration(entry.get("duration"))
            self.add_result_item(entry.get("title") or entry_url, entry_url, source, duration)

        playlist_title = entries[0].get("playlist_title") or "playlist"
        count = self.results_list.count()
        self.preview_info.setText(
            f"{t('playlist_loaded').format(count=count, title=playlist_title)}\n\n"
            f"{t('select_multiple_for_queue')}"
        )
        self.preview_selected = False
        self.preview_info.setStyleSheet(self.preview_style(selected=False))
        self.update_queue_button_state()
        self.download_btn.setEnabled(False)
        self.parent.logs_page.add_log(t("playlist_detected").format(count=count))

    def on_url_extract_finished(self, url, search_id):
        if search_id != self.active_search_id:
            return

        self.search_running = False
        self.url_extract_thread = None
        self.search_btn.setEnabled(True)
        self.search_btn.setText(t("search_btn"))
        self.progress_label.setText(t("searching"))
        self.progress_label.setVisible(False)
        self.progress.setVisible(False)
        if self.results_list.count() == 0:
            self.results_empty.setText(t("no_result_found"))
            self.results_empty.setVisible(True)

    def on_format_changed(self, fmt):
        is_audio = fmt in {"mp3", "wav", "m4a"}
        is_video = fmt == "mp4"
        self.quality_combo.parentWidget().setVisible(is_video)
        self.bitrate_combo.parentWidget().setVisible(is_audio and fmt != "wav")

    def search(self):
        if self.search_running:
            self.parent.logs_page.add_log(t("search_already_running"))
            return

        query = self.search_input.text().strip()
        if not query:
            self.parent.logs_page.add_log(t("empty_query"))
            return

        if self.is_direct_url(query):
            self.start_url_extraction(query)
            return

        sources = []
        if self.yt_check.isChecked() and self.engine.sources_enabled.get("youtube", True):
            sources.append("YouTube")
        if self.sc_check.isChecked() and self.engine.sources_enabled.get("soundcloud", True):
            sources.append("SoundCloud")

        if not sources:
            self.parent.logs_page.add_log(t("no_source_active"))
            return

        self.search_running = True
        self.active_search_id += 1
        search_id = self.active_search_id
        self.selected_url = None
        self.preview_selected = False
        self.current_results = []
        self.pending_sources = set(sources)
        self.results_list.clear()
        self.results_list.setVisible(False)
        self.select_all_btn.setVisible(False)
        self.results_empty.setText(t("searching"))
        self.results_empty.setVisible(True)
        self.selected_title = None
        self.selected_source = None
        self.update_queue_button_state()
        self.download_btn.setEnabled(False)
        self.parent.logs_page.add_log(t("search_log").format(query=query))

        self.search_btn.setEnabled(False)
        self.search_btn.setText(t("searching_short"))
        self.progress_label.setVisible(True)
        self.progress.setVisible(True)

        for source in sources:
            thread = SearchThread(self.engine, query, source, search_id)
            thread.result_found.connect(self.on_result_found)
            thread.search_finished.connect(self.on_search_finished)
            thread.finished.connect(thread.deleteLater)
            thread.start()
            self.search_threads.append(thread)

    def on_result_found(self, result, source, search_id):
        if search_id != self.active_search_id:
            return

        title = result.get("title", t("untitled"))
        url = result.get("webpage_url") or result.get("url", "")
        duration = result.get("duration_string") or self._format_duration(result.get("duration"))

        if not url:
            return

        self.current_results.append(result)
        self.results_empty.setVisible(False)
        self.results_list.setVisible(True)
        self.select_all_btn.setVisible(True)

        self.add_result_item(title, url, source, duration)

    def on_search_finished(self, source, search_id):
        if search_id != self.active_search_id:
            return

        self.pending_sources.discard(source)
        self.parent.logs_page.add_log(t("source_finished").format(source=source))

        if not self.pending_sources:
            self.search_running = False
            self.search_threads = []
            self.search_btn.setEnabled(True)
            self.search_btn.setText(t("search_btn"))
            self.progress_label.setVisible(False)
            self.progress.setVisible(False)
            if self.results_list.count() == 0:
                self.results_empty.setText(t("no_result_found"))
                self.results_empty.setVisible(True)

    def on_result_selected(self, item):
        self.selected_url = item.data(Qt.UserRole)
        self.selected_title = item.data(Qt.UserRole + 1)
        self.selected_source = item.data(Qt.UserRole + 2)
        duration = item.data(Qt.UserRole + 3)

        details = [
            f"{t('title_label')}: {self.selected_title}",
            f"{t('source_label')}: {self.selected_source}",
            f"{t('format_label')}: {self.format_combo.currentText().upper()}",
        ]
        if duration:
            details.append(f"{t('duration_label')}: {duration}")
        details.append(f"URL: {self.selected_url}")

        self.preview_info.setText("\n\n".join(details))
        self.preview_selected = True
        self.preview_info.setStyleSheet(self.preview_style(selected=True))

        self.update_queue_button_state()
        self.download_btn.setEnabled(True)

    def _selected_queue_state(self):
        if not self.selected_url:
            return "none"

        current_task = getattr(self.engine, "current_task", None)
        if current_task and current_task.url == self.selected_url:
            return "running"

        for task in self.engine.queue:
            if task.url == self.selected_url:
                return "queued"

        return "ready"

    def update_queue_button_state(self):
        state = self._selected_queue_state()
        if state == "none":
            self.add_btn.setText(t("add_to_queue"))
            self.add_btn.setToolTip(t("select_result_before_queue"))
            self.add_btn.setEnabled(False)
        elif state == "queued":
            self.add_btn.setText(t("in_queue"))
            self.add_btn.setToolTip(t("result_already_queued"))
            self.add_btn.setEnabled(False)
        elif state == "running":
            self.add_btn.setText(t("running"))
            self.add_btn.setToolTip(t("result_already_downloading"))
            self.add_btn.setEnabled(False)
        else:
            self.add_btn.setText(t("add_to_queue"))
            self.add_btn.setToolTip(t("add_selected_to_queue"))
            self.add_btn.setEnabled(True)

    def _create_task(self):
        fmt = self.format_combo.currentText()
        quality = self.quality_combo.currentText() if fmt == "mp4" else self.engine.quality
        bitrate = self.bitrate_combo.currentText() if fmt in {"mp3", "m4a"} else self.engine.audio_quality
        return DownloadTask(self.selected_url, fmt, self.selected_title, quality, bitrate)

    def add_to_queue(self):
        if not self.selected_url:
            self.parent.logs_page.add_log(t("no_result_selected"))
            return
        if self._selected_queue_state() in {"queued", "running"}:
            self.update_queue_button_state()
            return

        task = self._create_task()
        if self.engine.add_task(task):
            self.parent.logs_page.add_log(
                t("added_to_queue_log").format(title=self.selected_title[:40], format=task.fmt)
            )
        self.update_queue_button_state()

    def download_direct(self):
        if not self.selected_url:
            self.parent.logs_page.add_log(t("no_result_selected"))
            return
        if self.download_worker and self.download_worker.isRunning():
            self.parent.logs_page.add_log(t("direct_download_already_running"))
            return

        task = self._create_task()
        self.direct_task = task
        self.download_btn.setEnabled(False)
        self.add_btn.setEnabled(False)
        self.parent.logs_page.add_log(
            t("download_log").format(title=self.selected_title[:40], format=task.fmt)
        )

        try:
            self.download_worker = DownloadWorker(task, self.engine.output_dir)
            self.download_worker.finished.connect(self.on_download_finished)
            self.download_worker.log.connect(self.parent.logs_page.add_log)
            self.download_worker.start()
        except Exception as exc:
            logger.error("Download error: %s", exc, exc_info=True)
            self.parent.logs_page.add_log(f"{t('error')}: {str(exc)[:50]}")
            self.add_btn.setEnabled(True)
            self.download_btn.setEnabled(True)

    def on_download_finished(self, status, msg):
        self.parent.logs_page.add_log(msg)
        if self.direct_task:
            self.engine.add_history(self.direct_task, status, msg)
            self.direct_task = None
        if self.download_worker:
            self.download_worker.quit()
            self.download_worker.wait(500)
            self.download_worker = None

        has_selection = self.selected_url is not None
        self.update_queue_button_state()
        self.download_btn.setEnabled(has_selection)

    def on_result_selected(self, item):
        self.on_result_selection_changed()

    def on_result_selection_changed(self):
        items = self.results_list.selectedItems()
        if not items:
            self.selected_url = None
            self.selected_title = None
            self.selected_source = None
            self.preview_selected = False
            self.preview_info.setText(t("select_result"))
            self.preview_info.setStyleSheet(self.preview_style(selected=False))
            self.update_queue_button_state()
            self.download_btn.setEnabled(False)
            return

        if len(items) == 1:
            item = items[0]
            self.selected_url = item.data(Qt.UserRole)
            self.selected_title = item.data(Qt.UserRole + 1)
            self.selected_source = item.data(Qt.UserRole + 2)
            duration = item.data(Qt.UserRole + 3)

            details = [
                f"{t('title_label')}: {self.selected_title}",
                f"{t('source_label')}: {self.selected_source}",
                f"{t('format_label')}: {self.format_combo.currentText().upper()}",
            ]
            if duration:
                details.append(f"{t('duration_label')}: {duration}")
            details.append(f"URL: {self.selected_url}")

            self.preview_info.setText("\n\n".join(details))
            self.preview_selected = True
            self.preview_info.setStyleSheet(self.preview_style(selected=True))
            self.download_btn.setEnabled(True)
        else:
            self.selected_url = None
            self.selected_title = None
            self.selected_source = None
            counts = self._selection_counts(items)
            details = [
                t("selected_tracks").format(count=counts["total"]),
                f"{t('format_label')}: {self.format_combo.currentText().upper()}",
                f"{t('to_add')}: {counts['ready']}",
            ]
            if counts["queued"]:
                details.append(f"{t('already_in_queue')}: {counts['queued']}")
            if counts["running"]:
                details.append(f"{t('running')}: {counts['running']}")

            self.preview_info.setText("\n\n".join(details))
            self.preview_selected = True
            self.preview_info.setStyleSheet(self.preview_style(selected=True))
            self.download_btn.setEnabled(False)

        self.update_queue_button_state()

    def _queue_state_for_url(self, url):
        if not url:
            return "none"

        current_task = getattr(self.engine, "current_task", None)
        if current_task and current_task.url == url:
            return "running"

        for task in self.engine.queue:
            if task.url == url:
                return "queued"

        return "ready"

    def _selection_counts(self, items=None):
        items = items if items is not None else self.results_list.selectedItems()
        counts = {"total": len(items), "ready": 0, "queued": 0, "running": 0}
        for item in items:
            state = self._queue_state_for_url(item.data(Qt.UserRole))
            if state in counts:
                counts[state] += 1
        return counts

    def _selected_queue_state(self):
        items = self.results_list.selectedItems()
        if not items:
            return "none"
        counts = self._selection_counts(items)
        if counts["ready"]:
            return "ready"
        if counts["running"]:
            return "running"
        if counts["queued"]:
            return "queued"
        return "none"

    def update_queue_button_state(self):
        items = self.results_list.selectedItems()
        counts = self._selection_counts(items)

        if counts["total"] == 0:
            self.add_btn.setText(t("add_to_queue"))
            self.add_btn.setToolTip(t("select_result_before_queue"))
            self.add_btn.setEnabled(False)
        elif counts["ready"] == 0:
            if counts["running"] and counts["total"] == 1:
                self.add_btn.setText(t("running"))
                self.add_btn.setToolTip(t("result_already_downloading"))
            else:
                self.add_btn.setText(t("in_queue"))
                self.add_btn.setToolTip(t("selection_already_queued"))
            self.add_btn.setEnabled(False)
        elif counts["total"] == 1:
            self.add_btn.setText(t("add_to_queue"))
            self.add_btn.setToolTip(t("add_selected_to_queue"))
            self.add_btn.setEnabled(True)
        elif counts["ready"] == counts["total"]:
            self.add_btn.setText(t("add_count_to_queue").format(count=counts["ready"]))
            self.add_btn.setToolTip(t("add_all_selected_to_queue"))
            self.add_btn.setEnabled(True)
        else:
            self.add_btn.setText(t("add_count_remaining").format(count=counts["ready"]))
            self.add_btn.setToolTip(t("add_remaining_to_queue"))
            self.add_btn.setEnabled(True)

    def _create_task_from_item(self, item):
        fmt = self.format_combo.currentText()
        quality = self.quality_combo.currentText() if fmt == "mp4" else self.engine.quality
        bitrate = self.bitrate_combo.currentText() if fmt in {"mp3", "m4a"} else self.engine.audio_quality
        return DownloadTask(
            item.data(Qt.UserRole),
            fmt,
            item.data(Qt.UserRole + 1),
            quality,
            bitrate,
        )

    def _create_task(self):
        items = self.results_list.selectedItems()
        if not items:
            return None
        return self._create_task_from_item(items[0])

    def add_to_queue(self):
        items = self.results_list.selectedItems()
        if not items:
            self.parent.logs_page.add_log(t("no_result_selected"))
            return

        added = 0
        for item in items:
            if self._queue_state_for_url(item.data(Qt.UserRole)) != "ready":
                continue
            task = self._create_task_from_item(item)
            if self.engine.add_task(task):
                added += 1

        if added == 1:
            self.parent.logs_page.add_log(t("added_one_to_queue_log"))
        elif added > 1:
            self.parent.logs_page.add_log(t("added_count_to_queue_log").format(count=added))
        self.update_queue_button_state()

    def download_direct(self):
        items = self.results_list.selectedItems()
        if len(items) != 1:
            self.parent.logs_page.add_log(t("select_one_for_download_now"))
            return
        if self.download_worker and self.download_worker.isRunning():
            self.parent.logs_page.add_log(t("direct_download_already_running"))
            return

        task = self._create_task_from_item(items[0])
        self.direct_task = task
        self.download_btn.setEnabled(False)
        self.add_btn.setEnabled(False)
        self.parent.logs_page.add_log(t("download_log").format(title=task.title[:40], format=task.fmt))

        try:
            self.download_worker = DownloadWorker(task, self.engine.output_dir)
            self.download_worker.finished.connect(self.on_download_finished)
            self.download_worker.log.connect(self.parent.logs_page.add_log)
            self.download_worker.start()
        except Exception as exc:
            logger.error("Download error: %s", exc, exc_info=True)
            self.parent.logs_page.add_log(f"{t('error')}: {str(exc)[:50]}")
            self.add_btn.setEnabled(True)
            self.download_btn.setEnabled(True)

    def on_download_finished(self, status, msg):
        self.parent.logs_page.add_log(msg)
        if self.direct_task:
            self.engine.add_history(self.direct_task, status, msg)
            self.direct_task = None
        if self.download_worker:
            self.download_worker.quit()
            self.download_worker.wait(500)
            self.download_worker = None

        self.update_queue_button_state()
        self.download_btn.setEnabled(len(self.results_list.selectedItems()) == 1)

    def select_all_results(self):
        self.results_list.selectAll()

    @staticmethod
    def _format_duration(seconds):
        if not seconds:
            return ""
        try:
            seconds = int(seconds)
        except (TypeError, ValueError):
            return ""

        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    def on_language_changed(self, language_code):
        """Handle language change - refresh UI texts"""
        self.refresh_ui_text()

    def refresh_ui_text(self):
        """Refresh all UI texts with current language"""
        from i18n import t

        # Titles
        self.search_title.setText(t("search"))
        self.results_header.setText(t("results"))
        self.details_title.setText(t("details"))

        # Labels
        self.search_input.setPlaceholderText(t("search_placeholder"))
        self.preview_info.setText(t("select_result"))
        self.results_empty.setText(t("no_search"))

        # Buttons
        if hasattr(self, 'select_all_btn'):
            self.select_all_btn.setText(t("select_all"))
        if hasattr(self, 'add_btn'):
            self.add_btn.setText(t("add_to_queue"))
        if hasattr(self, 'search_btn'):
            self.search_btn.setText(t("search_btn"))
        if hasattr(self, 'download_btn'):
            self.download_btn.setText(t("download_now"))
        if hasattr(self, 'yt_check'):
            self.yt_check.setText(t("youtube"))
        if hasattr(self, 'sc_check'):
            self.sc_check.setText(t("soundcloud"))

        # Format/Bitrate labels
        for label in self.findChildren(QLabel):
            label_key = label.property("i18n_key")
            if label_key:
                label.setText(t(label_key))

        self.refresh_output_label()
        self.update_queue_button_state()
