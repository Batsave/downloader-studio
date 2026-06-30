# Documentación de Downloader Studio

Esta sección reúne la documentación en español para instalar, usar, compilar y entender Downloader Studio.

## Guías

- [Inicio rápido](quick-start.md) - instalar la app, iniciarla y hacer la primera descarga.
- [Guía de compilación](build-guide.md) - crear el ejecutable PyInstaller y el instalador de Windows.
- [Arquitectura](architecture.md) - entender la interfaz PyQt, el motor de descarga y la capa i18n.
- [Acerca de](about.md) - objetivos del proyecto, funciones y notas de uso.

## Flujo habitual

1. Instala dependencias con `pip install -r requirements.txt`.
2. Ejecuta la app con `python main.py`.
3. Elige idioma, tema, formatos, calidad y carpeta de salida en Configuración.
4. Busca o pega una URL en la página de búsqueda.
5. Agrega resultados a la cola o descarga un elemento directamente.

## Valores predeterminados

- Carpeta de salida: `%USERPROFILE%\Downloads`
- Tema: oscuro
- Idioma: francés
- Formatos: MP3, MP4, WAV, M4A

## Enlaces

- Repositorio: https://github.com/batsave/downloader-studio
- Issues: https://github.com/batsave/downloader-studio/issues
- Licencia: [MIT](../../LICENSE)

