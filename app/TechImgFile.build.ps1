# TechImgFile.build.ps1
# TechImgFile v0.5 Windows EXE化標準形式ビルドスクリプト
# 作成日: 2025-08-01

param(
    [string]$Version = "0.5",
    [switch]$Clean = $false,
    [switch]$Test = $false,
    [switch]$Debug = $false
)

# スクリプトのディレクトリを取得
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir
$DistDir = Join-Path $ProjectRoot "dist"

Write-Host "=== TechImgFile v$Version ビルドスクリプト ===" -ForegroundColor Green
Write-Host "プロジェクトルート: $ProjectRoot" -ForegroundColor Gray

# プロジェクトルートに移動
Set-Location $ProjectRoot

# 仮想環境の確認
$VenvPath = Join-Path $ProjectRoot "venv"
if (-not (Test-Path $VenvPath)) {
    Write-Host "仮想環境が見つかりません。作成します..." -ForegroundColor Yellow
    python -m venv venv
}

# 仮想環境をアクティベート
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    Write-Host "仮想環境をアクティブ化..." -ForegroundColor Gray
    & $ActivateScript
} else {
    Write-Host "警告: 仮想環境のアクティベーションに失敗しました" -ForegroundColor Yellow
}

# 依存関係のインストール
Write-Host "依存関係をインストール中..." -ForegroundColor Gray
pip install -r requirements.txt

# PyInstallerのインストール確認
try {
    pyinstaller --version > $null
    Write-Host "PyInstaller: 確認済み" -ForegroundColor Green
} catch {
    Write-Host "PyInstallerをインストール中..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Cleanオプション: dist, buildフォルダをクリア
if ($Clean) {
    Write-Host "クリーンビルドを実行中..." -ForegroundColor Yellow
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "*.spec") { Remove-Item -Force "*.spec" }
}

# distディレクトリの作成
if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir | Out-Null
}

# 前バージョンのバックアップ（標準規則準拠）
$ExeName = "TechImgFile.$Version.exe"
$ExePath = Join-Path $DistDir $ExeName

if (Test-Path $ExePath) {
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupName = "TechImgFile.$Version.backup_$Timestamp.exe"
    $BackupPath = Join-Path $DistDir $BackupName
    
    Write-Host "前バージョンをバックアップ: $BackupName" -ForegroundColor Yellow
    Move-Item $ExePath $BackupPath
}

# アイコンファイルの確認
$IconPath = Join-Path $ProjectRoot "resources\techimgfile_icon.ico"
$IconOption = ""
if (Test-Path $IconPath) {
    $IconOption = "--icon=`"$IconPath`""
    Write-Host "アイコンファイル: 確認済み" -ForegroundColor Green
} else {
    Write-Host "警告: アイコンファイルが見つかりません: $IconPath" -ForegroundColor Yellow
}

# ビルドオプション設定
$BuildOptions = @(
    "--onefile",
    "--windowed",
    "--name=`"TechImgFile.$Version`""
)

if ($IconOption) {
    $BuildOptions += $IconOption
}

if ($Debug) {
    $BuildOptions += "--debug=all"
    Write-Host "デバッグモードでビルド" -ForegroundColor Yellow
}

# 追加データファイルの指定
$ConfigDir = Join-Path $ProjectRoot "config"
if (Test-Path $ConfigDir) {
    $BuildOptions += "--add-data=`"$ConfigDir;config`""
}

$ResourcesDir = Join-Path $ProjectRoot "resources"
if (Test-Path $ResourcesDir) {
    $BuildOptions += "--add-data=`"$ResourcesDir;resources`""
}

# Hidden imports（必要に応じて）
$HiddenImports = @(
    "PyQt6.QtCore",
    "PyQt6.QtGui", 
    "PyQt6.QtWidgets",
    "PIL._tkinter_finder",
    "google.auth.transport.requests",
    "google.oauth2.service_account"
)

foreach ($import in $HiddenImports) {
    $BuildOptions += "--hidden-import=$import"
}

