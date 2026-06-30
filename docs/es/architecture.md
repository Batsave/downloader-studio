# Arquitectura - Downloader Studio

Downloader Studio es una aplicación PyQt5 organizada alrededor de tres áreas principales: interfaz, motor de descarga y recursos compartidos.

## Vista general

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

## Interfaz

`app/ui/main_window.py` contiene la ventana principal, la barra lateral, el cambio de tema, la pantalla inicial y la reconstrucción de páginas al cambiar de idioma.

Las páginas se separan por responsabilidad:

- `search_page.py`: búsqueda, formato, descarga directa y cola.
- `queue_page.py`: cola, progreso global e historial.
- `settings_page.py`: idioma, tema, fuentes, formatos, calidad y carpeta de salida.
- `logs_page.py`: registro de actividad y exportación de texto.
- `minimal_window.py`: modo flotante compacto con `Ctrl+M`.

## Motor

`app/core/download_engine.py` contiene la lógica de descarga:

- creación de tareas;
- deduplicación de la cola;
- ejecución asíncrona con `QThread`;
- integración con `yt-dlp`;
- señales de progreso, historial y logs.

La carpeta de salida predeterminada es `%USERPROFILE%\Downloads`.

## Traducciones

Los textos de la aplicación están centralizados en `i18n/translations.py`. Al cambiar de idioma, la app actualiza el traductor global, reconstruye las páginas y recrea la barra lateral para evitar widgets antiguos en otro idioma.

Idiomas disponibles:

- francés;
- inglés;
- alemán;
- español.

## Recursos

`app/utils/resources.py` resuelve rutas para tres contextos:

1. ejecución directa con Python;
2. ejecutable PyInstaller;
3. instalación Inno Setup.

Los recursos visuales están en `assets/`.

## Build

El build de Windows usa:

- `build_exe.py` para generar `dist/DownloaderStudio.exe`;
- `Downloader_Studio.iss` para generar el instalador de Windows.

Ver también: [Guía de compilación](build-guide.md).
