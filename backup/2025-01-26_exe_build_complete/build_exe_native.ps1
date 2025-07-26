# Build executable for TechZip using native Windows Python

Set-Location $PSScriptRoot

Write-Host "=== TechZip EXE Builder (Native) ===" -ForegroundColor Cyan
Write-Host "Using system Python 3.13.5" -ForegroundColor Yellow
Write-Host ""

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Green
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "*.spec") {
    Remove-Item -Force "*.spec"
}

# Create spec file with all necessary configurations
Write-Host "`nGenerating spec file..." -ForegroundColor Yellow
$specContent = @'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_clean.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'requests',
        'google.oauth2',
        'google.auth',
        'googleapiclient',
        'googleapiclient.discovery',
        'googleapiclient.errors',
        'googleapiclient.http',
        'httplib2',
        'docx',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PySide6'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TechZip',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'@

$specContent | Out-File -FilePath "techzip.spec" -Encoding utf8

# Build the executable
Write-Host "`nBuilding executable..." -ForegroundColor Green
python -m PyInstaller techzip.spec

# Check if build was successful
if (Test-Path "dist\TechZip.exe") {
    Write-Host "`n✓ Build successful!" -ForegroundColor Green
    Write-Host "Executable location: $PSScriptRoot\dist\TechZip.exe" -ForegroundColor Yellow
    
    # Get file size
    $fileSize = (Get-Item "dist\TechZip.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
} else {
    Write-Host "`n✗ Build failed!" -ForegroundColor Red
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")