# Build - Downloader Studio

## Installation, une fois

Utilise Python 3.13 x64 pour les releases Windows. Ne compile pas l'application
avec Python 3.14 ou 3.15 pour ce projet: PyInstaller peut produire un binaire
qui plante au lancement avec `Failed to load Python DLL`.

```powershell
py -3.13 -m venv .venv-build
.\.venv-build\Scripts\python -m pip install --upgrade pip
.\.venv-build\Scripts\python -m pip install -r requirements.txt pyinstaller
```

Inno Setup, pour produire l'installateur:

- https://jrsoftware.org/isdl.php

## Compiler tout

```powershell
.\.venv-build\Scripts\python build_exe.py
```

Le script compile:

1. L'application avec PyInstaller en mode `onedir`.
2. FFmpeg complet dans le dossier de l'application.
3. L'installateur Inno Setup.

Par defaut, le build est incremental: il garde le dossier
`dist\DownloaderStudio\` et ne supprime pas les gros fichiers deja presents
comme FFmpeg ou les DLL Python/PyQt. PyInstaller construit dans
`dist\.pyinstaller\`, puis le resultat est fusionne dans le dossier final.
FFmpeg est aussi garde en cache dans `dist\.ffmpeg-cache\bin`.

## Resultat

```text
dist\DownloaderStudio\DownloaderStudio.exe   <- app portable
dist\DownloaderStudio\ffmpeg\bin\            <- FFmpeg utilise par l'app
dist\DownloaderStudio*_Setup.exe             <- installateur
```

Distribue en priorite le dernier `DownloaderStudio*_Setup.exe`.
Pour une version portable, distribue le dossier `dist\DownloaderStudio\` complet,
pas seulement `DownloaderStudio.exe`.

## Pourquoi `onedir`

Le mode PyInstaller `onefile` extrait Python dans `%TEMP%\_MEI...` au lancement.
Sur certains PC, Defender, un antivirus ou une politique de droits peut bloquer
ou supprimer `python313.dll`, ce qui provoque `Failed to load Python DLL`.

Le mode `onedir` garde `python313.dll`, `python3.dll`, les DLL PyQt et FFmpeg a
cote de l'executable installe. Le lancement ne depend donc plus d'une extraction
temporaire.

## Options

```powershell
# Tout, par defaut
.\.venv-build\Scripts\python build_exe.py

# Clean du cache PyInstaller uniquement, sans supprimer dist\DownloaderStudio
.\.venv-build\Scripts\python build_exe.py --clean-build

# Sans FFmpeg
.\.venv-build\Scripts\python build_exe.py --no-ffmpeg

# Sans installer Inno
.\.venv-build\Scripts\python build_exe.py --no-installer

# Sans les deux
.\.venv-build\Scripts\python build_exe.py --no-ffmpeg --no-installer
```

Depuis Git Bash:

```bash
# Build rapide, sans reinstall pip si les dependances existent deja
./build.sh

# Reinstaller/mettre a jour les dependances puis builder
./build.sh --install-deps
```

## Erreurs courantes

**`Failed to load Python DLL` au lancement**

- Verifie que l'utilisateur lance la build `onedir` actuelle ou l'installateur actuel.
- Ne distribue pas l'ancien `dist\DownloaderStudio.exe` seul.
- Si le PC bloque encore le lancement, verifier l'historique Windows Defender.
- Installer/reparer Microsoft Visual C++ Redistributable 2015-2022 x64.

**`FFmpeg download failed`**

- Verifier la connexion internet.
- Ou installer FFmpeg localement dans `C:\ffmpeg\bin`.
- Puis relancer `.\.venv-build\Scripts\python build_exe.py`.
