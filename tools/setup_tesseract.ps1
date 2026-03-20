param(
    [string]$OutputPath = (Join-Path $PSScriptRoot "installers")
)

$ErrorActionPreference = "Stop"

$TesseractVersion = "5.5.0"
$InstallerBuild = "20241111"
$InstallerName = "tesseract-ocr-w64-setup-$TesseractVersion.$InstallerBuild.exe"
$TesseractUrl = "https://github.com/tesseract-ocr/tesseract/releases/download/$TesseractVersion/$InstallerName"
$InstallerPath = Join-Path $OutputPath $InstallerName

Write-Host "Downloading Tesseract OCR installer..."
Write-Host "Target directory: $OutputPath"

if (Test-Path $InstallerPath) {
    Write-Host "Tesseract installer already present at $InstallerPath. Skipping download."
    exit 0
}

New-Item -Path $OutputPath -ItemType Directory -Force | Out-Null

try {
    Write-Host "Downloading Tesseract OCR $TesseractVersion..."
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $TesseractUrl -OutFile $InstallerPath -UseBasicParsing
    Write-Host "Tesseract installer downloaded successfully."
    Write-Host "Tesseract installer cached at $InstallerPath"
}
catch {
    Write-Error "Failed to setup Tesseract: $_"
    exit 1
}