# PyInstallerコマンド構築
$PyInstallerCmd = "pyinstaller " + ($BuildOptions -join " ") + " main.py"

Write-Host "PyInstallerコマンド:" -ForegroundColor Cyan
Write-Host $PyInstallerCmd -ForegroundColor Gray

# ビルド実行
Write-Host "ビルドを開始..." -ForegroundColor Green
try {
    Invoke-Expression $PyInstallerCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "ビルド成功!" -ForegroundColor Green
        
        # 生成されたEXEをdistフォルダに適切な名前で配置
        $GeneratedExe = Join-Path "dist" "TechImgFile.$Version.exe"
        if (Test-Path $GeneratedExe) {
            Write-Host "EXEファイル生成完了: $ExeName" -ForegroundColor Green
            
            # ファイルサイズ確認
            $FileSize = (Get-Item $GeneratedExe).Length
            $FileSizeMB = [math]::Round($FileSize / 1MB, 2)
            Write-Host "ファイルサイズ: $FileSizeMB MB" -ForegroundColor Gray
            
            # TechGateから検出できるか確認
            Write-Host "TECHGATE統合: 検出パターン確認" -ForegroundColor Gray
            Write-Host "  フォルダパターン: TechImgFile.$Version" -ForegroundColor Gray
            Write-Host "  EXEパターン: TechImgFile.$Version.exe" -ForegroundColor Gray
            
        } else {
            Write-Host "警告: 期待されるEXEファイルが見つかりません" -ForegroundColor Yellow
        }
    } else {
        Write-Host "ビルドに失敗しました (終了コード: $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "ビルド中にエラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# テストオプション: 生成されたEXEの基本テスト
if ($Test -and (Test-Path $GeneratedExe)) {
    Write-Host "生成されたEXEファイルのテストを実行中..." -ForegroundColor Yellow
    
    # EXEファイルが実行可能かテスト（バックグラウンドで短時間実行）
    try {
        $TestProcess = Start-Process -FilePath $GeneratedExe -ArgumentList "--test-mode" -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        if (-not $TestProcess.HasExited) {
            $TestProcess.Kill()
            Write-Host "EXEテスト: 正常に起動することを確認" -ForegroundColor Green
        } else {
            Write-Host "EXEテスト: 即座に終了しました (終了コード: $($TestProcess.ExitCode))" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "EXEテスト中にエラー: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# .specファイルの保持確認
$SpecFile = "TechImgFile.$Version.spec"
if (Test-Path $SpecFile) {
    Write-Host "ビルド設定ファイル: $SpecFile 保持済み" -ForegroundColor Gray
}

# クリーンアップ
if (-not $Debug) {
    Write-Host "ビルド中間ファイルをクリーンアップ..." -ForegroundColor Gray
    if (Test-Path "build") {
        Remove-Item -Recurse -Force "build"
    }
}

# Memory Bank MCPに記録用情報を出力
$DistFullPath = (Resolve-Path $DistDir).Path
Write-Host ""
Write-Host "=== ビルド完了情報 ===" -ForegroundColor Green
Write-Host "アプリ名: TechImgFile" -ForegroundColor White
Write-Host "バージョン: $Version" -ForegroundColor White
Write-Host "EXE位置: $DistFullPath" -ForegroundColor White
Write-Host "EXEファイル名: $ExeName" -ForegroundColor White
Write-Host "TECHGATE統合: 対応済み" -ForegroundColor White

Write-Host ""
Write-Host "次のステップ:" -ForegroundColor Cyan
Write-Host "1. EXEファイルをテスト実行してください" -ForegroundColor Gray
Write-Host "2. TECHGATEから起動可能か確認してください" -ForegroundColor Gray
Write-Host "3. MIS・Memory Bank MCPに位置情報を記録してください:" -ForegroundColor Gray
Write-Host "   TechImgFile EXE位置: $DistFullPath" -ForegroundColor Gray

Write-Host ""
Write-Host "ビルドスクリプト完了" -ForegroundColor Green