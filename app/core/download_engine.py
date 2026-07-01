from PyQt5.QtCore import QThread, pyqtSignal, QObject
from i18n import t
from config import DEFAULT_OUTPUT_DIR
import os
import shutil
import sys
import yt_dlp


class DownloadTask:
    def __init__(self, url, fmt, title="", quality="best", bitrate="320kbps"):
        self.url = url
        self.fmt = fmt
        self.title = title or url
        self.quality = quality
        self.bitrate = bitrate
        self.status = "pending"
        self.progress = 0


class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str)
    log = pyqtSignal(str)

    def __init__(self, task, output_dir):
        super().__init__()
        self.task = task
        self.output_dir = output_dir
        self.ffmpeg_location = self._setup_ffmpeg_path()

    @staticmethod
    def _setup_ffmpeg_path():
        """Configure and return the bundled FFmpeg bin directory for yt-dlp."""
        def use_if_valid(path):
            ffmpeg_exe = os.path.join(path, 'ffmpeg.exe')
            ffprobe_exe = os.path.join(path, 'ffprobe.exe')
            if os.path.exists(ffmpeg_exe) and os.path.exists(ffprobe_exe):
                os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
                return path
            return None

        possible_paths = []

        if getattr(sys, 'frozen', False):
            # PyInstaller one-file extracts to _MEIPASS, while Inno installs FFmpeg
            # next to the executable.
            exe_dir = os.path.dirname(sys.executable)
            bundle_dir = getattr(sys, '_MEIPASS', '')
            possible_paths.extend([
                os.path.join(exe_dir, 'ffmpeg', 'bin'),
                os.path.join(exe_dir, 'ffmpeg'),
                os.path.join(bundle_dir, 'ffmpeg', 'bin'),
                os.path.join(bundle_dir, 'ffmpeg'),
            ])
        else:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            possible_paths.extend([
                os.path.join(project_root, 'dist', 'ffmpeg', 'bin'),
                'C:\\ffmpeg\\bin',
                'C:\\ffmpeg-master-latest-win64-gpl\\bin',
                os.path.expanduser('~\\ffmpeg\\bin'),
            ])

        for path in possible_paths:
            found = use_if_valid(path)
            if found:
                return found

        ffmpeg = shutil.which('ffmpeg')
        ffprobe = shutil.which('ffprobe')
        if ffmpeg and ffprobe:
            return os.path.dirname(ffmpeg)

        return None

    @staticmethod
    def _audio_quality(value):
        digits = "".join(ch for ch in str(value) if ch.isdigit())
        return digits or "192"

    @staticmethod
    def _video_format(value):
        text = str(value)
        if "2160" in text or "4K" in text:
            max_height = 2160
        elif "1080" in text or "Full HD" in text:
            max_height = 1080
        elif "720" in text:
            max_height = 720
        elif "480" in text:
            max_height = 480
        else:
            return "bestvideo+bestaudio/best"

        return (
            f"bestvideo[height<={max_height}]+bestaudio/"
            f"best[height<={max_height}]/best"
        )

    def run(self):
        def progress_hook(d):
            if d["status"] == "downloading":
                percent = d.get("_percent_str", "0%").replace("%", "").replace(" ", "")
                try:
                    value = int(float(percent))
                    self.task.progress = value
                    self.progress.emit(value)
                except Exception:
                    self.progress.emit(0)

        try:
            self.task.status = "downloading"
            self.log.emit(t("download_log").format(title=self.task.title, format=self.task.fmt))

            opts = {
                "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "quiet": False,
                "no_warnings": True,
                "socket_timeout": 30,
                "http_headers": {"User-Agent": "Mozilla/5.0"},
            }
            if self.ffmpeg_location:
                opts["ffmpeg_location"] = self.ffmpeg_location

            if self.task.fmt == "mp3":
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": self._audio_quality(self.task.bitrate),
                }]
            elif self.task.fmt == "wav":
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "0",
                }]
            elif self.task.fmt == "m4a":
                opts["format"] = "bestaudio/best"
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                    "preferredquality": self._audio_quality(self.task.bitrate),
                }]
            else:
                opts["format"] = self._video_format(self.task.quality)

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.extract_info(self.task.url, download=True)

            self.task.status = "completed"
            self.task.progress = 100
            self.finished.emit("completed", t("finished_log").format(title=self.task.title))
        except Exception as exc:
            self.task.status = "failed"
            error_msg = str(exc)[:100]
            self.finished.emit("failed", f"Erreur: {error_msg}")
            self.log.emit(f"Erreur: {error_msg}")


