# 📐 Architecture - Downloader Studio

Understand the structure and organization of the project.

## Overview

Downloader Studio is organized into 4 main packages:

```
app/
├── ui/              ← User interface
├── core/            ← Business logic
└── utils/           ← Utilities
i18n/               ← Multilingual translations
```

## Detailed Structure

### 📱 UI Package (`app/ui/`)

All PyQt5 user interface components.

**main_window.py**
- Application main window
- Tab management (Search, Queue, Settings, Logs)
- Themes (dark/light)
- Collapsible sidebar

**minimal_window.py**
- Minimalist window (Ctrl+M Mode)
- Drag-drop input for URLs
- Simple progress bar

**pages/**
- `search_page.py` - Search and download
- `queue_page.py` - Queue management
- `settings_page.py` - Application configuration
- `logs_page.py` - Download history

### ⚙️ Core Package (`app/core/`)

Business logic and main features.

**download_engine.py**
- Download engine
- Task management
- yt-dlp integration
- Progress signals

### 🛠️ Utils Package (`app/utils/`)

Shared utilities.

**icons.py**
- SVG icon creation
- Dynamic colorization
- Theme support

**resources.py**
- Resource path management
- PyInstaller compatible
- Inno Setup compatible

## 🌍 I18N Package (`i18n/`)

Multilingual localization system.

**translations.py**
- 4 languages: FR, EN, DE, ES
- 39+ translation keys
- Translator class
- `t()` and `set_language()` functions

## Data Flow

```
main.py
  ↓
Downloader (main_window.py)
  ├── UI Pages (pages/*.py)
  │   ├── SearchPage
  │   ├── QueuePage
  │   ├── SettingsPage
  │   └── LogsPage
  ├── MinimalWindow
  └── DownloadEngine (core/download_engine.py)
      └── yt-dlp
```

## Asynchronous Architecture

```
Main Thread (PyQt5)
  ↓
DownloadWorker (QThread)
  ├── Signals: result_found, progress, finished
  └── DownloadEngine
      └── yt-dlp operations
```

## Theme System

```
THEMES (config.py)
├── "dark"
│   ├── bg: #0f0f23
│   ├── surface: #1a1a2e
│   ├── accent: #f59e0b
│   └── text: #fafafa
└── "light"
    ├── bg: #f5f5f5
    ├── surface: #ffffff
    ├── accent: #f59e0b
    └── text: #1a1a1a
```

## Centralized Configuration

**config.py**
- Application constants
- Directory paths
- Default settings
- Supported languages

## Entry Points

1. **main.py** - Main entry point
2. **build_exe.py** - PyInstaller build script
3. **Downloader_Studio.iss** - Inno Setup configuration

## Path Compatibility

The application supports 3 execution modes:

```python
resource_path("assets/logo.svg")

1. Direct Python        → project_root/assets/
2. PyInstaller exe      → _MEIPASS/assets/
3. Inno Setup installed → Program Files/.../assets/
```

## Design Principles

✓ **Separation of Concerns**
  - UI in `app/ui/`
  - Logic in `app/core/`
  - Utilities in `app/utils/`

✓ **Absolute Paths**
  - All imports are absolute
  - Compatible with all environments

✓ **Centralized Translations**
  - All strings in `i18n/translations.py`
  - No hardcoded text

✓ **Centralized Configuration**
  - Constants in `config.py`
  - Easy to maintain

## Performance

- **Asynchronous threads** for downloads
- **PyQt5 signals** for communication
- **Caching** for icons
- **Lazy loading** of pages

## Security

- No password storage
- No sensitive data in cache
- URL validation before download
- Proper error handling

---

For more information:
- [Build Guide](build-guide.md)
- [Quick Start](quick-start.md)

