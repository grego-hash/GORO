param(
    [switch]$SkipInstaller,
    [string]$AppVersion,
    [string]$InstallerOutputDir,
    # GitHub Release options
    [switch]$SkipGitHubRelease,
    [string]$GitHubToken,       # Falls back to $env:GITHUB_TOKEN if empty
    [string]$ReleaseNotes       # Optional release notes text
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

function Test-AppVersionFormat {
    param(
        [string]$Version
    )

    # Accept SemVer-like values: 1.2.3, 1.2.3-beta1, 1.2.3-beta.1+build5
    $pattern = '^\d+\.\d+\.\d+(?:-[0-9A-Za-z\.-]+)?(?:\+[0-9A-Za-z\.-]+)?$'
    return $Version -match $pattern
}

function Get-NextAppVersion {
    param(
        [string]$CurrentVersion
    )

    if ($CurrentVersion -notmatch '^(\d+)\.(\d+)\.(\d+)$') {
        throw "APP_VERSION must be numeric major.minor.patch for auto-increment (example: 2.3.9). Found: $CurrentVersion"
    }

    [int]$major = [int]$Matches[1]
    [int]$minor = [int]$Matches[2]
    [int]$patch = [int]$Matches[3]

    $patch++
    if ($patch -ge 10) {
        $patch = 0
        $minor++
    }
    if ($minor -ge 10) {
        $minor = 0
        $major++
    }

    return "$major.$minor.$patch"
}

$constantsPath = Join-Path $projectRoot "core\constants.py"
if (-not (Test-Path $constantsPath)) {
    throw "Missing constants file: $constantsPath"
}

$constantsContent = Get-Content -Path $constantsPath -Raw
$versionMatch = [regex]::Match($constantsContent, '(?m)^APP_VERSION\s*=\s*"([^"]+)"')
if (-not $versionMatch.Success) {
    throw "Could not find APP_VERSION in $constantsPath"
}
$currentVersion = $versionMatch.Groups[1].Value

if ([string]::IsNullOrWhiteSpace($AppVersion)) {
    $AppVersion = Get-NextAppVersion -CurrentVersion $currentVersion
    Write-Host "Auto-bumped app version: $currentVersion -> $AppVersion"
} else {
    $AppVersion = $AppVersion.Trim()
    if (-not (Test-AppVersionFormat -Version $AppVersion)) {
        throw "Invalid -AppVersion format. Use values like 2.4.0, 2.4.0-beta1, or 2.4.0+build5."
    }
}

if ([string]::IsNullOrWhiteSpace($InstallerOutputDir)) {
    $InstallerOutputDir = "installers"
} else {
    $InstallerOutputDir = $InstallerOutputDir.Trim()
}

$updatedConstantsContent = [regex]::Replace(
    $constantsContent,
    '(?m)^APP_VERSION\s*=\s*"[^"]+"',
    "APP_VERSION = `"$AppVersion`"",
    1
)
if ($updatedConstantsContent -eq $constantsContent) {
    throw "Could not update APP_VERSION in $constantsPath"
}
Set-Content -Path $constantsPath -Value $updatedConstantsContent -Encoding UTF8
Write-Host "Using app version: $AppVersion"

function Get-AvailableDriveLetter {
    $candidates = @('Z', 'Y', 'X', 'W', 'V', 'U', 'T', 'S', 'R')
    foreach ($letter in $candidates) {
        if (-not (Test-Path ("$letter`:"))) {
            return $letter
        }
    }
    throw "No available drive letter found for temporary mapping."
}

