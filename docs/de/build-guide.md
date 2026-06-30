# 🔨 Build-Anleitung - Downloader Studio

Wie Sie Downloader Studio für die Verteilung kompilieren.

## Voraussetzungen

- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- Inno Setup (zum Erstellen des Windows-Installationsprogramms)

## Schritt 1: Abhängigkeiten Installieren

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Schritt 2: Ausführbare Datei Erstellen

```bash
python build_exe.py
```

Dies erstellt:
- `dist/DownloaderStudio.exe` - Eigenständige ausführbare Datei

## Schritt 3: Windows-Installationsprogramm Erstellen

### Inno Setup Installieren

1. Herunterladen von: https://jrsoftware.org/isdl.php
2. Installieren Sie es
3. Öffnen Sie `Downloader_Studio.iss` mit Inno Setup
4. Klicken Sie auf **Kompilieren** oder führen Sie aus:

```bash
iscc.exe Downloader_Studio.iss
```

Dies erstellt:
- `dist/DownloaderStudio_Setup.exe` - Vollständiges Windows-Installationsprogramm

## Verzeichnisstruktur

```
dist/
├── DownloaderStudio.exe       ← Eigenständige ausführbare Datei
├── DownloaderStudio_Setup.exe ← Windows-Installationsprogramm
└── ... (Abhängigkeiten)
```

## Fehlerbehebung

### PyInstaller findet Module nicht

Fügen Sie zum `build_exe.py`-Skript hinzu:
```python
--hidden-import=module_name
```

### Symbol wird nicht angezeigt

Überprüfen Sie, ob `assets/downloader-studio-logo.ico` vorhanden ist.

### Inno Setup wird nicht kompiliert

- Stellen Sie sicher, dass die Zeilenendungen korrekt sind (CRLF)
- Überprüfen Sie, ob der Ordner `dist/` mit allen Dateien vorhanden ist
- Führen Sie es als Administrator aus

## Veröffentlichungsprozess

Für jede Version:

1. Aktualisieren Sie `__version__` in `app/__init__.py`
2. Aktualisieren Sie die Version in `Downloader_Studio.iss`
3. Testen Sie die Anwendung
4. Build: `python build_exe.py`
5. Installationsprogramm erstellen: `iscc.exe Downloader_Studio.iss`
6. GitHub-Version mit den Dateien erstellen

## Dateigröße

- Ausführbare Datei: ~50-100 MB
- Installationsprogramm: ~30-50 MB

---

Siehe auch: [Schnelleinstieg](quick-start.md)

