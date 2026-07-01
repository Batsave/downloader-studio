# Downloader Studio v2.15.0

Release notes from `v2.12` to `v2.15.0`.

---

## English

### Highlights

- Fixed the Windows startup error `Failed to load Python DLL`.
- Switched from PyInstaller `onefile` to `onedir` packaging.
- FFmpeg is now bundled with the application and detected automatically by yt-dlp.
- Improved the Windows installer with full bundle installation and automatic versioning.
- Updated key dependencies, including yt-dlp.

### Critical fix

This release fixes startup failures reported on some Windows PCs:

```text
Failed to load Python DLL
C:\Users\...\AppData\Local\Temp\_MEI...\python313.dll
LoadLibrary: The specified module could not be found
```

Downloader Studio no longer extracts Python into a temporary `_MEI...` folder at
startup. Python, PyQt, yt-dlp and native DLLs now stay next to the executable in
the installed application folder.

### Install

Download and run:

```text
DownloaderStudio_2.15.0_Setup.exe
```

For portable use, copy the full folder:

```text
dist\DownloaderStudio\
```

Do not distribute `DownloaderStudio.exe` alone.

---

## Francais

### Points importants

- Correction de l'erreur Windows `Failed to load Python DLL`.
- Passage du packaging PyInstaller `onefile` au packaging `onedir`.
- FFmpeg est maintenant fourni avec l'application et detecte automatiquement par yt-dlp.
- Installateur Windows ameliore avec copie du bundle complet et version automatique.
- Mise a jour des dependances principales, dont yt-dlp.

### Correctif critique

Cette version corrige l'erreur observee sur certains PC Windows:

```text
Failed to load Python DLL
C:\Users\...\AppData\Local\Temp\_MEI...\python313.dll
LoadLibrary: Le module specifie est introuvable
```

Downloader Studio n'extrait plus Python dans un dossier temporaire `_MEI...` au
lancement. Python, PyQt, yt-dlp et les DLL natives restent maintenant a cote de
l'executable dans le dossier installe.

### Installation

Telecharger puis lancer:

```text
DownloaderStudio_2.15.0_Setup.exe
```

Pour une version portable, copier le dossier complet:

```text
dist\DownloaderStudio\
```

Ne pas distribuer `DownloaderStudio.exe` seul.

---

## Espanol

### Novedades principales

- Correccion del error de inicio en Windows `Failed to load Python DLL`.
- Cambio del empaquetado PyInstaller `onefile` a `onedir`.
- FFmpeg ahora se incluye con la aplicacion y yt-dlp lo detecta automaticamente.
- Instalador de Windows mejorado con copia completa del bundle y version automatica.
- Actualizacion de dependencias principales, incluido yt-dlp.

### Correccion critica

Esta version corrige fallos de inicio reportados en algunos PCs Windows:

```text
Failed to load Python DLL
C:\Users\...\AppData\Local\Temp\_MEI...\python313.dll
LoadLibrary: No se puede encontrar el modulo especificado
```

Downloader Studio ya no extrae Python en una carpeta temporal `_MEI...` al
iniciar. Python, PyQt, yt-dlp y las DLL nativas permanecen junto al ejecutable en
la carpeta instalada.

### Instalacion

Descargar y ejecutar:

```text
DownloaderStudio_2.15.0_Setup.exe
```

Para uso portable, copiar la carpeta completa:

```text
dist\DownloaderStudio\
```

No distribuir `DownloaderStudio.exe` solo.

---

## Deutsch

### Wichtigste Anderungen

- Behebt den Windows-Startfehler `Failed to load Python DLL`.
- Wechsel von PyInstaller `onefile` zu `onedir`.
- FFmpeg wird jetzt mit der Anwendung geliefert und automatisch von yt-dlp erkannt.
- Verbesserter Windows-Installer mit vollstaendiger Bundle-Installation und automatischer Versionierung.
- Aktualisierte Hauptabhaengigkeiten, einschliesslich yt-dlp.

### Kritische Korrektur

Diese Version behebt Startfehler auf einigen Windows-PCs:

```text
Failed to load Python DLL
C:\Users\...\AppData\Local\Temp\_MEI...\python313.dll
LoadLibrary: Das angegebene Modul wurde nicht gefunden
```

Downloader Studio extrahiert Python beim Start nicht mehr in einen temporaeren
`_MEI...` Ordner. Python, PyQt, yt-dlp und native DLLs bleiben nun neben der
ausfuehrbaren Datei im Installationsordner.

### Installation

Herunterladen und ausfuehren:

```text
DownloaderStudio_2.15.0_Setup.exe
```

Fuer portable Nutzung den kompletten Ordner kopieren:

```text
dist\DownloaderStudio\
```

`DownloaderStudio.exe` nicht einzeln verteilen.

---

## Technical details

### Changes since v2.12

- PyInstaller build now outputs:
  `dist\DownloaderStudio\DownloaderStudio.exe`.
- Required runtime files are stored in:
  `dist\DownloaderStudio\_internal\`.
- Bundled FFmpeg path:
  `dist\DownloaderStudio\ffmpeg\bin\`.
- The build script can copy a local FFmpeg install or download a release build.
- The installer copies the complete PyInstaller `onedir` bundle.
- Update installer launch now uses:
  `/VERYSILENT /NORESTART`.
- Search result scrollbars and the `Select All` button were improved.

### Dependencies

| Component | Version / detail |
|---|---|
| App version | 2.15.0 |
| Python runtime | CPython 3.13 x64 |
| UI framework | PyQt5 5.15.11 |
| PyQt5-sip | 12.18.0 |
| Download engine | yt-dlp 2026.6.9 |
| FFmpeg | Bundled release build |
| Build tools | PyInstaller + Inno Setup |
| Platform | Windows 10/11 |

### Upgrade notes

- Prefer `DownloaderStudio_2.15.0_Setup.exe` over older portable `onefile` builds.
- Uninstall older builds if Windows still launches an old `DownloaderStudio.exe`.
- If Windows Defender quarantined files from an older version, remove the old
  installation folder before reinstalling.
