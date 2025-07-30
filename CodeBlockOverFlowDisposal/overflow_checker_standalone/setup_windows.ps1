# Windows環境セットアップスクリプト - 溢れチェッカー独立版
# PowerShell 5.1以降対応

param(
    [switch]$Clean = $false,
    [switch]$SkipTesseract = $false,
    [string]$RequiredPythonVersion = "3.9"  # 変数名を変更して競合回避
)

$ErrorActionPreference = "Stop"

Write-Host "=== 溢れチェッカー Windows環境セットアップ ===" -ForegroundColor Cyan
Write-Host "Python 最小要求バージョン: $RequiredPythonVersion" -ForegroundColor Yellow

# 管理者権限チェック
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Pythonインストール確認
function Test-PythonInstallation {
    Write-Host "Python検出を試行中..." -ForegroundColor Yellow
    
    # 複数のPythonコマンドを試行
    $pythonCommands = @("python", "python3", "py")
    $foundPython = $false
    $pythonCommand = ""
    
    foreach ($cmd in $pythonCommands) {
        try {
            Write-Host "  $cmd を確認中..." -ForegroundColor Gray
            
            # PowerShellの実行ポリシーを考慮してコマンド実行
            $pythonOutput = ""
            if ($cmd -eq "py") {
                $pythonOutput = (& py --version 2>&1) | Out-String
            } else {
                $pythonOutput = (& $cmd --version 2>&1) | Out-String
            }
            
            # 文字列のトリムと正規化
            $pythonOutput = $pythonOutput.Trim()
            Write-Host "  $cmd の結果: '$pythonOutput'" -ForegroundColor Gray
            
            # より精密な正規表現パターンでバージョン抽出
            if ($pythonOutput -match "Python (\d+\.\d+(?:\.\d+)?)") {
                $versionString = $matches[1]
                Write-Host "  抽出されたバージョン文字列: '$versionString'" -ForegroundColor Gray
                
                try {
                    # バージョン文字列を明示的にSystem.Versionオブジェクトに変換
                    Write-Host "  バージョン変換を試行: '$versionString'" -ForegroundColor Gray
                    $version = New-Object System.Version($versionString)
                    $requiredVersion = New-Object System.Version($RequiredPythonVersion)
                    
                    Write-Host "  $cmd : Python $version を検出" -ForegroundColor Cyan
                    Write-Host "  要求バージョン: $requiredVersion" -ForegroundColor Gray
                    
                    if ($version -ge $requiredVersion) {
                        Write-Host "✅ Python $version が見つかりました ($cmd)" -ForegroundColor Green
                        $script:PythonCommand = $cmd  # グローバル変数として保存
                        return $true
                    } else {
                        Write-Host "  ⚠️ Python $version は要求バージョン $RequiredPythonVersion より古いです" -ForegroundColor Yellow
                    }
                } catch {
                    Write-Host "  ❌ バージョン解析エラー: $($_.Exception.Message)" -ForegroundColor Red
                    Write-Host "  バージョン文字列: '$versionString'" -ForegroundColor Red
                    Write-Host "  要求バージョン文字列: '$RequiredPythonVersion'" -ForegroundColor Red
                    
                    # フォールバック: 文字列比較でバージョンチェック
                    Write-Host "  フォールバック: 文字列比較を試行..." -ForegroundColor Yellow
                    Write-Host "  検出バージョン: '$versionString'" -ForegroundColor Gray
                    Write-Host "  要求バージョン: '$RequiredPythonVersion'" -ForegroundColor Gray
                    
                    try {
                        $versionParts = $versionString.Split('.')
                        $requiredParts = $RequiredPythonVersion.Split('.')
                        
                        Write-Host "  バージョン部分: $($versionParts -join ', ')" -ForegroundColor Gray
                        Write-Host "  要求部分: $($requiredParts -join ', ')" -ForegroundColor Gray
                        
                        if ($versionParts.Length -ge 2 -and $requiredParts.Length -ge 2) {
                            $majorVersion = [int]$versionParts[0]
                            $minorVersion = [int]$versionParts[1]
                            $requiredMajor = [int]$requiredParts[0]
                            $requiredMinor = [int]$requiredParts[1]
                            
                            Write-Host "  比較: $majorVersion.$minorVersion vs $requiredMajor.$requiredMinor" -ForegroundColor Gray
                            
                            if (($majorVersion -gt $requiredMajor) -or 
                                ($majorVersion -eq $requiredMajor -and $minorVersion -ge $requiredMinor)) {
                                Write-Host "✅ Python $versionString が見つかりました ($cmd) - 文字列比較" -ForegroundColor Green
                                $script:PythonCommand = $cmd
                                return $true
                            } else {
                                Write-Host "  ⚠️ Python $versionString は要求バージョン $RequiredPythonVersion より古いです" -ForegroundColor Yellow
                            }
                        } else {
                            Write-Host "  ❌ バージョン部分の解析に失敗" -ForegroundColor Red
                        }
                    } catch {
                        Write-Host "  ❌ フォールバック処理エラー: $($_.Exception.Message)" -ForegroundColor Red
                    }
                }
            } else {
                Write-Host "  ❌ $cmd からのバージョン情報が不正: $pythonOutput" -ForegroundColor Red
            }
        } catch {
            Write-Host "  ❌ $cmd の実行に失敗: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    # すべて失敗した場合
    Write-Host "❌ 適切なPythonが見つかりません" -ForegroundColor Red
    Write-Host "要求バージョン: $RequiredPythonVersion 以降" -ForegroundColor Yellow
    
    # インストール済みPythonの詳細表示
    Write-Host "`n利用可能なPythonコマンドの確認:" -ForegroundColor Yellow
    foreach ($cmd in $pythonCommands) {
        try {
            $cmdPath = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
            if ($cmdPath) {
                Write-Host "  $cmd : $cmdPath" -ForegroundColor Cyan
            }
        } catch {
            # 無視
        }
    }
    
    return $false
}

# 仮想環境作成
function New-VirtualEnvironment {
    Write-Host "仮想環境を作成中..." -ForegroundColor Yellow
    
    if ($Clean -and (Test-Path "venv")) {
        Write-Host "既存の仮想環境を削除中..." -ForegroundColor Yellow
        Remove-Item -Path "venv" -Recurse -Force
    }
    
    if (-not (Test-Path "venv")) {
        # グローバル変数のPythonCommandを使用、なければデフォルトのpythonを使用
        $cmdToUse = if ($script:PythonCommand) { $script:PythonCommand } else { "python" }
        Write-Host "使用するPythonコマンド: $cmdToUse" -ForegroundColor Cyan
        
        & $cmdToUse -m venv venv
        if ($LASTEXITCODE -ne 0) {
            throw "仮想環境の作成に失敗しました (使用コマンド: $cmdToUse)"
        }
    }
    
    Write-Host "✅ 仮想環境作成完了" -ForegroundColor Green
}

# 依存関係インストール
function Install-Dependencies {
    Write-Host "依存関係をインストール中..." -ForegroundColor Yellow
    
    # Windows環境変数の設定（WSL混在環境対応）
    $env:PYTHONPATH = ""  # WSLパスの干渉を回避
    $env:PATH = $env:PATH -replace "/usr/bin:", ""  # Linuxパスを除去
    
    # 仮想環境のパス確認
    $venvPython = ".\venv\Scripts\python.exe"
    $venvPip = ".\venv\Scripts\pip.exe"
    
    if (-not (Test-Path $venvPython)) {
        throw "仮想環境のPythonが見つかりません: $venvPython"
    }
    
    Write-Host "使用するPythonパス: $venvPython" -ForegroundColor Cyan
    Write-Host "使用するpipパス: $venvPip" -ForegroundColor Cyan
    
    # pipアップグレード（環境変数を明示的に設定）
    Write-Host "pipをアップグレード中..." -ForegroundColor Yellow
    $env:VIRTUAL_ENV = (Resolve-Path ".\venv").Path
    & $venvPython -m pip install --upgrade pip
    
    if ($LASTEXITCODE -ne 0) {
        throw "pipアップグレードに失敗しました"
    }
    
    # requirements.txtから依存関係をインストール
    Write-Host "requirements.txtから依存関係をインストール中..." -ForegroundColor Yellow
    & $venvPip install -r requirements.txt --no-warn-script-location
    
    if ($LASTEXITCODE -ne 0) {
        throw "依存関係のインストールに失敗しました"
    }
    
    Write-Host "✅ 依存関係インストール完了" -ForegroundColor Green
}

# Tesseract OCRセットアップ
function Install-TesseractOCR {
    if ($SkipTesseract) {
        Write-Host "⏭️ Tesseract OCRのインストールをスキップします" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Tesseract OCRの確認中..." -ForegroundColor Yellow
    
    # Tesseractが既にインストールされているかチェック
    $tesseractPaths = @(
        "${env:ProgramFiles}\Tesseract-OCR\tesseract.exe",
        "${env:ProgramFiles(x86)}\Tesseract-OCR\tesseract.exe",
        "C:\Tesseract-OCR\tesseract.exe"
    )
    
    $tesseractFound = $false
    foreach ($path in $tesseractPaths) {
        if (Test-Path $path) {
            Write-Host "✅ Tesseract OCRが見つかりました: $path" -ForegroundColor Green
            $env:TESSERACT_CMD = $path
            $tesseractFound = $true
            break
        }
    }
    
    if (-not $tesseractFound) {
        Write-Host "⚠️ Tesseract OCRが見つかりません" -ForegroundColor Yellow
        Write-Host "以下の方法でインストールしてください:" -ForegroundColor Yellow
        Write-Host "1. 手動インストール: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
        Write-Host "2. Chocolatey: choco install tesseract" -ForegroundColor Cyan
        Write-Host "3. winget: winget install UB-Mannheim.TesseractOCR" -ForegroundColor Cyan
        
        # Chocolateyが利用可能な場合は自動インストールを提案
        try {
            & choco --version | Out-Null
            $choice = Read-Host "Chocolateyを使用してTesseractを自動インストールしますか？ (y/N)"
            if ($choice -eq "y" -or $choice -eq "Y") {
                Write-Host "Chocolateyを使用してTesseractをインストール中..." -ForegroundColor Yellow
                & choco install tesseract -y
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Tesseract OCRインストール完了" -ForegroundColor Green
                } else {
                    Write-Host "❌ Tesseractインストールに失敗しました" -ForegroundColor Red
                }
            }
        } catch {
            # Chocolateyが無い場合は手動インストールを促す
        }
    }
}

# ディレクトリ構造作成
function New-DirectoryStructure {
    Write-Host "ディレクトリ構造を作成中..." -ForegroundColor Yellow
    
    $directories = @(
        "data",
        "logs",
        "temp",
        "assets",
        "dist",
        "build"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Host "✅ ディレクトリ構造作成完了" -ForegroundColor Green
}

# アイコンファイル作成
function New-ApplicationIcon {
    Write-Host "アプリケーションアイコンを作成中..." -ForegroundColor Yellow
    
    $iconScript = @"
from PIL import Image, ImageDraw, ImageFont
import os

def create_overflow_icon():
    '''溢れチェッカーのアイコン作成'''
    # 256x256のアイコン作成
    img = Image.new('RGBA', (256, 256), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 背景（グラデーション風）
    for i in range(256):
        color = (50, 100 + i//2, 200, 255)
        draw.rectangle([0, i, 256, i+1], fill=color)
    
    # "OC"の文字（Overflow Checker）
    try:
        # Windowsの標準フォント
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        # フォールバック
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 120)
        except:
            font = ImageFont.load_default()
    
    # 白い文字で"OC"を描画
    draw.text((40, 60), "OC", fill=(255, 255, 255, 255), font=font)
    
    # 溢れを示す赤い線（右端）
    draw.rectangle([200, 100, 256, 120], fill=(255, 0, 0, 255))
    
    # 複数サイズのアイコンを含むICOファイル作成
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    img.save("assets/overflow_checker.ico", sizes=[(16,16), (32,32), (48,48), (256,256)])
    print("✅ アイコンファイル作成完了: assets/overflow_checker.ico")

if __name__ == "__main__":
    create_overflow_icon()
"@
    
    $iconScript | Out-File -FilePath "create_icon.py" -Encoding UTF8
    & .\venv\Scripts\python.exe create_icon.py
    Remove-Item "create_icon.py" -Force
    
    Write-Host "✅ アプリケーションアイコン作成完了" -ForegroundColor Green
}

# バージョンファイル作成
function New-VersionFile {
    Write-Host "バージョンファイルを作成中..." -ForegroundColor Yellow
    
    $versionContent = @"
# -*- coding: utf-8 -*-
'''
バージョン情報ファイル
自動生成 - 編集しないでください
'''

VERSION = '1.0.0'
BUILD_DATE = '$(Get-Date -Format "yyyy-MM-dd")'
BUILD_TIME = '$(Get-Date -Format "HH:mm:ss")'
COMMIT_HASH = ''

# アプリケーション情報
APP_NAME = '溢れチェッカー'
APP_NAME_EN = 'Overflow Checker'
DESCRIPTION = 'PDF コードブロック溢れ検出ツール'
AUTHOR = 'Claude Code Assistant'
COPYRIGHT = '© 2025 Claude Code Assistant'

def get_version_string():
    '''バージョン文字列を取得'''
    return f'{APP_NAME} v{VERSION} ({BUILD_DATE})'

def get_full_version_info():
    '''完全なバージョン情報を取得'''
    return {
        'version': VERSION,
        'build_date': BUILD_DATE,
        'build_time': BUILD_TIME,
        'app_name': APP_NAME,
        'app_name_en': APP_NAME_EN,
        'description': DESCRIPTION,
        'author': AUTHOR,
        'copyright': COPYRIGHT
    }
"@
    
    $versionContent | Out-File -FilePath "version.py" -Encoding UTF8
    Write-Host "✅ バージョンファイル作成完了" -ForegroundColor Green
}

# 動作テスト
function Test-Installation {
    Write-Host "インストールをテスト中..." -ForegroundColor Yellow
    
    $testScript = @"
import sys
print(f"Python: {sys.version}")

# 主要ライブラリのインポートテスト
try:
    import PyQt6
    print(f"✅ PyQt6: {PyQt6.QtCore.PYQT_VERSION_STR}")
except ImportError as e:
    print(f"❌ PyQt6: {e}")

try:
    import fitz
    print(f"✅ PyMuPDF: {fitz.version[0]}")
except ImportError as e:
    print(f"❌ PyMuPDF: {e}")

try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV: {e}")

try:
    import numpy
    print(f"✅ NumPy: {numpy.__version__}")
except ImportError as e:
    print(f"❌ NumPy: {e}")

try:
    import pytesseract
    print(f"✅ pytesseract: インポート成功")
except ImportError as e:
    print(f"❌ pytesseract: {e}")

print("テスト完了")
"@
    
    $testScript | Out-File -FilePath "test_imports.py" -Encoding UTF8
    & .\venv\Scripts\python.exe test_imports.py
    Remove-Item "test_imports.py" -Force
    
    Write-Host "✅ インストールテスト完了" -ForegroundColor Green
}

# メイン処理
try {
    # Pythonインストール確認
    if (-not (Test-PythonInstallation)) {
        Write-Host "Python $RequiredPythonVersion 以降をインストールしてから再実行してください" -ForegroundColor Red
        Write-Host "ダウンロード: https://www.python.org/downloads/" -ForegroundColor Cyan
        exit 1
    }
    
    # 仮想環境作成
    New-VirtualEnvironment
    
    # 依存関係インストール
    Install-Dependencies
    
    # Tesseract OCRセットアップ
    Install-TesseractOCR
    
    # ディレクトリ構造作成
    New-DirectoryStructure
    
    # アイコン作成
    New-ApplicationIcon
    
    # バージョンファイル作成
    New-VersionFile
    
    # 動作テスト
    Test-Installation
    
    Write-Host ""
    Write-Host "🎉 Windows環境セットアップ完了！" -ForegroundColor Green
    Write-Host ""
    Write-Host "次のステップ:" -ForegroundColor Cyan
    Write-Host "1. アプリケーション実行: .\run_windows.ps1" -ForegroundColor White
    Write-Host "2. EXE化実行: .\build_exe.ps1" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ セットアップ中にエラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}