[Setup]
AppName=VORT Editor
AppVersion=2.3.3
DefaultDirName={pf}\VORT Editor
DefaultGroupName=VORT Editor
OutputDir=output
OutputBaseFilename=VORTInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\CLI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\VORT Editor"; Filename: "{app}\CLI.exe"
Name: "{commondesktop}\VORT Editor"; Filename: "{app}\CLI.exe"

[Registry]

Root: HKCR; Subkey: ".vort"; ValueType: string; ValueName: ""; ValueData: "VORTFile"; Flags: uninsdeletevalue

Root: HKCR; Subkey: "VORTFile"; ValueType: string; ValueName: ""; ValueData: "New VORT File"; Flags: uninsdeletekey

Root: HKCR; Subkey: "VORTFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CLI.exe,0"

Root: HKCR; Subkey: "VORTFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CLI.exe"" ""%1"""

Root: HKCR; Subkey: ".vort\ShellNew"; ValueType: string; ValueName: "NullFile"; ValueData: ""

[Run]
Filename: "{app}\CLI.exe"; Description: "Launch VORT Editor"; Flags: nowait postinstall skipifsilent