class DownloadEngine(QObject):
    log_signal = pyqtSignal(str)
    queue_updated = pyqtSignal()
    progress_updated = pyqtSignal(int, int)
    history_updated = pyqtSignal()
    download_finished = pyqtSignal(object, str, str)

    def __init__(self):
        super().__init__()
        self.queue = []
        self.current_worker = None
        self.current_task = None
        self.output_dir = DEFAULT_OUTPUT_DIR
        self.sources_enabled = {
            "youtube": True,
            "soundcloud": True,
            "twitch": True,
            "tiktok": True,
        }
        self.enabled_formats = ["mp3", "mp4", "wav", "m4a"]
        self.quality = "Full HD (1080p)"
        self.audio_quality = "320kbps"
        self.history = []

    def add_task(self, task):
        if self.current_task and self.current_task.url == task.url:
            self.log_signal.emit(t("already_downloading"))
            return False
        if any(existing.url == task.url for existing in self.queue):
            self.log_signal.emit(t("already_in_queue"))
            return False

        self.queue.append(task)
        self.queue_updated.emit()
        self.log_signal.emit(t("added_log").format(title=task.title))
        return True

    def add_history(self, task, status, message=""):
        self.history.insert(0, {
            "title": task.title,
            "url": task.url,
            "fmt": task.fmt,
            "status": status,
            "message": message,
        })
        self.history = self.history[:30]
        self.history_updated.emit()

    @staticmethod
    def _playlist_entry_url(entry, source_url):
        url = entry.get("webpage_url") or entry.get("url") or ""
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            return url

        entry_id = entry.get("id")
        extractor = str(entry.get("extractor_key") or entry.get("ie_key") or "").lower()
        source = str(source_url).lower()
        if entry_id and ("youtube" in extractor or "youtube.com" in source or "youtu.be" in source):
            return f"https://www.youtube.com/watch?v={entry_id}"

        return ""

    def extract_playlist_entries(self, url, max_entries=200):
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": 15,
                "extract_flat": "in_playlist",
                "skip_unavailable_fragments": True,
                "ignoreerrors": True,
                "playlistend": max_entries,
                "http_headers": {"User-Agent": "Mozilla/5.0"},
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)

            entries = []
            for entry in (info or {}).get("entries") or []:
                if not entry or entry.get("_type") == "error":
                    continue

                entry_url = self._playlist_entry_url(entry, url)
                if not entry_url:
                    continue

                title = entry.get("title") or entry.get("fulltitle") or entry_url
                entries.append({
                    "title": title,
                    "url": entry_url,
                    "webpage_url": entry_url,
                    "duration": entry.get("duration"),
                    "duration_string": entry.get("duration_string"),
                    "playlist_title": (info or {}).get("title") or "",
                })

            return entries
        except Exception as exc:
            print(f"Playlist extract error: {exc}")
            return []

    def remove_task(self, idx):
        if 0 <= idx < len(self.queue):
            self.queue.pop(idx)
            self.queue_updated.emit()

    def start_queue(self):
        if not self.queue:
            self.log_signal.emit(t("queue_is_empty"))
            return
        if self.current_worker and self.current_worker.isRunning():
            self.log_signal.emit(t("direct_download_already_running"))
            return
        self._process_next()

    def _process_next(self):
        if not self.queue:
            self.current_task = None
            self.queue_updated.emit()
            self.log_signal.emit(t("queue_finished"))
            return

        task = self.queue.pop(0)
        self.current_task = task
        self.current_worker = DownloadWorker(task, self.output_dir)
        self.current_worker.progress.connect(self._on_progress)
        self.current_worker.finished.connect(self._on_finished)
        self.current_worker.log.connect(self.log_signal.emit)
        self.current_worker.start()
        self.queue_updated.emit()

    def _on_progress(self, percent):
        self.progress_updated.emit(len(self.queue), percent)

    def _on_finished(self, status, msg):
        self.log_signal.emit(msg)
        self.progress_updated.emit(len(self.queue), 100 if status == "completed" else 0)
        finished_task = self.current_task
        if self.current_worker:
            self.current_worker.quit()
            self.current_worker.wait(1000)
            self.current_worker = None

        if finished_task:
            self.add_history(finished_task, status, msg)
            self.download_finished.emit(finished_task, status, msg)

        self.current_task = None
        self.queue_updated.emit()

        if status == "completed":
            self._process_next()
        elif self.queue:
            self.log_signal.emit(t("next_task"))
            self._process_next()
        else:
            self.log_signal.emit(t("all_downloads_finished"))

    def search_youtube(self, query):
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": 5,
                "default_search": "auto",
                "noplaylist": True,
                "skip_unavailable_fragments": True,
                "ignoreerrors": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch10:{query}", download=False)
                entries = info.get("entries", [])

                valid = []
                for entry in entries:
                    if not entry or entry.get("_type") == "error":
                        continue

                    title = str(entry.get("title", "")).lower()
                    if any(x in title for x in ["not available", "unavailable", "private", "deleted"]):
                        continue

                    if (entry.get("url") or entry.get("webpage_url")) and entry.get("id"):
                        valid.append(entry)
                        if len(valid) >= 10:
                            break

                return valid
        except Exception as exc:
            print(f"YouTube search error: {exc}")
            return []

    def search_soundcloud(self, query):
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "socket_timeout": 3,
                "noplaylist": True,
                "skip_unavailable_fragments": True,
                "ignoreerrors": True,
                "playlistend": 10,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                results = ydl.extract_info(f"scsearch10:{query}", download=False)
                entries = results.get("entries", [])

                valid = []
                for entry in entries:
                    if not entry or entry.get("_type") == "error":
                        continue

                    title = str(entry.get("title", "")).lower()
                    if any(x in title for x in ["drm", "protected", "restricted", "unavailable", "private"]):
                        continue
                    if entry.get("url") and entry.get("id"):
                        valid.append(entry)

                return valid[:10]
        except Exception as exc:
            print(f"SoundCloud search: {exc}")
            return []
