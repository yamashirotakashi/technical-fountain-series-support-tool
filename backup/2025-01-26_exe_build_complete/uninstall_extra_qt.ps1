# Uninstall extra Qt bindings to resolve conflicts

Write-Host "=== Uninstalling Extra Qt Bindings ===" -ForegroundColor Cyan
Write-Host "TechZip uses PyQt5, so we'll remove PyQt6 and PySide6" -ForegroundColor Yellow
Write-Host ""

# Uninstall PyQt6
Write-Host "Uninstalling PyQt6..." -ForegroundColor Green
python -m pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6_sip

# Uninstall PySide6
Write-Host "`nUninstalling PySide6..." -ForegroundColor Green
python -m pip uninstall -y PySide6 PySide6_Addons PySide6_Essentials shiboken6

# Verify remaining Qt packages
Write-Host "`n=== Remaining Qt Packages ===" -ForegroundColor Cyan
python -m pip list | findstr /i "qt"

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")