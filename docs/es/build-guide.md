# 🔨 Guía de Compilación - Downloader Studio

Cómo compilar Downloader Studio para distribución.

## Requisitos Previos

- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- Inno Setup (para crear el instalador de Windows)

## Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## Paso 2: Crear el Ejecutable

```bash
python build_exe.py
```

Esto crea:
- `dist/DownloaderStudio.exe` - Ejecutable independiente

## Paso 3: Crear Instalador de Windows

### Instalar Inno Setup

1. Descargue desde: https://jrsoftware.org/isdl.php
2. Instálelo
3. Abra `Downloader_Studio.iss` con Inno Setup
4. Haga clic en **Compilar** o ejecute:

```bash
iscc.exe Downloader_Studio.iss
```

Esto crea:
- `dist/DownloaderStudio_Setup.exe` - Instalador completo de Windows

## Estructura de Directorios

```
dist/
├── DownloaderStudio.exe       ← Ejecutable independiente
├── DownloaderStudio_Setup.exe ← Instalador de Windows
└── ... (dependencias)
```

## Solución de Problemas

### PyInstaller no encuentra módulos

Agregue al script `build_exe.py`:
```python
--hidden-import=module_name
```

### El icono no aparece

Verifique que `assets/downloader-studio-logo.ico` exista.

### Inno Setup no compila

- Verifique los terminadores de línea (CRLF)
- Verifique que la carpeta `dist/` exista con todos los archivos
- Ejecute como Administrador

## Proceso de Lanzamiento

Para cada versión:

1. Actualice `__version__` en `app/__init__.py`
2. Actualice la versión en `Downloader_Studio.iss`
3. Pruebe la aplicación
4. Compile: `python build_exe.py`
5. Cree el instalador: `iscc.exe Downloader_Studio.iss`
6. Cree una versión de GitHub con los archivos

## Tamaños de Archivo

- Ejecutable: ~50-100 MB
- Instalador: ~30-50 MB

---

Ver tambi?n: [Inicio r?pido](quick-start.md)

