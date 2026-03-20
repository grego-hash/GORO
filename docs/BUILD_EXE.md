# Build Installable EXE (Windows)

This project now includes:

- `goro.spec` (PyInstaller config)
- `build_installer.ps1` (automated build script)
- `installer.iss` (Inno Setup installer definition)

## Quick Start

From the project root (`GORO 2.3`):

```powershell
.\build_installer.ps1
```

What it does:

1. Installs/updates `pyinstaller` in `.venv`
2. Downloads/bundles Poppler and downloads the Tesseract installer for OCR support
3. Builds `dist\GORO\GORO.exe` using `goro.spec`
4. If Inno Setup is installed, creates a unique installer like `installers\GORO-Setup-2.0-2026-02-24_1542.exe` that provisions Tesseract during GORO setup

Important:

- Running `build_installer.ps1` does **not** install Tesseract on the build machine
- The generated GORO installer EXE installs Tesseract automatically for the end user into the GORO app folder
- Running `dist\GORO\GORO.exe` directly bypasses that installer step, so OCR provisioning will not happen automatically there

## Set app version (optional)

```powershell
.\build_installer.ps1 -AppVersion 2.1.0
```

This version value is embedded in installer metadata and filename.

## Set installer output folder (optional)

```powershell
.\build_installer.ps1 -InstallerOutputDir "Z:\GregO"
```

You can combine both options:

```powershell
.\build_installer.ps1 -AppVersion 2.4.0 -InstallerOutputDir "Z:\GregO"
```

When `-InstallerOutputDir` is set, the build also updates `updates.json` to point at the installer generated in that folder.

## If Inno Setup is not installed

Install **Inno Setup 6**:

https://jrsoftware.org/isinfo.php

Then run:

```powershell
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\installer.iss"
```

## Build app only (no installer)

```powershell
.\build_installer.ps1 -SkipInstaller
```

## Output

- App folder: `dist\GORO\`
- App executable: `dist\GORO\GORO.exe`
- Installer executable: `installers\GORO-Setup-<version>-<yyyy-mm-dd_HHNN>.exe`

## Project Layout Notes

- Build documentation lives in `docs\`
- Application icon assets are in `assets\icons\` (referenced by `goro.spec` and `installer.iss`)
- Bundled external runtime tools are staged under `tools\poppler-windows\`
- The embedded Tesseract installer is cached under `tools\installers\`
