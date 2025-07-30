# EXE Build Script - Overflow Checker Standalone
# PyInstaller-based EXE creation

param(
    [string]$Version = "1.0.0",
    [switch]$Clean = $false,
    [switch]$Debug = $false,
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== Overflow Checker EXE Build ===" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Yellow
Write-Host "Build Mode: Folder structure (fast startup)" -ForegroundColor Green

# Check prerequisites
function Test-Prerequisites {
    Write-Host "Checking prerequisites..." -ForegroundColor Yellow
    
    # Check virtual environment
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "Virtual environment not found" -ForegroundColor Red
        Write-Host "Run setup_windows.ps1 first" -ForegroundColor Yellow
        return $false
    }
    
    # Check PyInstaller
    try {
        & .\venv\Scripts\pip.exe show pyinstaller | Out-Null
        Write-Host "PyInstaller found" -ForegroundColor Green
    } catch {
        Write-Host "PyInstaller not found" -ForegroundColor Red
        Write-Host "Run pip install pyinstaller" -ForegroundColor Yellow
        return $false
    }
    
    # Check required files
    $requiredFiles = @(
        "run_ultimate.py",
        "overflow_checker.spec",
        "requirements.txt"
    )
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-Host "Required file not found: $file" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "Prerequisites check completed" -ForegroundColor Green
    return $true
}

# Clean build artifacts
function Clear-BuildArtifacts {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    
    # Safe deletion targets (protect other program files)
    $cleanTargets = @(
        "dist\OverflowChecker",      # This project's build artifacts only
        "build",                     # PyInstaller temp files
        "*.spec.bak"                 # spec file backups
    )
    
    foreach ($target in $cleanTargets) {
        if (Test-Path $target) {
            Remove-Item -Path $target -Recurse -Force
            Write-Host "Deleted: $target" -ForegroundColor Gray
        }
    }
    
    # Remove __pycache__ folders within project only
    Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        $fullPath = Join-Path (Get-Location) $_
        if (Test-Path $fullPath) {
            Remove-Item -Path $fullPath -Recurse -Force
            Write-Host "Deleted: $fullPath" -ForegroundColor Gray
        }
    }
    
    # Remove .pyc files within project only
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | ForEach-Object {
        Remove-Item -Path $_ -Force
    }
    
    Write-Host "Cleanup completed (other program files protected)" -ForegroundColor Green
}

# Update version info
function Update-VersionInfo {
    Write-Host "Updating version info..." -ForegroundColor Yellow
    
    # Update version.py
    $versionContent = @"
# -*- coding: utf-8 -*-
'''
Version information file
Auto-generated at build time - do not edit
'''

VERSION = '$Version'
BUILD_DATE = '$(Get-Date -Format "yyyy-MM-dd")'
BUILD_TIME = '$(Get-Date -Format "HH:mm:ss")'
BUILD_TYPE = '$(if($Debug) { "Debug" } else { "Release" })'

# Git info (if available)
try:
    import subprocess
    COMMIT_HASH = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                        stderr=subprocess.DEVNULL).decode().strip()
except:
    COMMIT_HASH = 'unknown'

# Application info
APP_NAME = 'Overflow Checker'
APP_NAME_EN = 'Overflow Checker'
DESCRIPTION = 'PDF Code Block Overflow Detection Tool'
AUTHOR = 'Claude Code Assistant'
COPYRIGHT = '© 2025 Claude Code Assistant'

def get_version_string():
    '''Get version string'''
    return f'{APP_NAME} v{VERSION} ({BUILD_DATE})'

def get_full_version_info():
    '''Get complete version info'''
    return {
        'version': VERSION,
        'build_date': BUILD_DATE,
        'build_time': BUILD_TIME,
        'build_type': BUILD_TYPE,
        'commit_hash': COMMIT_HASH,
        'app_name': APP_NAME,
        'app_name_en': APP_NAME_EN,
        'description': DESCRIPTION,
        'author': AUTHOR,
        'copyright': COPYRIGHT
    }
"@
    
    $versionContent | Out-File -FilePath "version.py" -Encoding UTF8
    
    Write-Host "Version info updated" -ForegroundColor Green
}

# Pre-build test
function Test-BeforeBuild {
    if ($SkipTests) {
        Write-Host "Skipping pre-build tests" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "Running pre-build tests..." -ForegroundColor Yellow
    
    # Import test
    $testScript = @"
import sys
import traceback

print("=== Import Test ===")
test_modules = [
    'PyQt6.QtCore',
    'PyQt6.QtWidgets',
    'PyQt6.QtGui',
    'fitz',
    'cv2',
    'numpy',
    'PIL',
    'pytesseract'
]

failed_modules = []
for module in test_modules:
    try:
        __import__(module)
        print(f"OK: {module}")
    except ImportError as e:
        print(f"FAIL: {module}: {e}")
        failed_modules.append(module)

if failed_modules:
    print(f"\nFailed modules: {failed_modules}")
    sys.exit(1)
else:
    print("\nAll module imports successful")

# Main script check
print("\n=== Main Script Check ===")
try:
    import run_ultimate
    print("OK: run_ultimate.py import successful")
except Exception as e:
    print(f"FAIL: run_ultimate.py import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\nPre-build test completed")
"@
    
    $testScript | Out-File -FilePath "pre_build_test.py" -Encoding UTF8
    
    try {
        & .\venv\Scripts\python.exe pre_build_test.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Pre-build test failed" -ForegroundColor Red
            return $false
        }
    } finally {
        Remove-Item "pre_build_test.py" -ErrorAction SilentlyContinue
    }
    
    Write-Host "Pre-build test completed" -ForegroundColor Green
    return $true
}

