# Build TECHZIP1.5.exe safely (preserve existing files)

Set-Location $PSScriptRoot

Write-Host "=== TECHZIP1.5 Safe EXE Builder ===" -ForegroundColor Cyan
Write-Host "Building TECHZIP1.5.exe (preserving existing TechZip files)" -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Using system Python (no venv found)" -ForegroundColor Yellow
}

# Install PyInstaller if needed
Write-Host "Checking PyInstaller..." -ForegroundColor Green
python -m pip show pyinstaller >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller
}

# Clean only TECHZIP1.5 related files
Write-Host "Cleaning only TECHZIP1.5 files (preserving others)..." -ForegroundColor Green
if (Test-Path "dist\TECHZIP1.5") {
    Remove-Item -Recurse -Force "dist\TECHZIP1.5"
}
if (Test-Path "dist\TECHZIP1.5.exe") {
    Remove-Item -Force "dist\TECHZIP1.5.exe"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Use existing techzip_windows.spec (already configured for TECHZIP1.5)
Write-Host "Using existing techzip_windows.spec..." -ForegroundColor Green

# Build the executable
Write-Host "`nBuilding TECHZIP1.5.exe..." -ForegroundColor Green
python -m PyInstaller techzip_windows.spec --clean --noconfirm

# Check if build was successful
if (Test-Path "dist\TECHZIP1.5\TECHZIP1.5.exe") {
    Write-Host "`n✓ Build successful!" -ForegroundColor Green
    Write-Host "Executable location: $PSScriptRoot\dist\TECHZIP1.5\TECHZIP1.5.exe" -ForegroundColor Yellow
    
    # Get file size
    $fileSize = (Get-Item "dist\TECHZIP1.5\TECHZIP1.5.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    # Show existing files in dist
    Write-Host "`nFiles in dist folder:" -ForegroundColor Cyan
    Get-ChildItem "dist" | Format-Table Name, Length, LastWriteTime
    
} else {
    Write-Host "`n✗ Build failed!" -ForegroundColor Red
    Write-Host "Checking what was created..." -ForegroundColor Yellow
    if (Test-Path "dist") {
        Get-ChildItem "dist" -Recurse
    }
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")