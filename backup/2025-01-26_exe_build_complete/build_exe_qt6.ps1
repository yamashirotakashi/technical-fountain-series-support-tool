# Qt6 EXE Build Script
# Windows PowerShell

Write-Host "TechZip Qt6 EXE Build Script" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Python executable check
$pythonPaths = @(
    "python",
    "py",
    "C:\Python313\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "C:\Users\tky99\AppData\Local\Programs\Python\Python313\python.exe",
    "C:\Users\tky99\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\tky99\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Users\tky99\AppData\Local\Programs\Python\Python310\python.exe",
    "C:\Program Files\Python313\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe",
    "C:\Program Files\Python310\python.exe"
)

$pythonPath = $null
foreach ($path in $pythonPaths) {
    try {
        $testPath = if ($path -match "^[A-Z]:") { $path } else { (Get-Command $path -ErrorAction SilentlyContinue).Path }
        if ($testPath -and (Test-Path $testPath)) {
            $version = & $testPath --version 2>&1
            if ($version -match "Python 3\.(1[0-3]|[89])") {
                $pythonPath = $testPath
                Write-Host "Found Python: $pythonPath ($version)" -ForegroundColor Green
                break
            }
        }
    } catch {
        # Ignore errors and try next
    }
}

if (-not $pythonPath) {
    Write-Host "Error: Python 3.8+ not found" -ForegroundColor Red
    Write-Host "Please install Python" -ForegroundColor Yellow
    pause
    exit 1
}

# PyInstaller check
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
& $pythonPath -m pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    & $pythonPath -m pip install pyinstaller
}

# PyQt6 check
Write-Host "Checking PyQt6..." -ForegroundColor Yellow
& $pythonPath -c "import PyQt6.QtCore; print(f'PyQt6 version: {PyQt6.QtCore.QT_VERSION_STR}')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: PyQt6 not installed" -ForegroundColor Red
    Write-Host "Please run run_qt6_windows.ps1 first" -ForegroundColor Yellow
    pause
    exit 1
}

# Clean build confirmation
$cleanBuild = Read-Host "Perform clean build? (Y/n)"
if ($cleanBuild -ne 'n') {
    Write-Host "Cleaning build directories..." -ForegroundColor Yellow
    Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Path "*.spec" | Where-Object { $_.Name -ne "techzip_qt6.spec" } | Remove-Item -Force -ErrorAction SilentlyContinue
}

# EXE build execution
Write-Host ""
Write-Host "Starting EXE build..." -ForegroundColor Green

# Use spec file if exists
if (Test-Path "techzip_qt6.spec") {
    Write-Host "Building with techzip_qt6.spec" -ForegroundColor Cyan
    & $pythonPath -m PyInstaller techzip_qt6.spec
} else {
    Write-Host "Creating new exe" -ForegroundColor Cyan
    & $pythonPath -m PyInstaller --onefile --windowed --name TechZip_Qt6 `
        --add-data "config;config" `
        --hidden-import PyQt6.QtCore `
        --hidden-import PyQt6.QtGui `
        --hidden-import PyQt6.QtWidgets `
        --exclude-module PyQt5 `
        --exclude-module matplotlib `
        --exclude-module numpy `
        --exclude-module pandas `
        main_qt6.py
}

# Build result check
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Build successful!" -ForegroundColor Green
    
    if (Test-Path "dist\TechZip_Qt6.exe") {
        $exeInfo = Get-Item "dist\TechZip_Qt6.exe"
        Write-Host "Created exe: $($exeInfo.FullName)" -ForegroundColor Cyan
        Write-Host "File size: $([math]::Round($exeInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
        
        # Copy required files
        Write-Host ""
        Write-Host "Copying required files..." -ForegroundColor Yellow
        
        # Copy config folder
        if (Test-Path "config") {
            Copy-Item -Path "config" -Destination "dist\config" -Recurse -Force
            Write-Host "✓ Copied config folder" -ForegroundColor Green
        }
        
        # Create .env sample file
        if (Test-Path ".env") {
            $envContent = "# Gmail setting`nGMAIL_ADDRESS=your_email@gmail.com`nGMAIL_APP_PASSWORD=your_app_password_here`n`n# GitHub setting (optional)`nGITHUB_TOKEN=your_github_token_here"
            $envContent | Out-File -FilePath "dist\.env.sample" -Encoding UTF8
            Write-Host "✓ Created .env.sample" -ForegroundColor Green
        }
        
        # Create README
        $readmeContent = "# TechZip Qt6 Tool`n`n## How to run`n1. Double-click TechZip_Qt6.exe to start`n2. For first time use, rename .env.sample to .env and enter settings`n`n## Required files`n- TechZip_Qt6.exe (main application)`n- config/ (configuration files)`n- .env (authentication info)`n`n## Troubleshooting`n- If Windows Defender shows warning, select 'More info' then 'Run anyway'`n- If not starting, check logs folder for error logs"
        $readmeContent | Out-File -FilePath "dist\README.txt" -Encoding UTF8
        Write-Host "✓ Created README.txt" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "Distribution ready!" -ForegroundColor Green
        Write-Host "Please distribute files in dist folder." -ForegroundColor Cyan
        
        # Open in explorer
        $openExplorer = Read-Host "Open dist folder? (Y/n)"
        if ($openExplorer -ne 'n') {
            explorer.exe dist
        }
    }
} else {
    Write-Host ""
    Write-Host "Build failed." -ForegroundColor Red
    Write-Host "Please check error logs." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host