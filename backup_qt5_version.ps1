# Backup current Qt5 implementation

Write-Host "=== Backing up Qt5 version ===" -ForegroundColor Cyan

# Create backup directory
$backupDir = "backup_qt5_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "Creating backup directory: $backupDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Copy important files
Write-Host "Copying files..." -ForegroundColor Green
Copy-Item -Path "*.py" -Destination $backupDir -Force
Copy-Item -Path "gui" -Destination $backupDir -Recurse -Force
Copy-Item -Path "core" -Destination $backupDir -Recurse -Force
Copy-Item -Path "utils" -Destination $backupDir -Recurse -Force
Copy-Item -Path "requirements.txt" -Destination $backupDir -Force

Write-Host "Backup completed to: $backupDir" -ForegroundColor Green
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")