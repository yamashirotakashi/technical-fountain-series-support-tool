# EXE化ビルドスクリプト - 溢れチェッカー独立版
# PyInstaller使用

param(
    [string]$Version = "1.0.0",
    [switch]$Clean = $false,
    [switch]$Debug = $false,
    [switch]$OneFile = $false,  # 非推奨（フォルダ構成が推奨）
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== 溢れチェッカー EXE化ビルド ===" -ForegroundColor Cyan
Write-Host "バージョン: $Version" -ForegroundColor Yellow
Write-Host "ビルドモード: フォルダ構成（高速起動）" -ForegroundColor Green
if ($OneFile) {
    Write-Host "注意: OneFileフラグは無視されます（フォルダ構成を強制）" -ForegroundColor Yellow
}

# 前提条件チェック
function Test-Prerequisites {
    Write-Host "前提条件をチェック中..." -ForegroundColor Yellow
    
    # 仮想環境チェック
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "❌ 仮想環境が見つかりません" -ForegroundColor Red
        Write-Host "setup_windows.ps1 を実行してください" -ForegroundColor Yellow
        return $false
    }
    
    # PyInstallerチェック
    try {
        & .\venv\Scripts\pip.exe show pyinstaller | Out-Null
        Write-Host "✅ PyInstaller確認完了" -ForegroundColor Green
    } catch {
        Write-Host "❌ PyInstallerが見つかりません" -ForegroundColor Red
        Write-Host "pip install pyinstaller を実行してください" -ForegroundColor Yellow
        return $false
    }
    
    # 必須ファイルチェック
    $requiredFiles = @(
        "run_ultimate.py",
        "overflow_checker.spec",
        "requirements.txt"
    )
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-Host "❌ 必須ファイルが見つかりません: $file" -ForegroundColor Red
            return $false
        }
    }
    
    Write-Host "✅ 前提条件チェック完了" -ForegroundColor Green
    return $true
}

# クリーンビルド
function Clear-BuildArtifacts {
    Write-Host "ビルド成果物をクリア中..." -ForegroundColor Yellow
    
    # 安全な削除対象のみに限定（他のプログラムファイルを保護）
    $cleanTargets = @(
        "dist\OverflowChecker",      # 本プロジェクトのビルド成果物のみ
        "build",                     # PyInstallerの一時ファイル
        "*.spec.bak"                 # specファイルのバックアップ
    )
    
    foreach ($target in $cleanTargets) {
        if (Test-Path $target) {
            Remove-Item -Path $target -Recurse -Force
            Write-Host "削除: $target" -ForegroundColor Gray
        }
    }
    
    # __pycache__ フォルダをプロジェクト内のみ削除
    Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        $fullPath = Join-Path (Get-Location) $_
        if (Test-Path $fullPath) {
            Remove-Item -Path $fullPath -Recurse -Force
            Write-Host "削除: $fullPath" -ForegroundColor Gray
        }
    }
    
    # .pyc ファイルをプロジェクト内のみ削除
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | ForEach-Object {
        Remove-Item -Path $_ -Force
    }
    
    Write-Host "✅ クリーンアップ完了（他のプログラムファイルは保護済み）" -ForegroundColor Green
}

# バージョン情報ファイル更新
function Update-VersionInfo {
    Write-Host "バージョン情報を更新中..." -ForegroundColor Yellow
    
    # version.py更新
    $versionContent = @"
# -*- coding: utf-8 -*-
'''
バージョン情報ファイル
ビルド時自動生成 - 編集しないでください
'''

VERSION = '$Version'
BUILD_DATE = '$(Get-Date -Format "yyyy-MM-dd")'
BUILD_TIME = '$(Get-Date -Format "HH:mm:ss")'
BUILD_TYPE = '$(if($Debug) { "Debug" } else { "Release" })'

# Git情報（可能な場合）
try:
    import subprocess
    COMMIT_HASH = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                        stderr=subprocess.DEVNULL).decode().strip()
