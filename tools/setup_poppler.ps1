# setup_poppler.ps1
# Downloads and extracts Poppler for Windows
# Called as part of the build process

param(
    [string]$OutputPath = (Join-Path $PSScriptRoot "poppler-windows")
)

$ErrorActionPreference = "Stop"

# Poppler Windows releases: https://github.com/oschwartz10612/poppler-windows/releases
# GitHub tags/assets use the form v<version> where version commonly ends with -0.
$PopplerVersion = "24.02.0-0"
$PopplerUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v$PopplerVersion/Release-$PopplerVersion.zip"
$TempZip = Join-Path $env:TEMP "poppler-$PopplerVersion.zip"

function Find-PopplerBinPath {
    param(
        [string]$BasePath
    )

    if (-not (Test-Path $BasePath)) {
        return $null
    }

    $directCandidates = @(
        (Join-Path $BasePath "Library\bin"),
        (Join-Path $BasePath "bin")
    )

    foreach ($candidate in $directCandidates) {
        if (Test-Path (Join-Path $candidate "pdfinfo.exe")) {
            return $candidate
        }
    }

    $pdfInfo = Get-ChildItem -Path $BasePath -Filter "pdfinfo.exe" -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pdfInfo) {
        return $pdfInfo.DirectoryName
    }

    return $null
}

Write-Host "Setting up Poppler for Windows..."
Write-Host "Target directory: $OutputPath"

# Check if already downloaded and valid
if (Test-Path $OutputPath) {
    $existingBin = Find-PopplerBinPath -BasePath $OutputPath
    if ($existingBin) {
        Write-Host "Poppler already present at $OutputPath. Bin path: $existingBin"
        exit 0
    }

    Write-Warning "Existing Poppler folder found but no pdfinfo.exe detected. Re-downloading."
    Remove-Item -Path $OutputPath -Recurse -Force -ErrorAction SilentlyContinue
}

New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null

try {
    Write-Host "Downloading Poppler $PopplerVersion..."
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $PopplerUrl -OutFile $TempZip -UseBasicParsing
    Write-Host "Poppler downloaded successfully."
    
    Write-Host "Extracting Poppler..."
    Expand-Archive -Path $TempZip -DestinationPath $OutputPath -Force
    Write-Host "Poppler extracted to $OutputPath"
    
    # Verify Poppler binary exists (supports nested release folder layouts)
    $BinPath = Find-PopplerBinPath -BasePath $OutputPath
    if ($BinPath) {
        Write-Host "Poppler bin directory verified at $BinPath"
    } else {
        throw "Poppler binary pdfinfo.exe not found under $OutputPath"
    }
}
catch {
    Write-Error "Failed to setup Poppler: $_"
    if (Test-Path $TempZip) { Remove-Item $TempZip -Force }
    exit 1
}
finally {
    if (Test-Path $TempZip) { Remove-Item $TempZip -Force }
}

Write-Host "Poppler setup complete."
