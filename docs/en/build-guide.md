# 🔨 Build Guide - Downloader Studio

How to build Downloader Studio for distribution.

## Prerequisites

- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- Inno Setup (to create Windows installer)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Step 2: Build the Executable

```bash
python build_exe.py
```

This creates:
- `dist/DownloaderStudio.exe` - Standalone executable

## Step 3: Create Windows Installer

### Installing Inno Setup

1. Download from: https://jrsoftware.org/isdl.php
2. Install it
3. Open `Downloader_Studio.iss` with Inno Setup
4. Click **Compile** or run:

```bash
iscc.exe Downloader_Studio.iss
```

This creates:
- `dist/DownloaderStudio_Setup.exe` - Complete Windows installer

## Directory Structure

```
dist/
├── DownloaderStudio.exe       ← Standalone executable
├── DownloaderStudio_Setup.exe ← Windows installer
└── ... (dependencies)
```

## Troubleshooting

### PyInstaller can't find modules

Add to the `build_exe.py` script:
```python
--hidden-import=module_name
```

### Icon doesn't appear

Check that `assets/downloader-studio-logo.ico` exists.

### Inno Setup won't compile

- Verify line endings (CRLF)
- Check that the `dist/` folder exists with all files
- Run as Administrator

## Release Process

For each version:

1. Update `__version__` in `app/__init__.py`
2. Update version in `Downloader_Studio.iss`
3. Test the application
4. Build: `python build_exe.py`
5. Create installer: `iscc.exe Downloader_Studio.iss`
6. Create GitHub release with the files

## File Sizes

- Executable: ~50-100 MB
- Installer: ~30-50 MB

---

See also: [Quick Start](quick-start.md)

