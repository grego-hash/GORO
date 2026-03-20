# Startup Update Check Guide

This app checks for updates on startup and shows an "Update Available" dialog with a **Download** button.

Default remote manifest URL:

`https://raw.githubusercontent.com/grego-hash/GORO/main/updates.json`

Lookup order:

1. `updates/manifest_url` (QSettings)
2. `GORO_UPDATE_URL` (environment variable)
3. Built-in default URL above

## 1) Host `updates.json` on GitHub

Create/update the repository root `updates.json` with a public installer URL:

```json
{
  "latest_version": "2.5.2",
  "download_url": "https://github.com/grego-hash/GORO/releases/download/v2.5.2/GORO-Setup-2.5.2-2026-03-19_1206.exe",
  "release_notes": "- Improvements\n- Bug fixes"
}
```

Use this as your manifest URL:

`https://raw.githubusercontent.com/grego-hash/GORO/main/updates.json`

## 2) Build and release the new installer

Example payload:

```json
{
  "latest_version": "2.4.0",
  "download_url": "https://github.com/grego-hash/GORO/releases/download/v2.4.0/GORO-Setup-2.4.0-2026-03-19_0900.exe",
  "release_notes": "- New update checker\n- Performance improvements\n- Bug fixes"
}
```

Supported key aliases:

- `latest_version` or `version`
- `download_url`, `url`, or `installer_url`
- `release_notes` or `notes`


```powershell
.\build_installer.ps1 -AppVersion 2.4.0
```

Or, if you want the installer written to a release share:

```powershell
.\build_installer.ps1 -AppVersion 2.4.0 -InstallerOutputDir "Z:\GregO"
```

The build script updates the top-level `updates.json` automatically.

Upload the produced installer to GitHub Releases and update repository `updates.json`.

## Runtime behavior

- Check runs after startup with a short delay.
- By default, check runs on every startup (`UPDATE_CHECK_INTERVAL_HOURS = 0`).
- If `UPDATE_CHECK_INTERVAL_HOURS` is set above 0, checks are throttled by that many hours.
- If user clicks **Skip This Version**, that exact version is suppressed on future checks.
- If user clicks **Download**, the installer URL opens in the default browser.

## Optional QSettings keys

- `updates/enabled` (`true` or `false`)
- `updates/manifest_url` (optional URL override)
- `updates/skipped_version` (string, managed by app)
- `updates/last_check_utc` (ISO timestamp, managed by app)
