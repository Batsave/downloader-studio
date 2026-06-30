# Downloader Studio

Downloader Studio is a desktop media downloader built with PyQt5 and yt-dlp. It focuses on a clean operator interface: search, queue, download, review logs, and adjust defaults without leaving the app.

## Features

- Multi-source search for YouTube and SoundCloud
- Audio and video formats: MP3, MP4, WAV, M4A
- Queue management with progress and history
- Dark and light themes
- French, English, German, and Spanish UI
- Minimal floating mode with `Ctrl+M`
- Windows installer workflow with PyInstaller and Inno Setup

## Quick Start

```bash
git clone https://github.com/batsave/downloader-studio.git
cd downloader-studio
pip install -r requirements.txt
python main.py
```

Downloaded files are written to the user's Downloads folder by default: `%USERPROFILE%\Downloads`.

## Documentation

Open [docs/index.html](docs/index.html) in a browser for the visual documentation hub.

GitHub Pages URL after deployment: `https://batsave.github.io/downloader-studio/`

For the first GitHub Pages setup, use:

- Source: `Deploy from a branch`
- Branch: `gh-pages`
- Folder: `/ (root)`

HTML guides:

- [French documentation](docs/fr/index.html)
- [English documentation](docs/en/index.html)
- [German documentation](docs/de/index.html)
- [Spanish documentation](docs/es/index.html)

## Build

```bash
python build_exe.py
```

Then compile `Downloader_Studio.iss` with Inno Setup to create the Windows installer.

## Project Structure

```text
downloader-studio/
|-- app/
|   |-- core/        # Download engine and workers
|   |-- ui/          # PyQt5 windows and pages
|   `-- utils/       # Icons and resource helpers
|-- i18n/            # Translation table
|-- assets/          # Logo and UI assets
|-- docs/            # HTML documentation hub and guides
|-- main.py          # Application entry point
`-- requirements.txt
```

## License

MIT License. See [LICENSE](LICENSE).