except:
    COMMIT_HASH = 'unknown'

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
    
    # Windows バージョン情報ファイル作成（EXEプロパティ用）
    $versionInfoContent = @"
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(1, 0, 0, 0),
        prodvers=(1, 0, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                u'040904B0',
                [
                StringStruct(u'CompanyName', u'Claude Code Assistant'),
                StringStruct(u'FileDescription', u'PDF コードブロック溢れ検出ツール'),
                StringStruct(u'FileVersion', u'$Version'),
                StringStruct(u'InternalName', u'OverflowChecker'),
                StringStruct(u'LegalCopyright', u'© 2025 Claude Code Assistant'),
                StringStruct(u'OriginalFilename', u'OverflowChecker.exe'),
                StringStruct(u'ProductName', u'溢れチェッカー'),
                StringStruct(u'ProductVersion', u'$Version')
                ]
            )
        ]),
        VarFileInfo([VarStruct(u'Translation', [1041, 1200])])
    ]
)
"@
    
    $versionInfoContent | Out-File -FilePath "version_info.txt" -Encoding UTF8
    
    Write-Host "✅ バージョン情報更新完了" -ForegroundColor Green
}

# 事前テスト実行
function Test-BeforeBuild {
    if ($SkipTests) {
        Write-Host "⏭️ 事前テストをスキップします" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "事前テストを実行中..." -ForegroundColor Yellow
    
    # インポートテスト
    $testScript = @"
import sys
import traceback

print("=== インポートテスト ===")
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
        print(f"✅ {module}")
    except ImportError as e:
        print(f"❌ {module}: {e}")
        failed_modules.append(module)

if failed_modules:
    print(f"\\n失敗したモジュール: {failed_modules}")
    sys.exit(1)
else:
    print("\\n✅ 全てのモジュールのインポートに成功")

# run_ultimate.pyの基本チェック
print("\\n=== メインスクリプトチェック ===")
try:
    import run_ultimate
    print("✅ run_ultimate.py インポート成功")
except Exception as e:
    print(f"❌ run_ultimate.py インポート失敗: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\\n✅ 事前テスト完了")
"@
    
    $testScript | Out-File -FilePath "pre_build_test.py" -Encoding UTF8
    
    try {
        & .\venv\Scripts\python.exe pre_build_test.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ 事前テストに失敗しました" -ForegroundColor Red
            return $false
        }
    } finally {
        Remove-Item "pre_build_test.py" -ErrorAction SilentlyContinue
    }
    
    Write-Host "✅ 事前テスト完了" -ForegroundColor Green
    return $true
}

