# TechDisposal Windows Environment Setup Script
# This script sets up Windows-specific virtual environment for TechDisposal EXE build

Write-Host "================================================================" -ForegroundColor Green
Write-Host "  TechDisposal Windows Environment Setup" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[Error] Python not installed" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Python confirmed: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[Error] Error checking Python: $_" -ForegroundColor Red
    exit 1
}

# Check/Create venv_windows
if (Test-Path "venv_windows") {
    Write-Host "Using existing venv_windows..." -ForegroundColor Yellow
} else {
    Write-Host "Creating venv_windows..." -ForegroundColor Blue
    try {
        python -m venv venv_windows
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[Error] Failed to create virtual environment" -ForegroundColor Red
            exit 1
        }
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    }
    catch {
        Write-Host "[Error] Error creating virtual environment: $_" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Blue
try {
    & "venv_windows\Scripts\Activate.ps1"
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
}
catch {
    Write-Host "[Error] Failed to activate virtual environment: $_" -ForegroundColor Red
    Write-Host "ExecutionPolicy may need to be set." -ForegroundColor Yellow
    Write-Host "Run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Blue
python -m pip install --upgrade pip

# Install TechDisposal dependencies
Write-Host "Installing TechDisposal dependencies..." -ForegroundColor Blue
pip install PyQt6 python-docx pyinstaller

# Verify installations
Write-Host "Verifying installations..." -ForegroundColor Blue
python -c "import PyQt6; print('✓ PyQt6 OK')"
python -c "import docx; print('✓ python-docx OK')"
python -c "import PyInstaller; print('✓ PyInstaller OK')"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: .\dist\TechDisposal.build.ps1" -ForegroundColor Cyan
Write-Host "2. Test the generated EXE" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to exit"