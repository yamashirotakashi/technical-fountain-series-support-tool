# Properly migrate from PyQt5 to PyQt6

Write-Host "=== Proper Qt5 to Qt6 Migration ===`n" -ForegroundColor Cyan

# Step 1: Fix all encodings first
Write-Host "Step 1: Fixing file encodings..." -ForegroundColor Yellow
& .\fix_all_encodings.ps1

# Step 2: Create backup
Write-Host "`nStep 2: Creating backup..." -ForegroundColor Yellow
$backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Copy-Item -Path "*.py" -Destination $backupDir -Recurse
Copy-Item -Path "gui" -Destination $backupDir -Recurse
Copy-Item -Path "utils" -Destination $backupDir -Recurse
Copy-Item -Path "core" -Destination $backupDir -Recurse
Write-Host "✓ Backup created in $backupDir" -ForegroundColor Green

# Step 3: Update imports in all files
Write-Host "`nStep 3: Updating imports..." -ForegroundColor Yellow

$files = Get-ChildItem -Path . -Include *.py -Recurse | Where-Object { $_.FullName -notmatch 'venv|__pycache__|build|dist|backup' }

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Basic replacements
    $content = $content -replace 'from PyQt5', 'from PyQt6'
    $content = $content -replace 'import PyQt5', 'import PyQt6'
    
    # Qt enum changes
    $content = $content -replace '\.KeepAspectRatio\b', '.AspectRatioMode.KeepAspectRatio'
    $content = $content -replace '\.IgnoreAspectRatio\b', '.AspectRatioMode.IgnoreAspectRatio'
    $content = $content -replace 'Qt\.Horizontal\b', 'Qt.Orientation.Horizontal'
    $content = $content -replace 'Qt\.Vertical\b', 'Qt.Orientation.Vertical'
    $content = $content -replace 'Qt\.AlignCenter\b', 'Qt.AlignmentFlag.AlignCenter'
    $content = $content -replace 'Qt\.AlignLeft\b', 'Qt.AlignmentFlag.AlignLeft'
    $content = $content -replace 'Qt\.AlignRight\b', 'Qt.AlignmentFlag.AlignRight'
    $content = $content -replace 'Qt\.AlignTop\b', 'Qt.AlignmentFlag.AlignTop'
    $content = $content -replace 'Qt\.AlignBottom\b', 'Qt.AlignmentFlag.AlignBottom'
    
    # QAction moved from QtWidgets to QtGui
    if ($content -match 'from PyQt6\.QtWidgets import.*QAction') {
        $content = $content -replace '(from PyQt6\.QtWidgets import .*?)QAction(.*)', '$1$2'
        if ($content -notmatch 'from PyQt6\.QtGui import.*QAction') {
            $content = $content -replace '(from PyQt6\.QtGui import .*)', '$1, QAction'
            if ($content -notmatch 'from PyQt6\.QtGui import') {
                $content = $content -replace '(from PyQt6\.QtCore.*\n)', '$1from PyQt6.QtGui import QAction`n'
            }
        }
    }
    
    # exec_ -> exec
    $content = $content -replace '\.exec_\(\)', '.exec()'
    
    # QMessageBox button changes
    $content = $content -replace 'QMessageBox\.Yes\b', 'QMessageBox.StandardButton.Yes'
    $content = $content -replace 'QMessageBox\.No\b', 'QMessageBox.StandardButton.No'
    $content = $content -replace 'QMessageBox\.Ok\b', 'QMessageBox.StandardButton.Ok'
    $content = $content -replace 'QMessageBox\.Cancel\b', 'QMessageBox.StandardButton.Cancel'
    
    # QTextCursor operations
    $content = $content -replace 'QTextCursor\.End\b', 'QTextCursor.MoveOperation.End'
    
    # QFont weight
    $content = $content -replace 'QFont\.Bold\b', 'QFont.Weight.Bold'
    
    # Remove High DPI attributes (automatic in Qt6)
    $content = $content -replace 'QApplication\.setAttribute\(Qt\.AA_EnableHighDpiScaling.*?\)\s*\n', ''
    $content = $content -replace 'QApplication\.setAttribute\(Qt\.AA_UseHighDpiPixmaps.*?\)\s*\n', ''
    
    [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.UTF8Encoding]::new($true))
    Write-Host "✓ Updated: $($file.Name)" -ForegroundColor Green
}

# Step 4: Update requirements.txt
Write-Host "`nStep 4: Updating requirements.txt..." -ForegroundColor Yellow
$reqContent = Get-Content "requirements.txt" -Raw
$reqContent = $reqContent -replace 'PyQt5==[\d.]+', 'PyQt6==6.7.0'
[System.IO.File]::WriteAllText("requirements.txt", $reqContent, [System.Text.UTF8Encoding]::new($true))
Write-Host "✓ Updated requirements.txt" -ForegroundColor Green

Write-Host "`n=== Migration Complete ===" -ForegroundColor Cyan
Write-Host "1. All files converted to UTF-8" -ForegroundColor Green
Write-Host "2. All imports updated to PyQt6" -ForegroundColor Green
Write-Host "3. Qt6 API changes applied" -ForegroundColor Green
Write-Host "4. requirements.txt updated" -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run: pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host "2. Test: python main.py" -ForegroundColor Cyan

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")