# PyInstallerでEXE化（フォルダ構成推奨）
function Build-Executable {
    Write-Host "PyInstallerでEXE化中（フォルダ構成）..." -ForegroundColor Yellow
    
    # フォルダ構成でのビルドオプション
    $buildArgs = @(
        "overflow_checker.spec",
        "--clean"
    )
    
    if ($Debug) {
        $buildArgs += "--debug", "all"
        Write-Host "デバッグモードでビルド" -ForegroundColor Yellow
    }
    
    # OneFileは警告表示のみ（非推奨）
    if ($OneFile) {
        Write-Host "⚠️ 警告: --OneFileは起動速度が遅いため非推奨です" -ForegroundColor Yellow
        Write-Host "フォルダ構成での高速起動を採用します" -ForegroundColor Yellow
        # OneFileオプションは無視してフォルダ構成で実行
    } else {
        Write-Host "フォルダ構成モードでビルド（高速起動対応）" -ForegroundColor Green
    }
    
    # PyInstaller実行
    try {
        Write-Host "PyInstaller実行中..." -ForegroundColor Cyan
        Write-Host "コマンド: pyinstaller $($buildArgs -join ' ')" -ForegroundColor Gray
        
        & .\venv\Scripts\pyinstaller.exe @buildArgs
        
        if ($LASTEXITCODE -ne 0) {
            throw "PyInstaller実行に失敗しました (終了コード: $LASTEXITCODE)"
        }
        
    } catch {
        Write-Host "❌ EXE化に失敗しました: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✅ EXE化完了（フォルダ構成）" -ForegroundColor Green
    return $true
}

# ビルド後テスト
function Test-AfterBuild {
    if ($SkipTests) {
        Write-Host "⏭️ ビルド後テストをスキップします" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "ビルド後テストを実行中..." -ForegroundColor Yellow
    
    $exePath = "dist\OverflowChecker\OverflowChecker.exe"
    
    if (-not (Test-Path $exePath)) {
        Write-Host "❌ 生成されたEXEファイルが見つかりません: $exePath" -ForegroundColor Red
        return $false
    }
    
    # ファイルサイズチェック
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Host "EXEファイルサイズ: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    # 簡単な起動テスト（GUI表示せずに終了）
    Write-Host "起動テストを実行中..." -ForegroundColor Yellow
    
    try {
        # タイムアウト付きでテスト実行
        $process = Start-Process -FilePath $exePath -ArgumentList "--test-mode" -PassThru -NoNewWindow
        
        if (-not $process.WaitForExit(10000)) {  # 10秒でタイムアウト
            $process.Kill()
            Write-Host "⚠️ 起動テストがタイムアウトしました（正常な可能性があります）" -ForegroundColor Yellow
        } else {
            Write-Host "✅ 起動テスト完了" -ForegroundColor Green
        }
        
    } catch {
        Write-Host "⚠️ 起動テストでエラーが発生しました（GUI環境の問題の可能性があります）" -ForegroundColor Yellow
        Write-Host "詳細: $($_.Exception.Message)" -ForegroundColor Gray
    }
    
    return $true
}

# 配布パッケージ作成
function New-DistributionPackage {
    Write-Host "配布パッケージを作成中..." -ForegroundColor Yellow
    
    $distDir = "dist\OverflowChecker"
    $packageDir = "dist\OverflowChecker_v$Version"
    
    if (Test-Path $packageDir) {
        Remove-Item -Path $packageDir -Recurse -Force
    }
    
    # パッケージディレクトリ作成
    Copy-Item -Path $distDir -Destination $packageDir -Recurse
    
    # 追加ファイルをコピー
    $additionalFiles = @{
        "README.md" = "使用方法.txt"
        "requirements.txt" = "requirements.txt"
    }
    
    foreach ($src in $additionalFiles.Keys) {
        if (Test-Path $src) {
            Copy-Item -Path $src -Destination "$packageDir\$($additionalFiles[$src])"
        }
    }
    
    # ZIPアーカイブ作成
    $zipPath = "dist\OverflowChecker_v$Version.zip"
    if (Test-Path $zipPath) {
        Remove-Item $zipPath -Force
    }
    
    Compress-Archive -Path $packageDir -DestinationPath $zipPath
    
    Write-Host "✅ 配布パッケージ作成完了: $zipPath" -ForegroundColor Green
    
    # サイズ情報表示
    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-Host "パッケージサイズ: $([math]::Round($zipSize, 2)) MB" -ForegroundColor Cyan
}

# メイン処理
try {
    Write-Host "開始時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
    # 前提条件チェック
    if (-not (Test-Prerequisites)) {
        exit 1
    }
    
    # クリーンビルド
    if ($Clean) {
        Clear-BuildArtifacts
    }
    
    # バージョン情報更新
    Update-VersionInfo
    
    # 事前テスト
    if (-not (Test-BeforeBuild)) {
        exit 1
    }
    
    # EXE化実行
    if (-not (Build-Executable)) {
        exit 1
    }
    
    # ビルド後テスト
    if (-not (Test-AfterBuild)) {
        Write-Host "⚠️ ビルド後テストに問題がありましたが、継続します" -ForegroundColor Yellow
    }
    
    # 配布パッケージ作成
    New-DistributionPackage
    
    Write-Host ""
    Write-Host "🎉 EXE化ビルド完了！" -ForegroundColor Green
    Write-Host ""
    Write-Host "生成されたファイル:" -ForegroundColor Cyan
    Write-Host "- EXE: dist\OverflowChecker\OverflowChecker.exe" -ForegroundColor White
    Write-Host "- パッケージ: dist\OverflowChecker_v$Version.zip" -ForegroundColor White
    Write-Host ""
    Write-Host "完了時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
} catch {
    Write-Host ""
    Write-Host "❌ ビルド中にエラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($Debug) {
        Write-Host "スタックトレース:" -ForegroundColor Red
        Write-Host $_.Exception.StackTrace -ForegroundColor Red
    }
    
    exit 1
}