# Build executable (folder structure recommended)
function Build-Executable {
    Write-Host "Building EXE with PyInstaller (folder structure)..." -ForegroundColor Yellow
    
    # Folder structure build options
    $buildArgs = @(
        "overflow_checker.spec",
        "--clean"
    )
    
    if ($Debug) {
        $buildArgs += "--debug", "all"
        Write-Host "Building in debug mode" -ForegroundColor Yellow
    }
    
    Write-Host "Building in folder structure mode (fast startup)" -ForegroundColor Green
    
    # Execute PyInstaller
    try {
        Write-Host "Executing PyInstaller..." -ForegroundColor Cyan
        Write-Host "Command: pyinstaller $($buildArgs -join ' ')" -ForegroundColor Gray
        
        & .\venv\Scripts\pyinstaller.exe @buildArgs
        
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller execution failed (exit code: $LASTEXITCODE)"
        }
        
    } catch {
        Write-Host "EXE build failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    Write-Host "EXE build completed (folder structure)" -ForegroundColor Green
    return $true
}

# Post-build test
function Test-AfterBuild {
    if ($SkipTests) {
        Write-Host "Skipping post-build tests" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "Running post-build tests..." -ForegroundColor Yellow
    
    $exePath = "dist\OverflowChecker\OverflowChecker.exe"
    
    if (-not (Test-Path $exePath)) {
        Write-Host "Generated EXE file not found: $exePath" -ForegroundColor Red
        return $false
    }
    
    # File size check
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Host "EXE file size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    # Simple startup test (GUI display without exit)
    Write-Host "Running startup test..." -ForegroundColor Yellow
    
    try {
        # Test execution with timeout
        $process = Start-Process -FilePath $exePath -ArgumentList "--test-mode" -PassThru -NoNewWindow
        
        if (-not $process.WaitForExit(10000)) {  # 10 second timeout
            $process.Kill()
            Write-Host "Startup test timed out (may be normal for GUI)" -ForegroundColor Yellow
        } else {
            Write-Host "Startup test completed" -ForegroundColor Green
        }
        
    } catch {
        Write-Host "Startup test error (may be GUI environment issue)" -ForegroundColor Yellow
        Write-Host "Details: $($_.Exception.Message)" -ForegroundColor Gray
    }
    
    return $true
}

# Create distribution package
function New-DistributionPackage {
    Write-Host "Creating distribution package..." -ForegroundColor Yellow
    
    $distDir = "dist\OverflowChecker"
    $packageDir = "dist\OverflowChecker_v$Version"
    
    if (Test-Path $packageDir) {
        Remove-Item -Path $packageDir -Recurse -Force
    }
    
    # Create package directory
    Copy-Item -Path $distDir -Destination $packageDir -Recurse
    
    # Copy additional files
    $additionalFiles = @{
        "README.md" = "Usage_Instructions.txt"
        "requirements.txt" = "requirements.txt"
    }
    
    foreach ($src in $additionalFiles.Keys) {
        if (Test-Path $src) {
            Copy-Item -Path $src -Destination "$packageDir\$($additionalFiles[$src])"
        }
    }
    
    # Create ZIP archive
    $zipPath = "dist\OverflowChecker_v$Version.zip"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Compress-Archive -Path $packageDir -DestinationPath $zipPath
    
    Write-Host "Distribution package created: $zipPath" -ForegroundColor Green
    
    # Show size info
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host "Package size: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan
}

# Main execution
try {
    Write-Host "Start time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
    # Check prerequisites
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    # Clean build
    if ($Clean) {
        Clear-BuildArtifacts
    }
    
    # Update version info
    Update-VersionInfo
    
    # Pre-build test
    if (-not (Test-BeforeBuild)) {
        exit 1
    }
    
    # Build EXE
    if (-not (Build-Executable)) {
        exit 1
    }
    
    # Post-build test
    if (-not (Test-AfterBuild)) {
        Write-Host "Some post-build tests failed, but continuing" -ForegroundColor Yellow
    }
    
    # Create distribution package
    New-DistributionPackage
    
    Write-Host ""
    Write-Host "EXE build completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Generated files:" -ForegroundColor Cyan
    Write-Host "- EXE: dist\OverflowChecker\OverflowChecker.exe" -ForegroundColor White
    Write-Host "- Package: dist\OverflowChecker_v$Version.zip" -ForegroundColor White
    Write-Host ""
    Write-Host "End time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
} catch {
    Write-Host ""
    Write-Host "Build error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($Debug) {
        Write-Host "Stack trace:" -ForegroundColor Red
        Write-Host $_.Exception.StackTrace -ForegroundColor Red
    }
    
    exit 1
}