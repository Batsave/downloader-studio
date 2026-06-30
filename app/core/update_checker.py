import re

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from config import APP_LATEST_RELEASE_API, APP_RELEASES_URL, APP_VERSION


def normalize_version(value):
    text = str(value or "").strip().lstrip("vV")
    return tuple(int(part) for part in re.findall(r"\d+", text)[:4])


def is_newer_version(candidate, current=APP_VERSION):
    candidate_parts = normalize_version(candidate)
    current_parts = normalize_version(current)
    if not candidate_parts:
        return False

    length = max(len(candidate_parts), len(current_parts))
    candidate_parts += (0,) * (length - len(candidate_parts))
    current_parts += (0,) * (length - len(current_parts))
    return candidate_parts > current_parts


def select_download_url(release):
    assets = release.get("assets") or []
    for suffix in ("setup.exe", "installer.exe", ".exe", ".msi", ".zip"):
        for asset in assets:
            name = str(asset.get("name") or "").lower()
            if name.endswith(suffix):
                return asset.get("browser_download_url")
    return release.get("html_url") or APP_RELEASES_URL


def release_version(release):
    candidates = [
        release.get("tag_name"),
        release.get("name"),
    ]
    candidates.extend(asset.get("name") for asset in release.get("assets") or [])

    for candidate in candidates:
        parts = normalize_version(candidate)
        if len(parts) >= 2:
            return ".".join(str(part) for part in parts)

    return ""


class UpdateCheckThread(QThread):
    update_available = pyqtSignal(dict)
    no_update = pyqtSignal()
    check_failed = pyqtSignal(str)

    def run(self):
        try:
            response = requests.get(
                APP_LATEST_RELEASE_API,
                headers={"Accept": "application/vnd.github+json"},
                timeout=8,
            )
            if response.status_code == 404:
                self.no_update.emit()
                return
            response.raise_for_status()
            release = response.json()
            version = release_version(release)

            if not is_newer_version(version):
                self.no_update.emit()
                return

            self.update_available.emit({
                "version": version,
                "name": release.get("name") or version,
                "url": select_download_url(release),
                "release_url": release.get("html_url") or APP_RELEASES_URL,
                "notes": release.get("body") or "",
            })
        except Exception as exc:
            self.check_failed.emit(str(exc)[:160])