function Update-UpdateManifest {
    param(
        [string]$ProjectRoot,
        [string]$Version,
        [string]$InstallerOutputDir
    )

    function Get-ResolvedDownloadUrl {
        param(
            [string]$ExistingUrl,
            [System.IO.FileInfo]$InstallerFile,
            [string]$NewVersion
        )

        $defaultUrl = $InstallerFile.Name
        if ([string]::IsNullOrWhiteSpace($ExistingUrl)) {
            return $defaultUrl
        }

        $trimmed = $ExistingUrl.Trim()
        if ($trimmed -match '^(?i)file:/') {
            return $defaultUrl
        }

        $installerNameMatch = [regex]::Match($trimmed, 'GORO-Setup-[^/?#\\]+\.exe')
        if ($installerNameMatch.Success) {
            $updated = $trimmed.Substring(0, $installerNameMatch.Index) + $InstallerFile.Name + $trimmed.Substring($installerNameMatch.Index + $installerNameMatch.Length)
            # Also update the GitHub Release tag version (e.g. releases/download/v2.5.1/ -> v2.5.2/)
            $updated = [regex]::Replace($updated, '(?<=/releases/download/)v[^/]+(?=/)', "v$NewVersion")
            return $updated
        }

        return $trimmed
    }

    if ([System.IO.Path]::IsPathRooted($InstallerOutputDir)) {
        $installersDir = $InstallerOutputDir
    } else {
        $installersDir = Join-Path $ProjectRoot $InstallerOutputDir
    }

    if (-not (Test-Path $installersDir)) {
        Write-Warning "Installer output directory not found at $installersDir. Skipping updates.json update."
        return
    }

    $installer = Get-ChildItem -Path $installersDir -File -Filter "GORO-Setup-$Version-*.exe" |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $installer) {
        Write-Warning "Could not find installer for version $Version in $installersDir. Skipping updates.json update."
        return
    }

    $manifestPaths = @(
        (Join-Path $ProjectRoot "data\updates.json"),
        (Join-Path $ProjectRoot "updates.json")
    ) | Select-Object -Unique

    foreach ($manifestPath in $manifestPaths) {
        $manifestObj = $null
        if (Test-Path $manifestPath) {
            try {
                $manifestObj = Get-Content -Path $manifestPath -Raw | ConvertFrom-Json
            } catch {
                Write-Warning "Existing manifest is not valid JSON at $manifestPath. A new manifest object will be written."
            }
        }
        if (-not $manifestObj) {
            $manifestObj = [pscustomobject]@{}
        }

        $existingDownloadUrl = ""
        if ($manifestObj.PSObject.Properties.Name -contains "download_url") {
            $existingDownloadUrl = [string]$manifestObj.download_url
        }

        $existingReleaseNotes = ""
        if ($manifestObj.PSObject.Properties.Name -contains "release_notes") {
            $existingReleaseNotes = [string]$manifestObj.release_notes
        }

        $manifestObj | Add-Member -NotePropertyName "latest_version" -NotePropertyValue $Version -Force
        $manifestObj | Add-Member -NotePropertyName "download_url" -NotePropertyValue (Get-ResolvedDownloadUrl -ExistingUrl $existingDownloadUrl -InstallerFile $installer -NewVersion $Version) -Force
        $manifestObj | Add-Member -NotePropertyName "release_notes" -NotePropertyValue $existingReleaseNotes -Force

        $manifestDir = Split-Path -Parent $manifestPath
        if (-not [string]::IsNullOrWhiteSpace($manifestDir) -and -not (Test-Path $manifestDir)) {
            New-Item -Path $manifestDir -ItemType Directory -Force | Out-Null
        }

        $manifestObj | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8
        Write-Host "Updated manifest: $manifestPath"
    }
}

# ---------------------------------------------------------------------------
# GitHub Release helpers
# ---------------------------------------------------------------------------

function Resolve-GitPath {
    $git = Get-Command git -ErrorAction SilentlyContinue
    if ($git) { return $git.Source }
    $candidates = @(
        'C:\Program Files\Git\cmd\git.exe',
        'C:\Program Files\Git\bin\git.exe',
        'C:\Program Files (x86)\Git\cmd\git.exe'
    )
    return $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}

