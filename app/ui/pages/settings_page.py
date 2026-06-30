from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox,
    QPushButton, QFileDialog, QGroupBox, QLineEdit, QGridLayout
)
from PyQt5.QtCore import Qt
from i18n import set_language, get_translator, t
from app.utils.resources import resource_path
import os
import sys
import json


class SettingsPage(QWidget):
    def __init__(self, engine, parent):
        super().__init__()
        self.engine = engine
        self.parent = parent
        self.setup_ui()
        # Connect language change signal
        from app.signals import signal_manager
        signal_manager.language_changed.connect(self.on_language_changed)

    def setup_ui(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)

        header = QHBoxLayout()
        self.title = QLabel(t("settings"))
        header.addWidget(self.title)
        header.addStretch()

        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: #888888; font-size: 11px;")
        header.addWidget(self.summary_label)
        outer.addLayout(header)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.addWidget(self.create_appearance_group(), 0, 0, 1, 2)
        grid.addWidget(self.create_sources_group(), 1, 0)
        grid.addWidget(self.create_formats_group(), 1, 1)
        grid.addWidget(self.create_quality_group(), 2, 0, 1, 2)
        grid.addWidget(self.create_output_group(), 3, 0, 1, 2)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        outer.addLayout(grid)
        outer.addStretch()

        self.setLayout(outer)
        self.apply_theme()
        self.update_summary()

    def colors(self):
        return self.parent.theme

    def group_style(self):
        t = self.colors()
        return f"""
            QGroupBox {{
                color: {t["text"]};
                font-weight: 700;
                border: 1px solid {t["border"]};
                border-radius: 6px;
                padding: 14px 12px 12px 12px;
                margin-top: 8px;
                background: {t["surface"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {t["text"]};
            }}
        """

    def checkbox_style(self):
        t = self.colors()
        check_icon = resource_path(os.path.join("assets", "check-mark.svg")).replace("\\", "/")
        return """
            QCheckBox {
                color: %s;
                spacing: 8px;
                font-size: 12px;
                padding: 4px 0;
            }
            QCheckBox:disabled {
                color: %s;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid %s;
                background: %s;
            }
            QCheckBox::indicator:hover {
                border: 1px solid %s;
            }
            QCheckBox::indicator:checked {
                background: %s;
                border: 1px solid %s;
                image: url("%s");
            }
            QCheckBox::indicator:disabled {
                background: %s;
                border: 1px solid %s;
            }
        """ % (
            t["text"], t["disabled_text"], t["border"], t["input"],
            t["ring"], t["accent"], t["accent"], check_icon,
            t["disabled_bg"], t["border"]
        )

    def create_appearance_group(self):
        group = QGroupBox(t("appearance"))
        self.appearance_group = group
        group.setStyleSheet(self.group_style())
        layout = QHBoxLayout()
        layout.setSpacing(10)

        label = QLabel(t("theme"))
        self.theme_label = label
        label.setStyleSheet("font-weight: 600;")
        layout.addWidget(label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(t("dark"), "dark")
        self.theme_combo.addItem(t("light"), "light")
        self.theme_combo.setCurrentIndex(0 if self.parent.theme_name == "dark" else 1)
        self.theme_combo.currentIndexChanged.connect(self.update_theme)
        layout.addWidget(self.theme_combo)

        # Language selector
        lang_label = QLabel(t("language"))
        self.language_label = lang_label
        lang_label.setStyleSheet("font-weight: 600; margin-left: 20px;")
        layout.addWidget(lang_label)

        self.language_combo = QComboBox()
        translator = get_translator()
        languages = translator.get_available_languages()
        current_lang = translator.language

        for code, name in languages.items():
            self.language_combo.addItem(name, code)
            if code == current_lang:
                self.language_combo.setCurrentIndex(self.language_combo.count() - 1)

        self.language_combo.currentIndexChanged.connect(self.update_language)
        layout.addWidget(self.language_combo)
        layout.addStretch()

        self.update_btn = QPushButton(t("check_updates"))
        self.update_btn.clicked.connect(self.check_updates)
        layout.addWidget(self.update_btn)

        credit = QLabel("BS Studio - V2.11")
        credit.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        credit.setObjectName("settingsCredit")
        layout.addWidget(credit)

        group.setLayout(layout)
        return group

    def create_sources_group(self):
        group = QGroupBox(t("sources"))
        self.sources_group = group
        group.setStyleSheet(self.group_style())
        layout = QVBoxLayout()
        layout.setSpacing(8)

        hint = QLabel(t("used_in_search"))
        self.sources_hint = hint
        hint.setObjectName("settingsHint")
        layout.addWidget(hint)

        self.source_checks = {}
        for source, label in [("youtube", "YouTube"), ("soundcloud", "SoundCloud")]:
            check = QCheckBox(label)
            check.setChecked(self.engine.sources_enabled.get(source, True))
            check.setStyleSheet(self.checkbox_style())
            check.stateChanged.connect(lambda state, s=source: self.toggle_source(s, state))
            self.source_checks[source] = check
            layout.addWidget(check)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def create_formats_group(self):
        group = QGroupBox(t("formats"))
        self.formats_group = group
        group.setStyleSheet(self.group_style())
        layout = QVBoxLayout()
        layout.setSpacing(8)

        hint = QLabel(t("available_in_search"))
        self.formats_hint = hint
        hint.setObjectName("settingsHint")
        layout.addWidget(hint)

        self.format_checks = {}
        for fmt, label in [
            ("mp3", "MP3 audio"),
            ("mp4", f"MP4 {t('video').lower()}"),
            ("wav", "WAV audio"),
            ("m4a", "M4A audio"),
        ]:
            check = QCheckBox(label)
            check.setChecked(fmt in self.engine.enabled_formats)
            check.setStyleSheet(self.checkbox_style())
            check.stateChanged.connect(lambda state, f=fmt: self.toggle_format(f, state))
            self.format_checks[fmt] = check
            layout.addWidget(check)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def create_quality_group(self):
        group = QGroupBox(t("quality"))
        self.quality_group = group
        group.setStyleSheet(self.group_style())
        layout = QGridLayout()
        layout.setHorizontalSpacing(14)
        layout.setVerticalSpacing(8)

        video_label = QLabel(t("video"))
        self.video_label = video_label
        video_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(video_label, 0, 0)

        self.video_quality_combo = QComboBox()
        self.video_quality_combo.addItems(["4K (2160p)", "Full HD (1080p)", "HD (720p)", "SD (480p)", "Auto"])
        self.video_quality_combo.setCurrentText(self.engine.quality)
        self.video_quality_combo.currentTextChanged.connect(self.update_video_quality)
        layout.addWidget(self.video_quality_combo, 0, 1)

        audio_label = QLabel(t("audio"))
        self.audio_label = audio_label
        audio_label.setStyleSheet("font-weight: 600;")
        layout.addWidget(audio_label, 1, 0)

        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(["320kbps", "256kbps", "192kbps", "128kbps"])
        self.audio_quality_combo.setCurrentText(self.engine.audio_quality)
        self.audio_quality_combo.currentTextChanged.connect(self.update_audio_quality)
        layout.addWidget(self.audio_quality_combo, 1, 1)

        note = QLabel(t("default_values_note"))
        self.quality_note = note
        note.setObjectName("settingsHint")
        layout.addWidget(note, 2, 0, 1, 2)
        layout.setColumnStretch(1, 1)

        group.setLayout(layout)
        return group

    def create_output_group(self):
        group = QGroupBox(t("output_folder"))
        self.output_group = group
        group.setStyleSheet(self.group_style())
        layout = QVBoxLayout()
        layout.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.output_label = QLineEdit()
        self.output_label.setText(self.engine.output_dir)
        self.output_label.setReadOnly(True)
        row.addWidget(self.output_label, 1)

        self.browse_btn = QPushButton(t("change"))
        self.browse_btn.setMinimumWidth(120)
        self.browse_btn.clicked.connect(self.choose_output_dir)
        row.addWidget(self.browse_btn)

        layout.addLayout(row)

        hint = QLabel(t("all_files_note"))
        self.output_hint = hint
        hint.setObjectName("settingsHint")
        layout.addWidget(hint)

        group.setLayout(layout)
        return group

    def notify_search_page(self):
        if hasattr(self.parent, "search_page"):
            self.parent.search_page.refresh_from_settings()

    def update_summary(self):
        sources = [name for name, enabled in self.engine.sources_enabled.items() if enabled and name in {"youtube", "soundcloud"}]
        formats = ", ".join(fmt.upper() for fmt in self.engine.enabled_formats)
        self.summary_label.setText(t("settings_summary").format(count=len(sources), formats=formats))

    def apply_theme(self):
        t = self.colors()
        self.setStyleSheet(f"background: {t['bg']};")
        self.title.setStyleSheet(
            f"font-weight: 700; color: {t['accent']}; font-size: 16px; background: transparent;"
        )
        self.summary_label.setStyleSheet(
            f"color: {t['muted']}; font-size: 11px; background: transparent;"
        )

        # Update theme combo to reflect current theme
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentIndex(0 if self.parent.theme_name == "dark" else 1)
        self.theme_combo.blockSignals(False)

        for group in self.findChildren(QGroupBox):
            group.setStyleSheet(self.group_style())
        for check in self.findChildren(QCheckBox):
            check.setStyleSheet(self.checkbox_style())
        for label in self.findChildren(QLabel):
            if label.objectName() in {"settingsHint", "settingsCredit"}:
                label.setStyleSheet(f"color: {t['muted']}; font-size: 11px; background: transparent;")
            else:
                # Ensure all labels have transparent background
                label.setStyleSheet(f"color: {t['text']}; background: transparent;")

        self.output_label.setStyleSheet(f"""
            QLineEdit {{
                background: {t['panel']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 8px;
                font-size: 11px;
                font-family: monospace;
            }}
        """)

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
            QPushButton:disabled {{
                background: {t['disabled_bg']};
                color: {t['disabled_text']};
            }}
        """
        self.browse_btn.setStyleSheet(button_style)
        self.update_btn.setStyleSheet(button_style)

    def update_theme(self):
        theme_name = self.theme_combo.currentData()
        if theme_name:
            self.parent.apply_theme(theme_name)
            self.parent.save_app_settings()
            self.parent.logs_page.add_log(t("theme_changed").format(theme=self.theme_combo.currentText()))

    def update_language(self):
        language_code = self.language_combo.currentData()
        if language_code:
            # Change language and update UI immediately
            self.parent.change_language(language_code)
            self.parent.save_app_settings()

            self.parent.logs_page.add_log(t("language_changed").format(language=self.language_combo.currentText()))

    def toggle_source(self, source, state):
        self.engine.sources_enabled[source] = bool(state)
        status = t("enabled") if state else t("disabled")
        self.parent.logs_page.add_log(t("source_status").format(source=source.capitalize(), status=status))
        self.update_summary()
        self.notify_search_page()
        self.parent.save_app_settings()

    def toggle_format(self, fmt, state):
        if state:
            if fmt not in self.engine.enabled_formats:
                self.engine.enabled_formats.append(fmt)
        else:
            if len(self.engine.enabled_formats) == 1 and fmt in self.engine.enabled_formats:
                self.format_checks[fmt].blockSignals(True)
                self.format_checks[fmt].setChecked(True)
                self.format_checks[fmt].blockSignals(False)
                self.parent.logs_page.add_log(t("one_format_required"))
                return
            if fmt in self.engine.enabled_formats:
                self.engine.enabled_formats.remove(fmt)

        status = t("enabled") if state else t("disabled")
        self.parent.logs_page.add_log(t("format_status").format(format=fmt.upper(), status=status))
        self.update_summary()
        self.notify_search_page()
        self.parent.save_app_settings()

    def update_video_quality(self, text):
        self.engine.quality = text
        self.parent.logs_page.add_log(t("video_quality_changed").format(quality=text))
        self.notify_search_page()
        self.parent.save_app_settings()

    def update_audio_quality(self, text):
        self.engine.audio_quality = text
        self.parent.logs_page.add_log(t("audio_quality_changed").format(quality=text))
        self.notify_search_page()
        self.parent.save_app_settings()

    def choose_output_dir(self):
        path = QFileDialog.getExistingDirectory(self, t("choose_folder"), self.engine.output_dir)
        if path:
            self.engine.output_dir = path
            self.output_label.setText(path)
            self.parent.logs_page.add_log(t("folder_changed").format(path=path))
            self.notify_search_page()
            self.parent.save_app_settings()

    def check_updates(self):
        if hasattr(self.parent, "check_for_updates"):
            self.parent.check_for_updates(show_no_update=True)

    def on_language_changed(self, language_code):
        """Handle language change - refresh UI texts"""
        self.refresh_ui_text()

    def refresh_ui_text(self):
        """Refresh all UI texts with current language"""
        from i18n import t
        self.title.setText(t("settings"))
        self.appearance_group.setTitle(t("appearance"))
        self.theme_label.setText(t("theme"))
        self.language_label.setText(t("language"))
        self.sources_group.setTitle(t("sources"))
        self.sources_hint.setText(t("used_in_search"))
        self.formats_group.setTitle(t("formats"))
        self.formats_hint.setText(t("available_in_search"))
        self.quality_group.setTitle(t("quality"))
        self.video_label.setText(t("video"))
        self.audio_label.setText(t("audio"))
        self.quality_note.setText(t("default_values_note"))
        self.output_group.setTitle(t("output_folder"))
        self.output_hint.setText(t("all_files_note"))
        self.browse_btn.setText(t("change"))
        self.update_btn.setText(t("check_updates"))
        self.update_summary()
