# Architecture - Downloader Studio

Downloader Studio est une application PyQt5 structurée autour de trois zones principales : interface, moteur de téléchargement et ressources partagées.

## Vue d'ensemble

```text
main.py
└── app/ui/main_window.py
    ├── pages/search_page.py
    ├── pages/queue_page.py
    ├── pages/settings_page.py
    ├── pages/logs_page.py
    ├── minimal_window.py
    └── app/core/download_engine.py
        └── yt-dlp
```

## Interface

`app/ui/main_window.py` contient la fenêtre principale, la sidebar, le changement de thème, le splash screen et la reconstruction des pages quand la langue change.

Les pages sont séparées par responsabilité :

- `search_page.py` : recherche, sélection de format, téléchargement direct et ajout à la file.
- `queue_page.py` : file d'attente, progression globale et historique.
- `settings_page.py` : langue, thème, sources, formats, qualité et dossier de sortie.
- `logs_page.py` : journal d'activité et export texte.
- `minimal_window.py` : mode flottant compact activé avec `Ctrl+M`.

## Moteur

`app/core/download_engine.py` porte la logique de téléchargement :

- création des tâches ;
- déduplication de la file ;
- exécution asynchrone via `QThread` ;
- intégration `yt-dlp` ;
- signaux de progression, historique et logs.

Le dossier de sortie par défaut est `%USERPROFILE%\Downloads`.

## Traductions

Les textes applicatifs sont centralisés dans `i18n/translations.py`. Le changement de langue met à jour le traducteur global, reconstruit les pages et recrée la sidebar pour éviter les anciens widgets dans la mauvaise langue.

Langues disponibles :

- français ;
- anglais ;
- allemand ;
- espagnol.

## Ressources

`app/utils/resources.py` résout les chemins pour trois contextes :

1. exécution Python directe ;
2. exécutable PyInstaller ;
3. installation Inno Setup.

Les assets visuels sont dans `assets/`.

## Build

Le build Windows utilise :

- `build_exe.py` pour générer `dist/DownloaderStudio.exe` ;
- `Downloader_Studio.iss` pour produire l'installateur Windows.

Voir aussi : [Guide de construction](guide-construction.md).