function Publish-GitHubRelease {
    param(
        [string]$Token,
        [string]$Owner,
        [string]$Repo,
        [string]$Version,
        [string]$Notes,
        [string]$InstallerPath
    )

    $tag      = "v$Version"
    $headers  = @{
        Authorization          = "Bearer $Token"
        Accept                 = 'application/vnd.github+json'
        'X-GitHub-Api-Version' = '2022-11-28'
    }

    Write-Host "[GitHub] Creating release $tag..."
    $body = @{ tag_name = $tag; name = "GORO $tag"; body = $Notes; draft = $false; prerelease = $false } | ConvertTo-Json
    try {
        $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/releases" `
            -Method Post -Headers $headers -Body $body -ContentType 'application/json'
    } catch {
        Write-Warning "GitHub release creation failed: $_"
        return $null
    }

    Write-Host "[GitHub] Uploading installer asset..."
    $uploadUrl  = ($release.upload_url -replace '\{.*\}', '')
    $fileName   = Split-Path $InstallerPath -Leaf
    $uploadHdrs = $headers.Clone()
    $uploadHdrs['Accept'] = 'application/vnd.github+json'
    try {
        Invoke-RestMethod -Uri "${uploadUrl}?name=$fileName" `
            -Method Post -Headers $uploadHdrs `
            -InFile $InstallerPath -ContentType 'application/octet-stream' | Out-Null
    } catch {
        Write-Warning "Asset upload failed: $_"
        Write-Warning "Release was created at $($release.html_url) — upload the installer manually."
        return $release
    }

    Write-Host "[GitHub] Release published: $($release.html_url)"
    return $release
}

function Push-ReleaseToGit {
    param(
        [string]$ProjectRoot,
        [string]$Version
    )

    $gitPath = Resolve-GitPath
    if (-not $gitPath) {
        Write-Warning 'git not found — skipping commit and push. Push manually.'
        return
    }

    Push-Location $ProjectRoot
    try {
        & $gitPath add core\constants.py updates.json data\updates.json 2>&1 | Out-Null
        $commitOut = & $gitPath commit -m "release: v$Version" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning 'Nothing to commit or commit failed. Skipping push.'
            return
        }
        Write-Host "[git] $commitOut"
        & $gitPath push 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[git] Pushed release commit for v$Version to GitHub."
        } else {
            Write-Warning 'git push failed. Push manually: git push'
        }
    } finally {
        Pop-Location
    }
}

# ---------------------------------------------------------------------------

$mappedDrive = Get-AvailableDriveLetter
$mappedDriveToken = "$mappedDrive`:"
$mappedBasePath = "$mappedDriveToken\"
$mappedPython = "$mappedBasePath.venv\Scripts\python.exe"
$mappedSpec = "${mappedBasePath}goro.spec"

subst $mappedDriveToken "$projectRoot"

