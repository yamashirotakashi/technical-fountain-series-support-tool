# Windows環境実行スクリプト - 溢れチェッカー独立版
# PowerShell 5.1以降対応

param(
    [switch]$Debug = $false,
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== 溢れチェッカー Windows実行 ===" -ForegroundColor Cyan

# 仮想環境の確認
function Test-VirtualEnvironment {
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "❌ 仮想環境が見つかりません" -ForegroundColor Red
        Write-Host "最初に setup_windows.ps1 を実行してください" -ForegroundColor Yellow
        return $false
    }
    return $true
}

# 環境変数設定
function Set-EnvironmentVariables {
    # Tesseract OCRパス設定
    $tesseractPaths = @(
        "${env:ProgramFiles}\Tesseract-OCR\tesseract.exe",
        "${env:ProgramFiles(x86)}\Tesseract-OCR\tesseract.exe",
        "C:\Tesseract-OCR\tesseract.exe"
    )
    
    foreach ($path in $tesseractPaths) {
        if (Test-Path $path) {
            $env:TESSERACT_CMD = $path
            if ($Verbose) {
                Write-Host "Tesseract パス設定: $path" -ForegroundColor Green
            }
            break
        }
    }
    
    # その他の環境変数
    $env:PYTHONPATH = (Get-Location).Path
    $env:OVERFLOW_CHECKER_HOME = (Get-Location).Path
    
    if ($Debug) {
        $env:OVERFLOW_CHECKER_DEBUG = "1"
        Write-Host "デバッグモード有効" -ForegroundColor Yellow
    }
}

# ログディレクトリ確認
function Ensure-LogDirectory {
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }
}

# アプリケーション実行
function Start-Application {
    Write-Host "溢れチェッカーを起動中..." -ForegroundColor Yellow
    
    # 実行前チェック
    if (-not (Test-Path "run_ultimate.py")) {
        Write-Host "❌ run_ultimate.py が見つかりません" -ForegroundColor Red
        exit 1
    }
    
    try {
        # 仮想環境でアプリケーション実行
        if ($Debug) {
            & .\venv\Scripts\python.exe run_ultimate.py --debug
        } else {
            & .\venv\Scripts\python.exe run_ultimate.py
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ アプリケーションの実行中にエラーが発生しました (終了コード: $LASTEXITCODE)" -ForegroundColor Red
        } else {
            Write-Host "✅ アプリケーションが正常に終了しました" -ForegroundColor Green
        }
        
    } catch {
        Write-Host "❌ 実行エラー: $($_.Exception.Message)" -ForegroundColor Red
        if ($Debug) {
            Write-Host "詳細: $($_.Exception)" -ForegroundColor Red
        }
    }
}

# メイン処理
try {
    # 仮想環境確認
    if (-not (Test-VirtualEnvironment)) {
        exit 1
    }
    
    # 環境変数設定
    Set-EnvironmentVariables
    
    # ログディレクトリ確認
    Ensure-LogDirectory
    
    # アプリケーション起動
    Start-Application
    
} catch {
    Write-Host "❌ 実行中にエラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    if ($Debug) {
        Write-Host "スタックトレース: $($_.Exception.StackTrace)" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""
Write-Host "実行完了" -ForegroundColor Cyan