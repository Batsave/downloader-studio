# Guide de construction - Downloader Studio

Ce guide décrit le build local de l'exécutable Windows et de l'installateur.

## Prérequis

- Python 3.8 ou plus récent ;
- dépendances du projet installées ;
- PyInstaller ;
- Inno Setup 6 pour l'installateur Windows.

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Générer l'exécutable

```bash
python build_exe.py
```

Sortie attendue :

```text
dist/
└── DownloaderStudio.exe
```

## Générer l'installateur

1. Installez Inno Setup depuis https://jrsoftware.org/isdl.php.
2. Ouvrez `Downloader_Studio.iss`.
3. Compilez le script depuis Inno Setup, ou lancez :

```bash
iscc.exe Downloader_Studio.iss
```

Sortie attendue :

```text
dist/
├── DownloaderStudio.exe
└── DownloaderStudio_Setup.exe
```

## Avant publication

Vérifiez au minimum :

- l'application démarre avec le splash screen ;
- la langue peut passer de EN à FR sans texte résiduel ;
- le dossier de sortie par défaut est `%USERPROFILE%\Downloads` ;
- `downloader_settings.json` n'est pas présent dans le commit ;
- l'installateur lance bien `DownloaderStudio.exe`.

## Dépannage

Si PyInstaller ne trouve pas un module, ajoutez le module dans `build_exe.py`.

Si Inno Setup échoue, vérifiez que `dist/DownloaderStudio.exe` existe et que `Downloader_Studio.iss` pointe vers les bons fichiers.

Voir aussi : [Démarrage rapide](demarrage-rapide.md).
