# 🚀 Build - Downloader Studio

Un script pour tout faire. C'est simple.

## Installation (une fois)

Utilise Python 3.13 x64 pour les releases Windows. Ne compile pas l'EXE avec
Python 3.14 ou 3.15 pour ce projet: PyInstaller peut produire un binaire qui
plante au lancement avec `Failed to load Python DLL`.

```powershell
py -3.13 -m venv .venv-build
.\.venv-build\Scripts\python -m pip install --upgrade pip
.\.venv-build\Scripts\python -m pip install -r requirements.txt pyinstaller
```

Inno Setup (pour installer):
- https://jrsoftware.org/isdl.php

## Compiler tout

```bash
.\.venv-build\Scripts\python build_exe.py
```

Ça compile:
1. ✓ App avec PyInstaller
2. ✓ FFmpeg complet (bin embarque dans l'installateur)
3. ✓ Installateur Inno Setup

**Temps**: 2-5 min (dépend FFmpeg)

## Résultat

```
dist/DownloaderStudio.exe          ← App portable
dist/DownloaderStudio*_Setup.exe   <- Installateur (distribue le plus recent)
dist/ffmpeg/bin/                   <- FFmpeg complet utilise par l'app
```

## Utilisation

### App portable
```bash
dist/DownloaderStudio.exe
```

### Installateur (utilisateur)
1. Double-clique le dernier `DownloaderStudio*_Setup.exe`
2. FFmpeg est installe automatiquement avec l'application
3. App prête

## Options

```bash
# Tout (par défaut)
.\.venv-build\Scripts\python build_exe.py

# Sans FFmpeg
.\.venv-build\Scripts\python build_exe.py --no-ffmpeg

# Sans installer Inno
.\.venv-build\Scripts\python build_exe.py --no-installer

# Sans les deux
.\.venv-build\Scripts\python build_exe.py --no-ffmpeg --no-installer
```

## FFmpeg

### Local
Si tu as FFmpeg à `C:\ffmpeg\bin`, il va l'utiliser automatiquement.

### Télécharger
Sinon, le script telecharge un build release de FFmpeg et copie tout le dossier `bin`.

## Erreurs Courantes

**"PyInstaller not found"**
```powershell
.\.venv-build\Scripts\python -m pip install pyinstaller
```

**"Failed to load Python DLL" au lancement**
- Supprime `build/` et `dist/`.
- Recompile avec Python 3.13 x64 via `.venv-build`.
- Verifie que la build n'utilise pas Python 3.14/3.15.

**"Inno Setup not found"**
- Télécharger: https://jrsoftware.org/isdl.php
- Installer normalement
- Relancer `.\.venv-build\Scripts\python build_exe.py`

**"FFmpeg download failed"**
- Vérifier internet
- Ou installer manuellement: https://ffmpeg.org/download.html
- Continuer avec `--no-ffmpeg`

## Checklist

- [ ] PyInstaller installé
- [ ] Inno Setup installé (optionnel)
- [ ] `.\.venv-build\Scripts\python build_exe.py` fonctionne
- [ ] `dist/DownloaderStudio.exe` existe
- [ ] `dist/DownloaderStudio*_Setup.exe` cree (si Inno)
- [ ] Distribuer l'installer

---

**C'est tout!** Un script = tout compilé. 🎉
