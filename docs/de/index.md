# Downloader Studio Dokumentation

Dieser Bereich sammelt die deutsche Dokumentation zum Installieren, Nutzen, Bauen und Verstehen von Downloader Studio.

## Anleitungen

- [Schnelleinstieg](quick-start.md) - App installieren, starten und den ersten Download ausführen.
- [Build-Anleitung](build-guide.md) - PyInstaller-EXE und Windows-Installer erstellen.
- [Architektur](architecture.md) - PyQt-Oberfläche, Download-Engine und i18n-Schicht verstehen.
- [Über](about.md) - Projektziele, Funktionen und Nutzungshinweise.

## Typischer Ablauf

1. Abhängigkeiten mit `pip install -r requirements.txt` installieren.
2. App mit `python main.py` starten.
3. Sprache, Design, Formate, Qualität und Ausgabeordner in den Einstellungen wählen.
4. Auf der Suchseite suchen oder eine URL einfügen.
5. Ergebnisse in die Warteschlange legen oder direkt herunterladen.

## Standardwerte

- Ausgabeordner: `%USERPROFILE%\Downloads`
- Design: dunkel
- Sprache: Französisch
- Formate: MP3, MP4, WAV, M4A

## Links

- Repository: https://github.com/batsave/downloader-studio
- Issues: https://github.com/batsave/downloader-studio/issues
- Lizenz: [MIT](../../LICENSE)

