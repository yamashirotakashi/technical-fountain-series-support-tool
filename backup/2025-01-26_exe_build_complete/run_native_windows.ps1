# Windows Native Run Script for TechZip (No Virtual Environment)

# Move to project directory  
Set-Location $PSScriptRoot

Write-Host "=== TechZip Native Windows Launcher ===" -ForegroundColor Cyan
Write-Host "Using system Python (no virtual environment)" -ForegroundColor Yellow
Write-Host ""

# Check Python version
Write-Host "Python Version:" -ForegroundColor Green
python --version

# Install dependencies to user directory
Write-Host "`nInstalling dependencies to user directory..." -ForegroundColor Yellow
python -m pip install --user --upgrade pip
python -m pip install --user -r requirements.txt

# Launch application
Write-Host "`nLaunching TechZip..." -ForegroundColor Green
python main.py

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")