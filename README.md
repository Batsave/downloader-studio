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

Open the public documentation hub:

[https://batsave.github.io/downloader-studio/](https://batsave.github.io/downloader-studio/)

You can also open [docs/index.html](docs/index.html) locally from the repository.

For the first GitHub Pages setup, use:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/docs`

If GitHub shows an old `actions/configure-pages@v5` error, the repository is
still configured for `GitHub Actions` Pages deployment or the page is showing an
older failed run. This project serves the static documentation from `main/docs`,
so the Pages source must be `Deploy from a branch`.

HTML guides:

- [French documentation](https://batsave.github.io/downloader-studio/fr/)
- [English documentation](https://batsave.github.io/downloader-studio/en/)
- [German documentation](https://batsave.github.io/downloader-studio/de/)
- [Spanish documentation](https://batsave.github.io/downloader-studio/es/)

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
