#ifndef MyAppVersion
  #define MyAppVersion "3.1.1"
#endif

[Setup]
AppId={{6FCF9AB8-03DF-4544-949C-9F71241AACFD}
AppName=VOCALSPROUT
AppVersion={#MyAppVersion}
AppPublisher=VOCALSPROUT
DefaultDirName={autopf}\VOCALSPROUT
DefaultGroupName=VOCALSPROUT
OutputDir=..\release
OutputBaseFilename=VOCALSPROUT-{#MyAppVersion}-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\VOCALSPROUT.exe

[InstallDelete]
; Same AppId as AYLO, so this upgrades an existing AYLO install in place.
; Remove the old executable and shortcuts left over from AYLO.
Type: files; Name: "{app}\Aylo.exe"
Type: files; Name: "{app}\Aylo Quick Start.txt"
Type: files; Name: "{autoprograms}\Aylo.lnk"
Type: files; Name: "{autodesktop}\Aylo.lnk"

[Files]
Source: "..\dist\VOCALSPROUT.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\FRIEND_TESTING.md"; DestDir: "{app}"; DestName: "VOCALSPROUT Quick Start.txt"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\VOCALSPROUT"; Filename: "{app}\VOCALSPROUT.exe"
Name: "{autodesktop}\VOCALSPROUT"; Filename: "{app}\VOCALSPROUT.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\VOCALSPROUT.exe"; Description: "Launch VOCALSPROUT"; Flags: nowait postinstall skipifsilent
