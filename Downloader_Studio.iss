; Inno Setup Script for Downloader Studio with FFmpeg auto-installation
; Builds with PyInstaller and automatically downloads/installs FFmpeg

#define MyAppName "Downloader Studio"
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0-dev"
#endif
#define MyAppPublisher "BS Studio"
#define MyAppExeName "DownloaderStudio.exe"
#define MyAppURL "https://github.com/batsave/downloader-studio"

[Setup]
AppId={{A1B2C3D4-E5F6-47A8-B9C0-D1E2F3A4B5C6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputBaseFilename=DownloaderStudio_{#MyAppVersion}_Setup
OutputDir=dist
Compression=lzma
SolidCompression=yes
SetupIconFile=assets\downloader-studio-logo.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Complete PyInstaller onedir bundle.
Source: "dist\DownloaderStudio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Assets
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Application configuration reference
Source: "config.py"; DestDir: "{app}"; Flags: ignoreversion

; License and README
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

; FFmpeg is normally already included in dist\DownloaderStudio\ffmpeg\bin.

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Code]
var
  FFmpegInstalled: Boolean;
  DownloadAttempted: Boolean;

function CheckFFmpegInstalled(): Boolean;
var
  FFmpegPath: string;
begin
  FFmpegPath := ExpandConstant('{app}\ffmpeg\bin');
  Result := FileExists(FFmpegPath + '\ffmpeg.exe') and FileExists(FFmpegPath + '\ffprobe.exe');
end;

function DownloadAndExtractFFmpeg(): Boolean;
var
  TempDir: string;
  DownloadUrl: string;
  ZipFile: string;
  ResultCode: Integer;
  PowerShellCmd: string;
  FFmpegBin: string;
begin
  Result := False;
  DownloadAttempted := True;
  TempDir := ExpandConstant('{tmp}');
  ZipFile := TempDir + '\ffmpeg.zip';
  FFmpegBin := ExpandConstant('{app}\ffmpeg\bin');

  Log('Downloading FFmpeg...');

  DownloadUrl := 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip';

  ForceDirectories(FFmpegBin);

  { Download using PowerShell and copy the complete FFmpeg bin folder. }
  PowerShellCmd := 'powershell -NoProfile -Command "' +
                   '$ErrorActionPreference = ''Stop''; ' +
                   'if (Test-Path ''' + TempDir + '\ffmpeg-extract'') { Remove-Item -LiteralPath ''' + TempDir + '\ffmpeg-extract'' -Recurse -Force }; ' +
                   'New-Item -ItemType Directory -Force -Path ''' + TempDir + '\ffmpeg-extract'' | Out-Null; ' +
                   '[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; ' +
                   '(New-Object Net.WebClient).DownloadFile(''' + DownloadUrl + ''', ''' + ZipFile + '''); ' +
                   'Add-Type -AssemblyName System.IO.Compression.FileSystem; ' +
                   '[System.IO.Compression.ZipFile]::ExtractToDirectory(''' + ZipFile + ''', ''' + TempDir + '\ffmpeg-extract''); ' +
                   '$bin = Get-ChildItem -Path ''' + TempDir + '\ffmpeg-extract'' -Directory -Recurse | Where-Object { Test-Path (Join-Path $_.FullName ''ffmpeg.exe'') -and Test-Path (Join-Path $_.FullName ''ffprobe.exe'') } | Select-Object -First 1; ' +
                   'if (-not $bin) { throw ''FFmpeg bin directory not found'' }; ' +
                   'Copy-Item -Path (Join-Path $bin.FullName ''*'') -Destination ''' + FFmpegBin + ''' -Recurse -Force"';

  if Exec(ExpandConstant('{cmd}'), '/c ' + PowerShellCmd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
    begin
      Result := CheckFFmpegInstalled();
      if Result then
      begin
        Log('FFmpeg installed successfully');
      end;
    end;
  end;

  { Clean up temporary files }
  if FileExists(ZipFile) then
    DeleteFile(ZipFile);

  if not Result then
  begin
    Log('FFmpeg download failed');
  end;
end;

procedure InitializeWizard();
begin
  { The app install directory is not available yet during wizard initialization. }
  FFmpegInstalled := False;
  DownloadAttempted := False;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    FFmpegInstalled := CheckFFmpegInstalled();

    if WizardSilent() and not FFmpegInstalled and not DownloadAttempted then
    begin
      DownloadAndExtractFFmpeg();
      FFmpegInstalled := CheckFFmpegInstalled();
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  { Check FFmpeg after installation, before launching app }
  if CurPageID = wpFinished then
  begin
    if not FFmpegInstalled and not DownloadAttempted then
    begin
      if MsgBox('FFmpeg is not installed.' + #13#10 +
                'Would you like to download and install it now?' + #13#10 +
                '(Required for audio/video processing)',
                mbConfirmation, MB_YESNO) = IDYES then
      begin
        DownloadAndExtractFFmpeg();
        FFmpegInstalled := CheckFFmpegInstalled();
      end;
    end;
  end;
end;

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
