; Inno Setup 6 Script for Oqteris Desktop
; Organization: OriginSD
; Developer: Subhadip Dutta
; Application: Oqteris

#define MyAppName "Oqteris"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "OriginSD"
#define MyAppURL "https://originsd.vercel.app"
#define MyAppExeName "Oqteris.exe"

[Setup]
AppId={{D37E84B0-C2B1-4A59-86BC-9DFB83617260}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL=https://github.com/subhadip6869/Oqteris-Desktop/issues
AppUpdatesURL=https://github.com/subhadip6869/Oqteris-Desktop/releases
DefaultDirName={autopf}\OriginSD\Oqteris
DefaultGroupName=OriginSD\Oqteris
AllowNoIcons=yes
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=Oqteris-{#MyAppVersion}-Windows-x64-Setup
SetupIconFile=..\..\assets\icons\app\oqteris-logo.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "associatepdf"; Description: "Associate Oqteris with PDF files (.pdf)"; GroupDescription: "File Associations:"; Flags: checkedonce

[Files]
Source: "..\..\dist\Oqteris.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\..\assets\icons\document\oqteris-document.ico"; DestDir: "{app}\resources"; Flags: ignoreversion
Source: "..\..\assets\icons\app\oqteris-logo.ico"; DestDir: "{app}\resources"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\resources\oqteris-logo.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\resources\oqteris-logo.ico"

[Registry]
; Register Oqteris.PDF ProgID
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\resources\oqteris-document.ico,0"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associatepdf

; Associate .pdf extension
Root: HKA; Subkey: "Software\Classes\.pdf\OpenWithProgids"; ValueType: string; ValueName: "Oqteris.PDF"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatepdf

; Register with Windows RegisteredApplications
Root: HKLM; Subkey: "Software\OriginSD\Oqteris\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "Oqteris"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\OriginSD\Oqteris\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Professional Cross-Platform PDF Reader and Editor"
Root: HKLM; Subkey: "Software\OriginSD\Oqteris\Capabilities\FileAssociations"; ValueType: string; ValueName: ".pdf"; ValueData: "Oqteris.PDF"
Root: HKLM; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "Oqteris"; ValueData: "Software\OriginSD\Oqteris\Capabilities"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
