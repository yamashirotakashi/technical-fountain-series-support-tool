# Install PyInstaller for native Windows Python

Write-Host "=== Installing PyInstaller (Native) ===" -ForegroundColor Cyan
Write-Host "Target: System Python 3.13.5" -ForegroundColor Yellow
Write-Host ""

# Install PyInstaller
Write-Host "Installing PyInstaller..." -ForegroundColor Green
python -m pip install --user pyinstaller

# Verify installation
Write-Host "`nVerifying PyInstaller installation..." -ForegroundColor Yellow
python -m PyInstaller --version

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")