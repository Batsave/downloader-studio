"""
PyInstaller build script for Downloader Studio
Creates executable compatible with Inno Setup
"""

import os
import shutil
import subprocess
import sys

def build():
    """Build executable with PyInstaller"""
    
    # Clean previous builds
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned {folder}/")
    
    # PyInstaller command
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--name=DownloaderStudio',
        '--onefile',
        '--windowed',
        '--icon=assets/downloader-studio-logo.ico',
        f'--add-data=assets{os.pathsep}assets',
        f'--add-data=i18n{os.pathsep}i18n',
        '--collect-all=PyQt5',
        '--collect-all=yt_dlp',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=yt_dlp',
        '--hidden-import=requests',
        'main.py'
    ]
    
    print("Building executable with PyInstaller...")
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    
    if result.returncode == 0:
        print("\nOK: Build successful!")
        print("Executable: dist/DownloaderStudio.exe")
        print("\nNext steps:")
        print("1. Install Inno Setup")
        print("2. Run: iscc.exe Downloader_Studio.iss")
        print("3. Installer will be in: dist/DownloaderStudio_Setup.exe")
    else:
        print("\nERROR: Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    build()
