; Downloader Studio Installer with FFmpeg Integration
; Uses NSIS Modern UI and INetC for downloads

!include "MUI2.nsh"
!include "x64.nsh"
!include "FileFunc.nsh"
!include "nsDialogs.nsh"

; Load INetC plugin
!addincludedir "."
!addplugindir "."

; Basic Settings
Name "Downloader Studio"
OutFile "DownloaderStudio-Installer.exe"
InstallDir "$PROGRAMFILES\Downloader Studio"
InstallDirRegKey HKCU "Software\Downloader Studio" ""
RequestExecutionLevel admin

; Variables
Var FFmpegInstalled

; Version Info
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "Downloader Studio"
VIAddVersionKey "CompanyName" "Downloader Studio"
VIAddVersionKey "FileDescription" "Download videos and audio from multiple sources"
VIAddVersionKey "FileVersion" "1.0.0"

; MUI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"

; Install Section
Section "Downloader Studio"
  SetOutPath "$INSTDIR"

  ; Copy application files
  File "dist\DownloaderStudio.exe"
  File /r "dist\*.*"

  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\Downloader Studio"
  CreateShortCut "$SMPROGRAMS\Downloader Studio\Downloader Studio.lnk" "$INSTDIR\DownloaderStudio.exe"
  CreateShortCut "$SMPROGRAMS\Downloader Studio\Uninstall.lnk" "$INSTDIR\uninstall.exe"

  ; Create Desktop shortcut
  CreateShortCut "$DESKTOP\Downloader Studio.lnk" "$INSTDIR\DownloaderStudio.exe"

  ; Store install folder
  WriteRegStr HKCU "Software\Downloader Studio" "" $INSTDIR

  ; Add to Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Downloader Studio" "DisplayName" "Downloader Studio"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Downloader Studio" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Downloader Studio" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Downloader Studio" "DisplayVersion" "1.0.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Downloader Studio" "Publisher" "Downloader Studio"

  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

SectionEnd

; FFmpeg Section
Section "FFmpeg (required for audio)" SecFFmpeg
  DetailPrint "Installing FFmpeg..."
  Call InstallFFmpeg
SectionEnd

; Uninstall Section
Section "Uninstall"
  Delete "$INSTDIR\uninstall.exe"
  RMDir /r "$INSTDIR"

  Delete "$SMPROGRAMS\Downloader Studio\Downloader Studio.lnk"
  Delete "$SMPROGRAMS\Downloader Studio\Uninstall.lnk"
  RMDir "$SMPROGRAMS\Downloader Studio"

  Delete "$DESKTOP\Downloader Studio.lnk"

  DeleteRegKey HKCU "Software\Downloader Studio"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Downloader Studio"
SectionEnd

; FFmpeg Installation Function
Function InstallFFmpeg
  ; Use local ffmpeg directory bundled with installer
  StrCpy $0 "$INSTDIR\ffmpeg"

  IfFileExists "$0\bin\ffmpeg.exe" FFmpegExists

  ; If ffmpeg directory exists in dist, copy it
  IfFileExists "dist\ffmpeg\bin\ffmpeg.exe" CopyLocalFFmpeg

  DetailPrint "FFmpeg not found locally. Will download on first use."
  DetailPrint "Users can manually install FFmpeg from: https://ffmpeg.org/download.html"
  GoTo FFmpegDone

CopyLocalFFmpeg:
  DetailPrint "Copying bundled FFmpeg..."
  CreateDirectory "$0"
  CopyFiles "dist\ffmpeg\*.*" "$0\"
  DetailPrint "FFmpeg copied successfully"
  Call AddToPath
  GoTo FFmpegDone

FFmpegExists:
  DetailPrint "FFmpeg already installed at: $0"

FFmpegDone:
  DetailPrint "FFmpeg installation complete"
FunctionEnd

; Add FFmpeg to PATH
Function AddToPath
  StrCpy $0 "$INSTDIR\ffmpeg\bin"
  StrCpy $1 "PATH"

  ReadRegStr $2 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "$1"

  ${StrContains} $3 "$0" "$2"
  ${If} $3 == ""
    WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "$1" "$2;$0"
    DetailPrint "Added FFmpeg to system PATH: $0"

    ; Broadcast environment change
    SendMessage ${HWND_BROADCAST} ${WM_SETTINGCHANGE} 0 "STR:Environment" /TIMEOUT=5000
  ${Else}
    DetailPrint "FFmpeg already in PATH"
  ${EndIf}
FunctionEnd

; Section Descriptions
LangString DESC_SecFFmpeg ${LANG_ENGLISH} "FFmpeg binaries for audio/video processing (required)"
LangString DESC_SecFFmpeg ${LANG_FRENCH} "Binaires FFmpeg pour traiter l'audio/vidéo (requis)"

!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecFFmpeg} $(DESC_SecFFmpeg)
!insertmacro MUI_FUNCTION_DESCRIPTION_END
