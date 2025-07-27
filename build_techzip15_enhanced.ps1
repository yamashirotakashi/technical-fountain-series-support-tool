# Build TECHZIP1.5.exe with enhanced configuration support

Set-Location $PSScriptRoot

Write-Host "=== TECHZIP1.5 EXE Builder (Enhanced) ===" -ForegroundColor Cyan
Write-Host "Building with development settings inheritance" -ForegroundColor Yellow
Write-Host ""

# Clean only TECHZIP1.5 related builds
Write-Host "Cleaning TECHZIP1.5 related builds..." -ForegroundColor Green
if (Test-Path "dist\TECHZIP1.5") {
    Remove-Item -Recurse -Force "dist\TECHZIP1.5"
}
if (Test-Path "dist\TECHZIP1.5.exe") {
    Remove-Item -Force "dist\TECHZIP1.5.exe"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Prepare development settings for bundling
Write-Host "`nPreparing development settings..." -ForegroundColor Yellow

# Create .env.template from current .env if exists
if (Test-Path ".env") {
    Write-Host "Creating .env.template from current .env..." -ForegroundColor Green
    Copy-Item -Path ".env" -Destination ".env.template" -Force
} else {
    Write-Host "No .env file found, using default template" -ForegroundColor Yellow
}

# Check current settings
Write-Host "`nCurrent settings check:" -ForegroundColor Cyan
if (Test-Path "config\settings.json") {
    Write-Host "[OK] config\settings.json exists" -ForegroundColor Green
}
if (Test-Path "config\gmail_oauth_credentials.json") {
    Write-Host "[OK] config\gmail_oauth_credentials.json exists" -ForegroundColor Green
}
if (Test-Path ".env") {
    Write-Host "[OK] .env file exists (will be used as template)" -ForegroundColor Green
}

# Build the executable
Write-Host "`nBuilding executable with enhanced configuration..." -ForegroundColor Green
python -m PyInstaller techzip15_improved.spec

# Check if build was successful
if (Test-Path "dist\TECHZIP1.5.exe") {
    Write-Host "`n✓ Build successful!" -ForegroundColor Green
    Write-Host "Executable location: $PSScriptRoot\dist\TECHZIP1.5.exe" -ForegroundColor Yellow
    
    # Get file size
    $fileSize = (Get-Item "dist\TECHZIP1.5.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    Write-Host "`nEnhanced features:" -ForegroundColor Yellow
    Write-Host "- Development settings are inherited as defaults" -ForegroundColor White
    Write-Host "- Word2XHTML5 settings added to configuration dialog" -ForegroundColor White
    Write-Host "- All authentication methods configurable via GUI" -ForegroundColor White
    Write-Host "- First run automatically copies development settings" -ForegroundColor White
} else {
    Write-Host "`n✗ Build failed!" -ForegroundColor Red
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")