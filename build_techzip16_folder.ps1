# Build TECHZIP1.6 folder version using native Windows Python

Set-Location $PSScriptRoot

Write-Host "=== TECHZIP1.6 Folder Builder (Native) ===" -ForegroundColor Cyan
Write-Host "Building TECHZIP1.6 as folder distribution with faster startup" -ForegroundColor Yellow
Write-Host ""

# Clean only TECHZIP1.6 folder related builds
Write-Host "Cleaning TECHZIP1.6 folder builds..." -ForegroundColor Green
if (Test-Path "dist\TECHZIP1.6_folder") {
    Remove-Item -Recurse -Force "dist\TECHZIP1.6_folder"
}
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "techzip16_folder.spec") {
    Remove-Item -Force "techzip16_folder.spec"
}

# Create spec file for folder version
Write-Host "`nCreating spec file for folder version..." -ForegroundColor Yellow
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
    [],
    exclude_binaries=True,
    name='TECHZIP1.6',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TECHZIP1.6_folder'
)
'@

$specContent | Out-File -FilePath "techzip16_folder.spec" -Encoding utf8

# Check if Gmail OAuth credentials exist
$gmailCredsPath = "config\gmail_oauth_credentials.json"
if (-not (Test-Path $gmailCredsPath)) {
    Write-Host "`nWarning: Gmail OAuth credentials not found at $gmailCredsPath" -ForegroundColor Yellow
    Write-Host "Gmail API features will not work without this file." -ForegroundColor Yellow
}

# Build the folder distribution
Write-Host "`nBuilding folder distribution..." -ForegroundColor Green
python -m PyInstaller techzip16_folder.spec

# Check if build was successful
if (Test-Path "dist\TECHZIP1.6_folder\TECHZIP1.6.exe") {
    Write-Host "`n✓ Build successful!" -ForegroundColor Green
    Write-Host "Folder location: $PSScriptRoot\dist\TECHZIP1.6_folder\" -ForegroundColor Yellow
    
    # Get folder size
    $folderSize = (Get-ChildItem "dist\TECHZIP1.6_folder" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Write-Host "Total size: $([math]::Round($folderSize, 2)) MB" -ForegroundColor Cyan
    
    # Count files
    $fileCount = (Get-ChildItem "dist\TECHZIP1.6_folder" -Recurse -File).Count
    Write-Host "File count: $fileCount files" -ForegroundColor Cyan
    
    
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
    }
    
    # Create README for distribution
    $readmeContent = @"
TECHZIP 1.6 - 技術の泉シリーズ制作支援ツール
==========================================

【起動方法】
TECHZIP1.6.exe をダブルクリック

【フォルダ構成】
- TECHZIP1.6.exe: メインプログラム
- config/: 設定ファイル
- その他のファイル: 必要なライブラリ（削除しないでください）

【注意事項】
- このフォルダ内のファイルは削除しないでください
- フォルダごと移動する場合は全ファイルを一緒に移動してください

【トラブルシューティング】
- 起動しない場合: ウイルス対策ソフトの除外設定を確認
- エラーが出る場合: .NET Framework 4.7.2以上がインストールされているか確認
"@
    $readmeContent | Out-File -FilePath "dist\TECHZIP1.6_folder\README.txt" -Encoding utf8
    Write-Host "✓ Created README.txt" -ForegroundColor Green
    
} else {
    Write-Host "`n✗ Build failed!" -ForegroundColor Red
}

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")