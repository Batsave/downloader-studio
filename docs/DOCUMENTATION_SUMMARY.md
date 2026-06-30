# Documentation Summary

This folder contains the visual documentation hub and the Markdown guides for Downloader Studio.

## Structure

```text
docs/
├── index.html                  # Visual documentation hub
├── fr/
│   ├── index.md
│   ├── demarrage-rapide.md
│   ├── guide-construction.md
│   ├── architecture.md
│   └── about.md
├── en/
│   ├── index.md
│   ├── quick-start.md
│   ├── build-guide.md
│   ├── architecture.md
│   └── about.md
├── de/
│   ├── index.md
│   ├── quick-start.md
│   ├── build-guide.md
│   ├── architecture.md
│   └── about.md
└── es/
    ├── index.md
    ├── quick-start.md
    ├── build-guide.md
    ├── architecture.md
    └── about.md
```

## Hub HTML

`docs/index.html` is a standalone static page. It uses the same dark surface, amber accent, compact cards, and sidebar rhythm as the PyQt application.

It links only to files that exist in this repository.

## Maintenance Rules

- Keep repository links pointed at `https://github.com/batsave/downloader-studio`.
- Do not commit `downloader_settings.json`; it is local user state.
- Keep the documented default output folder as `%USERPROFILE%\Downloads`.
- When adding a new guide, add it to the matching language `index.md` and to `docs/index.html`.

## Current Coverage

| Language | Index | Quick Start | Build | Architecture | About |
| --- | --- | --- | --- | --- | --- |
| French | yes | yes | yes | yes | yes |
| English | yes | yes | yes | yes | yes |
| German | yes | yes | yes | yes | yes |
| Spanish | yes | yes | yes | yes | yes |

Last updated: 30 June 2026.