try {
    if (-not (Test-Path $mappedPython)) {
        throw ".venv Python not found at $mappedPython"
    }

    Write-Host "[1/4] Installing/Updating PyInstaller..."
    & $mappedPython -m pip install --upgrade pip pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install/update PyInstaller. Exit code: $LASTEXITCODE"
    }

    Write-Host "[2/4] Cleaning old build artifacts..."
    Write-Host "[2a/4] Setting up Poppler for PDF support..."
    $popplerSetupScript = Join-Path $projectRoot "tools\setup_poppler.ps1"
    if (Test-Path $popplerSetupScript) {
        & $popplerSetupScript -OutputPath (Join-Path $projectRoot "tools\poppler-windows")
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Poppler setup failed, but continuing. PDF import may not work without bundled Poppler."
        }
    } else {
        Write-Warning "Poppler setup script not found at $popplerSetupScript"
    }

    Write-Host "[2b/4] Setting up Tesseract for OCR support..."
    $tesseractSetupScript = Join-Path $projectRoot "tools\setup_tesseract.ps1"
    if (Test-Path $tesseractSetupScript) {
        & $tesseractSetupScript -OutputPath (Join-Path $projectRoot "tools\installers")
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Tesseract installer download failed, but continuing. The final installer will not be able to provision OCR automatically."
        }
    } else {
        Write-Warning "Tesseract setup script not found at $tesseractSetupScript"
    }

    $buildPath = Join-Path $projectRoot "build"
    $distPath = Join-Path $projectRoot "dist"
    if (Test-Path $buildPath) { Remove-Item $buildPath -Recurse -Force }
    if (Test-Path $distPath) { Remove-Item $distPath -Recurse -Force }

    Write-Host "[3/4] Building app with PyInstaller spec..."
    & $mappedPython -m PyInstaller --noconfirm --clean $mappedSpec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE"
    }

    Write-Host "[3a/4] Bundling Poppler with application..."
    $popplerSource = Join-Path $projectRoot "tools\poppler-windows"
    $popplerDest = Join-Path $projectRoot "dist\GORO\poppler"
    if (Test-Path $popplerSource) {
        Write-Host "Copying Poppler from $popplerSource to $popplerDest..."
        New-Item -Path $popplerDest -ItemType Directory -Force | Out-Null
        Copy-Item -Path (Join-Path $popplerSource "*") -Destination $popplerDest -Recurse -Force
        Write-Host "Poppler bundled successfully"
    } else {
        Write-Warning "Poppler source directory not found at $popplerSource. PDF import may require manual Poppler installation."
    }

    if ($SkipInstaller) {
        Write-Host "Installer generation skipped. App output: dist\GORO\GORO.exe"
        exit 0
    }

    Write-Host "[4/4] Building installer with Inno Setup (if available)..."
    $issPath = Join-Path $projectRoot "installer.iss"
    if (-not (Test-Path $issPath)) {
        throw "Missing installer script: $issPath"
    }

    $iscc = Get-Command iscc -ErrorAction SilentlyContinue
    if (-not $iscc) {
        $isccCandidates = @(
            "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            "C:\Program Files\Inno Setup 6\ISCC.exe",
            (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe")
        )
        $isccPath = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
        if (-not $isccPath) {
            Write-Warning "Inno Setup compiler (ISCC.exe) not found."
            Write-Host "Install Inno Setup 6 from https://jrsoftware.org/isinfo.php"
            Write-Host "Then run ISCC manually against: `"$issPath`""
            Write-Host "PyInstaller output is ready at: dist\GORO\GORO.exe"
            exit 0
        }
    } else {
        $isccPath = $iscc.Source
    }

    & $isccPath "/DMyAppVersion=$AppVersion" "/DInstallerOutputDir=$InstallerOutputDir" $issPath
    if ($LASTEXITCODE -ne 0) {
        throw "Inno Setup build failed with exit code $LASTEXITCODE"
    }

    Update-UpdateManifest -ProjectRoot $projectRoot -Version $AppVersion -InstallerOutputDir $InstallerOutputDir

    # --- GitHub Release ---
    if (-not $SkipGitHubRelease) {
        $token = $GitHubToken
        if ([string]::IsNullOrWhiteSpace($token)) { $token = $env:GITHUB_TOKEN }

        if ([string]::IsNullOrWhiteSpace($token)) {
            Write-Warning ''
            Write-Warning 'No GitHub token found — skipping automatic GitHub Release.'
            Write-Warning 'To enable: set $env:GITHUB_TOKEN = "ghp_..." or pass -GitHubToken "ghp_..."'
            Write-Warning 'Then manually create a release at https://github.com/grego-hash/GORO/releases'
            Write-Warning 'and upload the installer from the installers\ folder.'
        } else {
            # Find the installer so we can upload it
            $installersDir = if ([System.IO.Path]::IsPathRooted($InstallerOutputDir)) { $InstallerOutputDir } else { Join-Path $projectRoot $InstallerOutputDir }
            $installer = Get-ChildItem -Path $installersDir -File -Filter "GORO-Setup-$AppVersion-*.exe" |
                Sort-Object LastWriteTime -Descending | Select-Object -First 1

            if (-not $installer) {
                Write-Warning "Installer not found in $installersDir — skipping GitHub Release."
            } else {
                $notes = if ($ReleaseNotes) { $ReleaseNotes } else { '' }
                Publish-GitHubRelease -Token $token -Owner 'grego-hash' -Repo 'GORO' `
                    -Version $AppVersion -Notes $notes -InstallerPath $installer.FullName
            }
        }
    }

    # --- Commit & push updates.json + version bump ---
    Push-ReleaseToGit -ProjectRoot $projectRoot -Version $AppVersion

    Write-Host "Build complete. Installer output is in $InstallerOutputDir (version $AppVersion)."
}
finally {
    subst $mappedDriveToken /d | Out-Null
}
