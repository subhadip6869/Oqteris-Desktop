; Inno Setup 6 Script for Oqteris Desktop
; Organization: OriginSD
; Developer: Subhadip Dutta
; Application: Oqteris

#define MyAppName "Oqteris"
#define MyAppVersion "1.2.1"
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

; In-place Update & Upgrade Behavior
UsePreviousAppDir=yes
UsePreviousGroup=yes
UsePreviousTasks=yes
UpdateUninstallLogAppName=yes
CloseApplications=yes
RestartApplications=yes
CloseApplicationsFilter=*.exe

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
; 1. Register Oqteris.PDF ProgID (Standard Windows Document Association)
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF"; ValueType: string; ValueName: "FriendlyTypeName"; ValueData: "PDF Document"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\resources\oqteris-document.ico"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF\CurVer"; ValueType: string; ValueName: ""; ValueData: "Oqteris.PDF"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF\shell"; ValueType: string; ValueName: ""; ValueData: "open"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF\shell\open"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "{#MyAppName}"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Oqteris.PDF\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associatepdf

; 2. Associate .pdf extension in HKCR / Software\Classes
Root: HKA; Subkey: "Software\Classes\.pdf"; ValueType: string; ValueName: ""; ValueData: "Oqteris.PDF"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\.pdf\OpenWithProgids"; ValueType: string; ValueName: "Oqteris.PDF"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\.pdf\OpenWithList\{#MyAppExeName}"; ValueType: string; ValueName: ""; ValueData: ""; Flags: uninsdeletekey; Tasks: associatepdf

; 3. Applications registration for Windows Default Apps & Open With dialog
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}"; ValueType: string; ValueName: "ApplicationCompany"; ValueData: "{#MyAppPublisher}"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\resources\oqteris-document.ico"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".pdf"; ValueData: ""; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\shell\open"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "{#MyAppName}"; Tasks: associatepdf
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associatepdf

; 4. App Paths registration
Root: HKA; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\{#MyAppExeName}"; ValueType: string; ValueName: "Path"; ValueData: "{app}"

; 5. Windows Default Programs / RegisteredApplications
Root: HKA; Subkey: "Software\OriginSD\Oqteris\Capabilities"; ValueType: string; ValueName: "ApplicationName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\OriginSD\Oqteris\Capabilities"; ValueType: string; ValueName: "ApplicationDescription"; ValueData: "Professional Cross-Platform PDF Reader and Editor"
Root: HKA; Subkey: "Software\OriginSD\Oqteris\Capabilities"; ValueType: string; ValueName: "ApplicationIcon"; ValueData: "{app}\resources\oqteris-logo.ico"
Root: HKA; Subkey: "Software\OriginSD\Oqteris\Capabilities\FileAssociations"; ValueType: string; ValueName: ".pdf"; ValueData: "Oqteris.PDF"
Root: HKA; Subkey: "Software\RegisteredApplications"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: "Software\OriginSD\Oqteris\Capabilities"; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
