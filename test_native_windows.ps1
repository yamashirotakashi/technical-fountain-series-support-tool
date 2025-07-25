# Windows Native Test Script for TechZip

# Move to project directory
Set-Location $PSScriptRoot

Write-Host "=== TechZip Windows Native Test ===" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Python Version:" -ForegroundColor Yellow
python --version

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv_windows\Scripts\Activate.ps1"

# Install/Update dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Test import
Write-Host "`nTesting imports..." -ForegroundColor Yellow
python -c @"
try:
    import PyQt5
    print('✓ PyQt5 imported successfully')
    import requests
    print('✓ requests imported successfully')
    import google.auth
    print('✓ google.auth imported successfully')
    import docx
    print('✓ python-docx imported successfully')
    import dotenv
    print('✓ python-dotenv imported successfully')
    print('\nAll imports successful!')
except ImportError as e:
    print(f'✗ Import error: {e}')
"@

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")