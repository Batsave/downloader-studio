from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
    QLabel, QProgressBar
)
from PyQt5.QtCore import Qt, QSize
from i18n import t


class QueuePage(QWidget):
    def __init__(self, engine, parent):
        super().__init__()
        self.engine = engine
        self.parent = parent
        self.setup_ui()
        self.engine.queue_updated.connect(self.update_queue_display)
        self.engine.progress_updated.connect(self.update_progress)
        self.engine.history_updated.connect(self.update_history_display)
        self.queue_list.currentRowChanged.connect(self.update_actions)
        self.update_queue_display()
        self.update_history_display()
        # Connect language change signal
        from app.signals import signal_manager
        signal_manager.language_changed.connect(self.on_language_changed)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.title = QLabel(t("queue"))
        layout.addWidget(self.title)

        info_layout = QHBoxLayout()
        self.queue_info = QLabel("")
        info_layout.addWidget(self.queue_info)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        self.current_label = QLabel("")
        self.current_label.setWordWrap(True)
        layout.addWidget(self.current_label)

        self.global_progress = QProgressBar()
        self.global_progress.setRange(0, 100)
        self.global_progress.setValue(0)
        layout.addWidget(self.global_progress)

        self.empty_label = QLabel(f"{t('queue_empty')}\n{t('launch_search_then_add')}")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        layout.addWidget(self.empty_label, 1)

        self.queue_list = QListWidget()
        layout.addWidget(self.queue_list, 1)

        self.history_title = QLabel(t("history"))
        layout.addWidget(self.history_title)

        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(150)
        layout.addWidget(self.history_list)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.start_btn = QPushButton(t("start_queue"))
        self.start_btn.clicked.connect(self.start_queue)

        self.remove_btn = QPushButton(t("remove"))
        self.remove_btn.clicked.connect(self.remove_selected)

        self.clear_btn = QPushButton(t("clear_queue"))
        self.clear_btn.clicked.connect(self.clear_queue)

        controls.addWidget(self.start_btn)
        controls.addWidget(self.remove_btn)
        controls.addStretch()
        controls.addWidget(self.clear_btn)
        layout.addLayout(controls)

        self.setLayout(layout)
        self.apply_theme()

    def apply_theme(self):
        t = self.parent.theme
        self.setStyleSheet(f"background: {t['bg']};")
        self.title.setStyleSheet(
            f"font-weight: 700; color: {t['accent']}; font-size: 16px; background: transparent;"
        )
        self.history_title.setStyleSheet(
            f"font-weight: 700; color: {t['accent']}; font-size: 13px; background: transparent;"
        )
        self.queue_info.setStyleSheet(f"color: {t['text']}; font-weight: 600; background: transparent;")
        self.current_label.setStyleSheet(f"""
            color: {t['muted']};
            background: {t['surface']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 12px;
        """)
        self.global_progress.setStyleSheet(f"""
            QProgressBar {{
                background: {t['panel']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                height: 28px;
                text-align: center;
                color: {t['text']};
                font-weight: bold;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: {t['accent']};
                border-radius: 4px;
                margin: 2px;
            }}
        """)
        self.empty_label.setStyleSheet(f"""
            color: {t['muted']};
            background: {t['surface']};
            border: 1px dashed {t['border']};
            border-radius: 6px;
            padding: 28px;
            font-size: 12px;
        """)
        self.queue_list.setStyleSheet(f"""
            QListWidget {{
                background: {t['panel']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 0px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {t['border']};
                background: {t['panel']};
            }}
            QListWidget::item:selected {{
                background: {t['panel_alt']};
                color: {t['accent']};
            }}
            QListWidget::item:hover {{
                background: {t['panel_alt']};
            }}
        """)
        self.history_list.setStyleSheet(self.queue_list.styleSheet())

        primary = f"""
            QPushButton {{
                background: {t['accent']};
                color: {t['accent_text']};
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
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

        secondary = f"""
            QPushButton {{
                background: {t['panel_alt']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {t['panel']};
            }}
            QPushButton:disabled {{
                background: {t['disabled_bg']};
                color: {t['disabled_text']};
            }}
        """

        self.start_btn.setStyleSheet(primary)
        self.remove_btn.setStyleSheet(secondary)
        self.clear_btn.setStyleSheet(secondary)

    def _task_text(self, idx, task, status):
        title = task.title[:70] if task.title else task.url[:70]
        meta = f"{task.fmt.upper()}"
        if task.fmt == "mp4":
            meta += f" | {task.quality}"
        elif task.fmt in {"mp3", "m4a"}:
            meta += f" | {task.bitrate}"
        return f"{status}  {idx}. {title}\n{meta}"

    def _current_text(self):
        task = self.engine.current_task
        if not task:
            return t("no_current_download")

        title = task.title[:90] if task.title else task.url[:90]
        return f"{t('running')}: {title}"

    def update_queue_display(self):
        self.queue_list.clear()

        row = 1
        if self.engine.current_task:
            item = QListWidgetItem(self._task_text(row, self.engine.current_task, t("running")))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            item.setData(Qt.UserRole, None)
            item.setSizeHint(QSize(0, 54))
            self.queue_list.addItem(item)
            row += 1

        for idx, task in enumerate(self.engine.queue):
            item = QListWidgetItem(self._task_text(row, task, t("pending")))
            item.setData(Qt.UserRole, idx)
            item.setSizeHint(QSize(0, 54))
            self.queue_list.addItem(item)
            row += 1

        pending = len(self.engine.queue)
        running = self.engine.current_task is not None
        if running:
            self.queue_info.setText(t("queue_info_running").format(pending=pending))
        else:
            self.queue_info.setText(t("queue_info_pending").format(pending=pending))

        self.current_label.setText(self._current_text())
        self.current_label.setVisible(running or pending > 0)
        self.global_progress.setVisible(running or pending > 0)

        has_items = running or pending > 0
        self.empty_label.setVisible(not has_items)
        self.queue_list.setVisible(has_items)
        self.update_actions()

    def update_history_display(self):
        self.history_list.clear()
        for entry in self.engine.history[:8]:
            status = "OK" if entry.get("status") == "completed" else t("error")
            title = entry.get("title") or entry.get("url") or t("untitled")
            fmt = (entry.get("fmt") or "").upper()
            item = QListWidgetItem(f"{status}  {title[:70]}\n{fmt}")
            item.setSizeHint(QSize(0, 46))
            item.setToolTip(entry.get("message", ""))
            self.history_list.addItem(item)

        self.history_title.setVisible(bool(self.engine.history))
        self.history_list.setVisible(bool(self.engine.history))

    def update_actions(self):
        current_data = None
        if self.queue_list.currentRow() >= 0:
            current_data = self.queue_list.currentItem().data(Qt.UserRole)

        pending = len(self.engine.queue)
        running = bool(self.engine.current_worker and self.engine.current_worker.isRunning())
        self.start_btn.setEnabled(pending > 0 and not running)
        self.remove_btn.setEnabled(current_data is not None)
        self.clear_btn.setEnabled(pending > 0)

    def update_progress(self, idx, percent):
        self.global_progress.setValue(percent)
        self.update_queue_display()

    def start_queue(self):
        if self.engine.queue:
            self.engine.start_queue()
            self.parent.logs_page.add_log(t("queue_started"))
        else:
            self.parent.logs_page.add_log(t("queue_is_empty"))
        self.update_actions()

    def clear_queue(self):
        if not self.engine.queue:
            return
        self.engine.queue.clear()
        self.update_queue_display()
        self.parent.logs_page.add_log(t("queue_cleared"))

    def remove_selected(self):
        current = self.queue_list.currentRow()
        if current < 0:
            return

        pending_idx = self.queue_list.currentItem().data(Qt.UserRole)
        if pending_idx is None:
            return

        self.engine.remove_task(pending_idx)
        self.update_queue_display()

    def on_language_changed(self, language_code):
        """Handle language change - refresh UI texts"""
        self.refresh_ui_text()

    def refresh_ui_text(self):
        """Refresh all UI texts with current language"""
        from i18n import t
        self.title.setText(t("queue"))
        self.history_title.setText(t("history"))
        self.start_btn.setText(t("start_queue"))
        self.remove_btn.setText(t("remove"))
        self.clear_btn.setText(t("clear_queue"))
        self.empty_label.setText(f"{t('queue_empty')}\n{t('launch_search_then_add')}")
        self.update_queue_display()
        self.update_history_display()
