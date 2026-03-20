# Startup Update Check Guide

This app checks for updates on startup and shows an "Update Available" dialog with a **Download** button.

Default remote manifest URL:

`https://raw.githubusercontent.com/grego-hash/GORO/main/updates.json`

Lookup order:

1. `updates/manifest_url` (QSettings)
2. `GORO_UPDATE_URL` (environment variable)
3. Built-in default URL above
4. Local manifest fallback (`updates/manifest_path`, `root_dir\updates.json`, then project `data\updates.json`)

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

## 2) Optional local fallback (`updates.json` inside selected data folder)

If the user selected data folder is:

`D:\GORO\data`

then put the manifest at:

`D:\GORO\data\updates.json`

Primary lookup order:

1. Optional override setting `updates/manifest_path`
2. `root_dir\updates.json`
3. Built-in fallback: project `data\updates.json`

The app gets `root_dir` from the Data Folder selection in the UI.

## 3) Build and release the new installer

Example payload:

```json
{
  "latest_version": "2.4.0",
  "download_url": "GORO-Setup-2.4.0-2026-03-19_0900.exe",
  "release_notes": "- New update checker\n- Performance improvements\n- Bug fixes"
}
```

For local update manifests, `download_url` can be omitted or set to just the installer filename.
GORO resolves it from the same folder as `updates.json`.

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

The build script updates both `data\updates.json` and the top-level `updates.json` automatically.

The build script writes `download_url` as the generated installer filename so local checks resolve from the same folder as `updates.json`.

Upload the produced installer to GitHub Releases and update repository `updates.json`.

## Runtime behavior

- Check runs after startup with a short delay.
- By default, check runs on every startup (`UPDATE_CHECK_INTERVAL_HOURS = 0`).
- If `UPDATE_CHECK_INTERVAL_HOURS` is set above 0, checks are throttled by that many hours.
- If user clicks **Skip This Version**, that exact version is suppressed on future checks.
- If user clicks **Download**, the installer URL opens in the default browser.

## Optional QSettings keys

- `updates/enabled` (`true` or `false`)
- `updates/manifest_path` (optional full path override)
- `updates/skipped_version` (string, managed by app)
- `updates/last_check_utc` (ISO timestamp, managed by app)
