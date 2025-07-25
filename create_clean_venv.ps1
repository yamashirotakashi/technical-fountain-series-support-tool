# Create clean virtual environment for TechZip

Set-Location $PSScriptRoot

Write-Host "=== Creating Clean Virtual Environment for TechZip ===" -ForegroundColor Cyan
Write-Host ""

# Remove existing virtual environment
if (Test-Path "venv_clean") {
    Write-Host "Removing existing venv_clean..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv_clean"
}

# Create new virtual environment
Write-Host "Creating new virtual environment..." -ForegroundColor Green
python -m venv venv_clean

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv_clean\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install only required dependencies
Write-Host "`nInstalling dependencies from requirements.txt..." -ForegroundColor Green
python -m pip install -r requirements.txt

# Install PyInstaller
Write-Host "`nInstalling PyInstaller..." -ForegroundColor Green
python -m pip install pyinstaller

# Verify installation
Write-Host "`n=== Verifying Installation ===" -ForegroundColor Cyan
python -c @"
import sys
print(f'Python: {sys.version}')
print(f'Executable: {sys.executable}')
print('\nChecking imports:')
try:
    import PyQt5
    print('✓ PyQt5')
    import requests
    print('✓ requests')
    from google.oauth2 import service_account
    print('✓ google.auth')
    import docx
    print('✓ python-docx')
    import dotenv
    print('✓ python-dotenv')
    print('\nAll dependencies installed successfully!')
except ImportError as e:
    print(f'✗ Error: {e}')
"@

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")