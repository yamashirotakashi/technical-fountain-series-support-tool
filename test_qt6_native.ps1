# Test Qt6 version in native Windows

Set-Location $PSScriptRoot

Write-Host "=== Testing TechZip Qt6 Version ===" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Python Version:" -ForegroundColor Yellow
python --version

# Test imports
Write-Host "`nTesting Qt6 imports..." -ForegroundColor Yellow
python -c @"
try:
    import PyQt6
    print('✓ PyQt6 imported successfully')
    from PyQt6.QtWidgets import QApplication
    print('✓ QApplication imported successfully')
    from PyQt6.QtGui import QAction
    print('✓ QAction imported successfully')
    print('\nQt6 setup is ready!')
except ImportError as e:
    print(f'✗ Import error: {e}')
"@

# Launch the application
Write-Host "`nLaunching TechZip with Qt6..." -ForegroundColor Green
python main_clean.py

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")