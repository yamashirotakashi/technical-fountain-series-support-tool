# Windows Environment Execution Script - Overflow Checker Standalone
# PowerShell 5.1+ Compatible

param(
    [switch]$Debug = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== Overflow Checker Windows Execution ===" -ForegroundColor Cyan

# Check virtual environment
function Test-VirtualEnvironment {
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "Virtual environment not found" -ForegroundColor Red
        Write-Host "Please run setup_windows.ps1 first" -ForegroundColor Yellow
        return $false
    }
    return $true
}

# Set environment variables
function Set-EnvironmentVariables {
    # Tesseract OCR path setup
    $tesseractPaths = @(
        "${env:ProgramFiles}\Tesseract-OCR\tesseract.exe",
        "${env:ProgramFiles(x86)}\Tesseract-OCR\tesseract.exe",
        "C:\Tesseract-OCR\tesseract.exe"
    )
    
    foreach ($path in $tesseractPaths) {
        if (Test-Path $path) {
            $env:TESSERACT_CMD = $path
            if ($Verbose) {
                Write-Host "Tesseract path set: $path" -ForegroundColor Green
            }
            break
        }
    }
    
    # Other environment variables
    $env:PYTHONPATH = (Get-Location).Path
    $env:OVERFLOW_CHECKER_HOME = (Get-Location).Path
    
    if ($Debug) {
        $env:OVERFLOW_CHECKER_DEBUG = "1"
        Write-Host "Debug mode enabled" -ForegroundColor Yellow
    }
}

# Ensure log directory
function Ensure-LogDirectory {
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }
}

# Start application
function Start-Application {
    Write-Host "Starting Overflow Checker..." -ForegroundColor Yellow
    
    # Pre-execution check
    if (-not (Test-Path "run_ultimate.py")) {
        Write-Host "run_ultimate.py not found" -ForegroundColor Red
        exit 1
    }
    
    try {
        # Run application in virtual environment
        if ($Debug) {
            & .\venv\Scripts\python.exe run_ultimate.py --debug
        } else {
            & .\venv\Scripts\python.exe run_ultimate.py
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Application execution error (exit code: $LASTEXITCODE)" -ForegroundColor Red
        } else {
            Write-Host "Application completed successfully" -ForegroundColor Green
        }
        
    } catch {
        Write-Host "Execution error: $($_.Exception.Message)" -ForegroundColor Red
        if ($Debug) {
            Write-Host "Details: $($_.Exception)" -ForegroundColor Red
        }
    }
}

# Main execution
try {
    # Check virtual environment
    if (-not (Test-VirtualEnvironment)) {
        exit 1
    }
    
    # Set environment variables
    Set-EnvironmentVariables
    
    # Ensure log directory
    Ensure-LogDirectory
    
    # Start application
    Start-Application
    
} catch {
    Write-Host "Execution error: $($_.Exception.Message)" -ForegroundColor Red
    if ($Debug) {
        Write-Host "Stack trace: $($_.Exception.StackTrace)" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""
Write-Host "Execution completed" -ForegroundColor Cyan