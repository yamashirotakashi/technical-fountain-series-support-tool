# Build TECHZIP1.6.exe using native Windows Python

Set-Location $PSScriptRoot

Write-Host "=== TECHZIP1.6 EXE Builder (Native) ===" -ForegroundColor Cyan
Write-Host "Building TECHZIP1.6.exe with Slack PDF posting functionality" -ForegroundColor Yellow
Write-Host ""

# Clean only TECHZIP1.6 related builds (preserve existing executables)
Write-Host "Cleaning TECHZIP1.6 related builds..." -ForegroundColor Green
if (Test-Path "dist\TECHZIP1.6") {
    Remove-Item -Recurse -Force "dist\TECHZIP1.6"
}
if (Test-Path "dist\TECHZIP1.6.exe") {
    Remove-Item -Force "dist\TECHZIP1.6.exe"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "techzip16.spec") {
    Remove-Item -Force "techzip16.spec"
}

# Create spec file for version 1.6
Write-Host "`nCreating spec file for version 1.6..." -ForegroundColor Yellow
$specContent = @'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('.env.template', '.'),
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
        'google_auth_httplib2',
        'httplib2',
        'docx',
        'python-docx',
        'dotenv',
        'python-dotenv',
        'slack_sdk',
        'slack_sdk.web',
        'slack_sdk.errors',
        'cryptography',
        'cryptography.fernet',
        'utils.path_resolver',
        'utils.env_manager',
        'core.gmail_oauth_exe_helper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=['PyQt5', 'PySide6'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add Gmail OAuth credentials if exists
import os
from pathlib import Path

gmail_creds_path = Path('config/gmail_oauth_credentials.json')
if gmail_creds_path.exists():
    a.datas.append(('config/gmail_oauth_credentials.json', str(gmail_creds_path), 'DATA'))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TECHZIP1.6',
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

$specContent | Out-File -FilePath "techzip16.spec" -Encoding utf8

# Check if Gmail OAuth credentials exist
$gmailCredsPath = "config\gmail_oauth_credentials.json"
if (-not (Test-Path $gmailCredsPath)) {
    Write-Host "`nWarning: Gmail OAuth credentials not found at $gmailCredsPath" -ForegroundColor Yellow
    Write-Host "Gmail API features will not work in the EXE without this file." -ForegroundColor Yellow
    Write-Host "Users will need to set up Gmail API manually." -ForegroundColor Yellow
}

# Build the executable
Write-Host "`nBuilding executable..." -ForegroundColor Green
python -m PyInstaller techzip16.spec

# Check if build was successful
if (Test-Path "dist\TECHZIP1.6.exe") {
    Write-Host "`n✓ Build successful!" -ForegroundColor Green
    Write-Host "Executable location: $PSScriptRoot\dist\TECHZIP1.6.exe" -ForegroundColor Yellow
    
    # Get file size
    $fileSize = (Get-Item "dist\TECHZIP1.6.exe").Length / 1MB
    Write-Host "File size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    # Copy .env file to user directory for EXE environment
    Write-Host "`nSetting up EXE environment..." -ForegroundColor Yellow
    $userTechzipDir = "$env:USERPROFILE\.techzip"
    if (-not (Test-Path $userTechzipDir)) {
        New-Item -ItemType Directory -Path $userTechzipDir -Force | Out-Null
        Write-Host "Created user directory: $userTechzipDir" -ForegroundColor Green
    }
    
    if (Test-Path ".env") {
        Copy-Item ".env" "$userTechzipDir\.env" -Force
        Write-Host "✓ Copied .env file to EXE environment" -ForegroundColor Green
    } else {
        Write-Host "⚠️ .env file not found in development directory" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n✗ Build failed!" -ForegroundColor Red
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")