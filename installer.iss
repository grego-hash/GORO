#define MyAppName "GORO"
#ifndef MyAppVersion
	#define MyAppVersion "2.0"
#endif
#ifndef InstallerOutputDir
	#define InstallerOutputDir "installers"
#endif
#define MyAppPublisher "Stockham Construction, Inc"
#define MyAppExeName "GORO.exe"
#define TesseractInstallerName "tesseract-ocr-w64-setup-5.5.0.20241111.exe"
#define BuildStamp GetDateTimeString('yyyy-mm-dd_HHNN', '-', ':')

[Setup]
AppId={{52D306E9-6E6D-4B5D-B43C-5AF6A8F1C6C6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir={#InstallerOutputDir}
OutputBaseFilename={#MyAppName}-Setup-{#MyAppVersion}-{#BuildStamp}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
SetupIconFile=assets\icons\GORO_LOGO.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Recursive copy includes bundled runtime dependencies such as Poppler.
Source: "dist\GORO\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Include the official Tesseract installer so GORO setup can provision OCR automatically.
Source: "tools\installers\{#TesseractInstallerName}"; DestDir: "{tmp}"; Flags: deleteafterinstall ignoreversion; Check: FileExists(ExpandConstant('{src}\tools\installers\{#TesseractInstallerName}'))

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; AppUserModelID: "OropezaApps.GORO"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"; AppUserModelID: "OropezaApps.GORO"; Tasks: desktopicon

[Run]
Filename: "{tmp}\{#TesseractInstallerName}"; Parameters: "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /DIR=""{app}\tesseract-ocr"""; StatusMsg: "Installing OCR engine for scanned PDF support..."; Flags: waituntilterminated; Check: not FileExists(ExpandConstant('{app}\tesseract-ocr\tesseract.exe')) and FileExists(ExpandConstant('{tmp}\{#TesseractInstallerName}'))
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
