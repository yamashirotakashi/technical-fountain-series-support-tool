# Convert PyQt5 to PyQt6

Write-Host "=== Converting PyQt5 to PyQt6 ===" -ForegroundColor Cyan

# Function to update Python files
function Update-PythonFile {
    param($FilePath)
    
    Write-Host "Updating: $FilePath" -ForegroundColor Yellow
    
    $content = Get-Content $FilePath -Raw
    
    # Basic replacements
    $content = $content -replace 'from PyQt5', 'from PyQt6'
    $content = $content -replace 'import PyQt5', 'import PyQt6'
    
    # Qt.AlignCenter changes in Qt6
    $content = $content -replace 'Qt\.AlignCenter', 'Qt.AlignmentFlag.AlignCenter'
    $content = $content -replace 'Qt\.AlignLeft', 'Qt.AlignmentFlag.AlignLeft'
    $content = $content -replace 'Qt\.AlignRight', 'Qt.AlignmentFlag.AlignRight'
    $content = $content -replace 'Qt\.AlignTop', 'Qt.AlignmentFlag.AlignTop'
    $content = $content -replace 'Qt\.AlignBottom', 'Qt.AlignmentFlag.AlignBottom'
    $content = $content -replace 'Qt\.AlignVCenter', 'Qt.AlignmentFlag.AlignVCenter'
    $content = $content -replace 'Qt\.AlignHCenter', 'Qt.AlignmentFlag.AlignHCenter'
    
    # WindowType changes
    $content = $content -replace 'Qt\.WindowStaysOnTopHint', 'Qt.WindowType.WindowStaysOnTopHint'
    $content = $content -replace 'Qt\.FramelessWindowHint', 'Qt.WindowType.FramelessWindowHint'
    
    # Other Qt enums
    $content = $content -replace 'Qt\.Checked', 'Qt.CheckState.Checked'
    $content = $content -replace 'Qt\.Unchecked', 'Qt.CheckState.Unchecked'
    $content = $content -replace 'Qt\.PartiallyChecked', 'Qt.CheckState.PartiallyChecked'
    
    # QAction moved
    $content = $content -replace 'from PyQt6\.QtWidgets import (.*)QAction', 'from PyQt6.QtWidgets import $1'
    $content = $content -replace 'from PyQt6\.QtWidgets import QAction', 'from PyQt6.QtGui import QAction'
    
    # If QAction is in a multi-import, add separate import
    if ($content -match 'from PyQt6\.QtWidgets import.*\bQAction\b') {
        if (-not ($content -match 'from PyQt6\.QtGui import QAction')) {
            $content = $content -replace '(from PyQt6\.QtWidgets import.*)', '$1`nfrom PyQt6.QtGui import QAction'
        }
    }
    
    # Save the file
    Set-Content -Path $FilePath -Value $content -NoNewline
}

# Get all Python files
$pythonFiles = Get-ChildItem -Path . -Recurse -Filter "*.py" | 
    Where-Object { $_.FullName -notmatch "backup_qt5|venv|__pycache__|test_" }

# Update each file
foreach ($file in $pythonFiles) {
    Update-PythonFile -FilePath $file.FullName
}

Write-Host "`n=== Conversion completed ===" -ForegroundColor Green
Write-Host "Please review the changes and test the application" -ForegroundColor Yellow

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")