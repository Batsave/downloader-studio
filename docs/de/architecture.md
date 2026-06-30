# 📐 Architektur - Downloader Studio

Verstehen Sie die Struktur und Organisation des Projekts.

## Übersicht

Downloader Studio ist in 4 Hauptpakete organisiert:

```
app/
├── ui/              ← Benutzeroberfläche
├── core/            ← Geschäftslogik
└── utils/           ← Hilfsfunktionen
i18n/               ← Mehrsprachige Übersetzungen
```

## Detaillierte Struktur

### 📱 UI-Paket (`app/ui/`)

Alle PyQt5-Benutzeroberflächenkomponenten.

**main_window.py**
- Hauptfenster der Anwendung
- Registerkartenverwaltung (Suche, Warteschlange, Einstellungen, Protokolle)
- Designs (dunkel/hell)
- Zusammenklappbare Seitenleiste

**minimal_window.py**
- Minimalistisches Fenster (Strg+M-Modus)
- Drag-and-Drop-Eingabe für URLs
- Einfache Fortschrittsleiste

**pages/**
- `search_page.py` - Suche und Download
- `queue_page.py` - Warteschlangenverwaltung
- `settings_page.py` - Anwendungskonfiguration
- `logs_page.py` - Download-Verlauf

### ⚙️ Core-Paket (`app/core/`)

Geschäftslogik und Hauptfunktionen.

**download_engine.py**
- Download-Engine
- Aufgabenverwaltung
- yt-dlp-Integration
- Fortschrittssignale

### 🛠️ Utils-Paket (`app/utils/`)

Gemeinsame Hilfsfunktionen.

**icons.py**
- SVG-Icon-Erstellung
- Dynamische Farbgebung
- Design-Unterstützung

**resources.py**
- Ressourcenpfad-Verwaltung
- PyInstaller-kompatibel
- Inno-Setup-kompatibel

## 🌍 I18N-Paket (`i18n/`)

Mehrsprachiges Lokalisierungssystem.

**translations.py**
- 4 Sprachen: FR, EN, DE, ES
- 39+ Übersetzungsschlüssel
- Translator-Klasse
- `t()`- und `set_language()`-Funktionen

## Datenfluss

```
main.py
  ↓
Downloader (main_window.py)
  ├── UI-Seiten (pages/*.py)
  │   ├── SearchPage
  │   ├── QueuePage
  │   ├── SettingsPage
  │   └── LogsPage
  ├── MinimalWindow
  └── DownloadEngine (core/download_engine.py)
      └── yt-dlp
```

## Asynchrone Architektur

```
Hauptthread (PyQt5)
  ↓
DownloadWorker (QThread)
  ├── Signale: result_found, progress, finished
  └── DownloadEngine
      └── yt-dlp-Vorgänge
```

## Design-System

```
DESIGNS (config.py)
├── "dunkel"
│   ├── bg: #0f0f23
│   ├── surface: #1a1a2e
│   ├── accent: #f59e0b
│   └── text: #fafafa
└── "hell"
    ├── bg: #f5f5f5
    ├── surface: #ffffff
    ├── accent: #f59e0b
    └── text: #1a1a1a
```

## Zentralisierte Konfiguration

**config.py**
- Anwendungskonstanten
- Verzeichnispfade
- Standardeinstellungen
- Unterstützte Sprachen

## Einstiegspunkte

1. **main.py** - Haupteinstiegspunkt
2. **build_exe.py** - PyInstaller-Build-Skript
3. **Downloader_Studio.iss** - Inno-Setup-Konfiguration

## Pfad-Kompatibilität

Die Anwendung unterstützt 3 Ausführungsmodi:

```python
resource_path("assets/logo.svg")

1. Direktes Python        → project_root/assets/
2. PyInstaller exe        → _MEIPASS/assets/
3. Inno Setup installiert → Program Files/.../assets/
```

## Design-Prinzipien

✓ **Aufgabenteilung**
  - UI in `app/ui/`
  - Logik in `app/core/`
  - Hilfsfunktionen in `app/utils/`

✓ **Absolute Pfade**
  - Alle Importe sind absolut
  - Kompatibel mit allen Umgebungen

✓ **Zentralisierte Übersetzungen**
  - Alle Zeichenketten in `i18n/translations.py`
  - Kein hardcodierter Text

✓ **Zentralisierte Konfiguration**
  - Konstanten in `config.py`
  - Leicht zu warten

## Leistung

- **Asynchrone Threads** für Downloads
- **PyQt5-Signale** für Kommunikation
- **Caching** für Symbole
- **Lazy Loading** von Seiten

## Sicherheit

- Kein Passwort-Speicher
- Keine sensiblen Daten im Cache
- URL-Validierung vor dem Download
- Ordnungsgemäße Fehlerbehandlung

---

Für weitere Informationen:
- [Build-Anleitung](build-guide.md)
- [Schnelleinstieg](quick-start.md)

