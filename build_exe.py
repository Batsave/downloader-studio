"""
Complete build script for Downloader Studio
Builds PyInstaller exe + Inno Setup installer + FFmpeg setup
"""

import ast
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from zipfile import ZipFile

SUPPORTED_PYTHON_MIN = (3, 10)
SUPPORTED_PYTHON_MAX = (3, 13)
FFMPEG_DOWNLOAD_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


class Builder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.dist_dir = self.project_dir / 'dist'
        self.app_dist_dir = self.dist_dir / 'DownloaderStudio'
        self.pyinstaller_dist_dir = self.dist_dir / '.pyinstaller'
        self.ffmpeg_cache_bin = self.dist_dir / '.ffmpeg-cache' / 'bin'

    def log(self, msg, level='info'):
        prefix = {'info': '  INFO', 'ok': '  OK', 'error': '  ERROR', 'header': '='}
        print(f"{prefix.get(level, level)} {msg}")

    def get_app_version(self):
        config_path = self.project_dir / 'config.py'
        tree = ast.parse(config_path.read_text(encoding='utf-8'), filename=str(config_path))

        for node in tree.body:
            if (
                isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == 'APP_VERSION' for target in node.targets)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                return node.value.value

        raise RuntimeError("APP_VERSION not found in config.py")

    def validate_python_runtime(self):
        """Prevent release builds with Python versions that produce fragile PyInstaller EXEs."""
        version = sys.version_info
        current = f"{version.major}.{version.minor}.{version.micro}"
        min_label = ".".join(map(str, SUPPORTED_PYTHON_MIN))
        max_label = ".".join(map(str, SUPPORTED_PYTHON_MAX))

        if version.releaselevel != "final":
            self.log(
                f"Unsupported Python runtime: {current}-{version.releaselevel} ({sys.executable})",
                'error',
            )
            self.log(f"Use CPython {min_label}-{max_label} final for release builds.", 'info')
            self.show_python_setup_help()
            return False

        if not (SUPPORTED_PYTHON_MIN <= (version.major, version.minor) <= SUPPORTED_PYTHON_MAX):
            self.log(f"Unsupported Python runtime: {current} ({sys.executable})", 'error')
            self.log(f"Use CPython {min_label}-{max_label} final for release builds.", 'info')
            self.log("Python 3.14/3.15 builds can fail at startup with python*.dll load errors.", 'info')
            self.show_python_setup_help()
            return False

        self.log(f"Python runtime OK: {current} ({sys.executable})", 'ok')
        return True

    def show_python_setup_help(self):
        self.log("Install Python 3.13 x64, then run:", 'info')
        print("    winget install Python.Python.3.13")
        print("    py -3.13 -m venv .venv-build")
        print("    ./.venv-build/Scripts/python.exe -m pip install --upgrade pip")
        print("    ./.venv-build/Scripts/python.exe -m pip install -r requirements.txt pyinstaller")
        print("    ./.venv-build/Scripts/python.exe build_exe.py")

    def remove_tree(self, path, max_retries=3):
        """Remove directory tree with retry logic"""
        for attempt in range(max_retries):
            try:
                shutil.rmtree(path)
                self.log(f"Cleaned {path}", 'ok')
                return True
            except PermissionError:
                if attempt < max_retries - 1:
                    self.log(f"Locked: {path}, retrying in 2s...", 'info')
                    time.sleep(2)
                else:
                    self.log(f"Cannot remove {path} - file in use", 'error')
                    return False
        return False

    def build_pyinstaller(self):
        """Build executable with PyInstaller"""
        self.log("Building with PyInstaller...", 'header')

        if self.app_dist_dir.exists():
            self.log(f"Keeping existing bundle: {self.app_dist_dir}", 'info')
        else:
            self.app_dist_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--name=DownloaderStudio',
            '--onedir', '--windowed',
            '--noconfirm',
            '--noupx',
            f'--distpath={self.pyinstaller_dist_dir}',
            '--icon=assets/downloader-studio-logo.ico',
            f'--add-data=assets{os.pathsep}assets',
            f'--add-data=i18n{os.pathsep}i18n',
            '--collect-all=PyQt5',
            '--collect-all=yt_dlp',
            '--hidden-import=PyQt5.QtCore',
            '--hidden-import=PyQt5.QtGui',
            '--hidden-import=PyQt5.QtWidgets',
            '--hidden-import=yt_dlp',
            '--hidden-import=requests',
            'main.py'
        ]

        result = subprocess.run(cmd, cwd=str(self.project_dir))
        if result.returncode == 0:
            staged_app = self.pyinstaller_dist_dir / 'DownloaderStudio'
            if not staged_app.exists():
                self.log(f"PyInstaller output not found: {staged_app}", 'error')
                return False

            shutil.copytree(staged_app, self.app_dist_dir, dirs_exist_ok=True)
            exe = self.app_dist_dir / 'DownloaderStudio.exe'
            size_mb = exe.stat().st_size / (1024 * 1024)
            self.log(f"Built: {exe.relative_to(self.project_dir)} ({size_mb:.1f} MB)", 'ok')
            return True
        else:
            self.log("PyInstaller build failed", 'error')
            return False

    def setup_ffmpeg(self):
        """Find or download FFmpeg"""
        self.log("Setting up FFmpeg...", 'header')

        ffmpeg_bin = self.app_dist_dir / 'ffmpeg' / 'bin'

        # Check if already exists
        if (ffmpeg_bin / 'ffmpeg.exe').exists() and (ffmpeg_bin / 'ffprobe.exe').exists():
            self.log("FFmpeg already present", 'ok')
            return True

        if (self.ffmpeg_cache_bin / 'ffmpeg.exe').exists() and (self.ffmpeg_cache_bin / 'ffprobe.exe').exists():
            self.log(f"Found cached FFmpeg: {self.ffmpeg_cache_bin}", 'info')
            return self._copy_ffmpeg(self.ffmpeg_cache_bin)

        # Try local installation
        local = self._find_local_ffmpeg()
        if local:
            self.log(f"Found local FFmpeg: {local}", 'info')
            return self._copy_ffmpeg(local)

        # Download
        self.log("No local FFmpeg, attempting download...", 'info')
        return self._download_ffmpeg()

    def _find_local_ffmpeg(self):
        """Find FFmpeg in common locations"""
        paths = [
            'C:\\ffmpeg\\bin',
            'C:\\ffmpeg-master-latest-win64-gpl\\bin',
            os.path.expanduser('~\\ffmpeg\\bin'),
        ]
        for path in paths:
            if (
                Path(path).exists()
                and Path(path).joinpath('ffmpeg.exe').exists()
                and Path(path).joinpath('ffprobe.exe').exists()
            ):
                return Path(path)
        return None

    def _copy_ffmpeg(self, source):
        """Copy the complete FFmpeg bin folder from a local installation."""
        dest = self.app_dist_dir / 'ffmpeg' / 'bin'
        dest.mkdir(parents=True, exist_ok=True)

        for item in source.iterdir():
            target = dest / item.name
            if item.is_dir():
                if target.exists():
                    shutil.rmtree(target)
                shutil.copytree(item, target)
            else:
                shutil.copy2(item, target)

        has_ffmpeg = (dest / 'ffmpeg.exe').exists()
        has_ffprobe = (dest / 'ffprobe.exe').exists()
        self.log(f"Copied FFmpeg bin folder from {source}", 'ok')
        return has_ffmpeg and has_ffprobe

    def _download_ffmpeg(self):
        """Download FFmpeg release build and extract the complete bin folder."""
        url = FFMPEG_DOWNLOAD_URL
        zip_file = self.project_dir / 'temp_ffmpeg.zip'

        try:
            self.log("Downloading FFmpeg release essentials...", 'info')
            self._download_with_progress(url, str(zip_file))

            self.log("Extracting FFmpeg...", 'info')
            dest = self.ffmpeg_cache_bin
            dest.mkdir(parents=True, exist_ok=True)

            with ZipFile(zip_file) as zf:
                names = zf.namelist()
                ffmpeg_name = next((name for name in names if name.endswith('bin/ffmpeg.exe')), None)
                if not ffmpeg_name:
                    self.log("Could not find FFmpeg bin folder in archive", 'error')
                    return False

                bin_prefix = ffmpeg_name.rsplit('/', 1)[0] + '/'
                extracted = 0
                for name in names:
                    if not name.startswith(bin_prefix) or name.endswith('/'):
                        continue

                    relative_name = name[len(bin_prefix):]
                    if not relative_name:
                        continue

                    output = dest / relative_name.replace('/', os.sep)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(zf.read(name))
                    extracted += 1

                self.log(f"Extracted {extracted} FFmpeg bin files", 'ok')

            zip_file.unlink()

            # Verify both files exist
            has_ffmpeg = (dest / 'ffmpeg.exe').exists()
            has_ffprobe = (dest / 'ffprobe.exe').exists()

            if has_ffmpeg and has_ffprobe:
                self.log("FFmpeg cached", 'ok')
                return self._copy_ffmpeg(dest)
            else:
                self.log(f"Missing: ffmpeg={has_ffmpeg} ffprobe={has_ffprobe}", 'error')
                return False

        except Exception as e:
            self.log(f"Download failed: {e}", 'error')
            if zip_file.exists():
                zip_file.unlink()
            return False

    def _download_with_progress(self, url, dest):
        """Download with progress bar"""
        def hook(block, size, total):
            if total > 0:
                pct = min(100, int(block * size * 100 / total))
                print(f"\r  Progress: {pct}%", end='', flush=True)
        urllib.request.urlretrieve(url, dest, reporthook=hook)
        print()

    def build_inno_installer(self):
        """Build Inno Setup installer"""
        self.log("Building Inno Setup installer...", 'header')
        app_version = self.get_app_version()
        self.log(f"Installer version: {app_version}", 'info')

        inno_paths = [
            r'A:\Inno Setup 6\ISCC.exe',
            r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
            r'C:\Program Files\Inno Setup 6\ISCC.exe',
            r'C:\Program Files (x86)\Inno Setup 5\ISCC.exe',
            r'C:\Program Files\Inno Setup 5\ISCC.exe',
        ]

        inno = None
        for path in inno_paths:
            if Path(path).exists():
                inno = path
                break

        if not inno:
            self.log("Inno Setup not found - skipping installer", 'info')
            self.log("Install from: https://jrsoftware.org/isdl.php", 'info')
            return False

        iss_file = self.project_dir / 'Downloader_Studio.iss'
        if not iss_file.exists():
            self.log(f"Script not found: {iss_file}", 'error')
            return False

        result = subprocess.run(
            [inno, f'/DMyAppVersion={app_version}', str(iss_file)],
            cwd=str(self.project_dir),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            installers = sorted(
                self.dist_dir.glob('DownloaderStudio*_Setup.exe'),
                key=lambda path: path.stat().st_mtime,
                reverse=True,
            )
            if installers:
                installer = installers[0]
                size_mb = installer.stat().st_size / (1024 * 1024)
                self.log(f"Installer created: {installer.name} ({size_mb:.1f} MB)", 'ok')
                return True

        self.log(f"Inno Setup error:\n{result.stderr}", 'error')
        return False

    def build_all(self, args):
        """Build everything"""
        print("\n" + "=" * 60)
        print("Downloader Studio - Complete Build")
        print("=" * 60 + "\n")

        if not self.validate_python_runtime():
            self.log("Build stopped before creating a broken release executable.", 'error')
            return False

        if '--clean-build' in args:
            for folder in [self.project_dir / 'build', self.pyinstaller_dist_dir, self.project_dir / '__pycache__']:
                if folder.exists() and not self.remove_tree(folder):
                    return False

        # PyInstaller
        if not self.build_pyinstaller():
            self.log("Build failed", 'error')
            return False

        # FFmpeg
        if '--no-ffmpeg' not in args:
            if not self.setup_ffmpeg():
                self.log("FFmpeg setup skipped", 'info')

        # Inno Setup
        if '--no-installer' not in args:
            if not self.build_inno_installer():
                self.log("Installer build failed", 'error')
                return False

        print("\n" + "=" * 60)
        self.log("Build complete!", 'ok')
        print("=" * 60)
        print(f"\n  App:       dist/DownloaderStudio/DownloaderStudio.exe")
        print("  Portable:  dist/DownloaderStudio/")
        print("  Installer: dist/DownloaderStudio*_Setup.exe")
        print("\n  Distribute the newest DownloaderStudio*_Setup.exe\n")

        return True


if __name__ == "__main__":
    builder = Builder()
    success = builder.build_all(sys.argv[1:])
    sys.exit(0 if success else 1)
