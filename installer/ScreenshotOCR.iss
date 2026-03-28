#ifndef STAMP
  #define STAMP "dev"
#endif

[Setup]
AppId={{E1D99C1A-4EA0-4D62-A12C-8EBE4A5CB2A2}
AppName=Screenshot OCR
AppVersion=1.0.0
AppPublisher=YBGuoYang
DefaultDirName={localappdata}\Programs\ScreenshotOCR
DefaultGroupName=Screenshot OCR
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=ScreenshotOCR_Setup_{#STAMP}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\ScreenshotOCR.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional tasks:"; Flags: unchecked

[Files]
Source: "..\dist\ScreenshotOCR.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\config\hotkey_config.json"; DestDir: "{app}\config"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Screenshot OCR"; Filename: "{app}\ScreenshotOCR.exe"
Name: "{autodesktop}\Screenshot OCR"; Filename: "{app}\ScreenshotOCR.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ScreenshotOCR.exe"; Description: "Launch Screenshot OCR"; Flags: nowait postinstall skipifsilent
