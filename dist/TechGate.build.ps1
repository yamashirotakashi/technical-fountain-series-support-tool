# EXE化ビルドスクリプト - TechGate（標準仕様準拠版）
# PyInstaller使用 - 標準規則準拠

param(
    [string]$Version = "0.6",
    [switch]$Clean = $false,
    [switch]$Debug = $false,
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== TechGate EXE化ビルド（標準仕様）===" -ForegroundColor Cyan
Write-Host "バージョン: $Version" -ForegroundColor Yellow
Write-Host "ビルドモード: フォルダ構成（高速起動）" -ForegroundColor Green

# 現在のディレクトリ（distフォルダ）をワーキングディレクトリとして使用
$DistPath = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $DistPath

Write-Host "Distパス: $DistPath" -ForegroundColor Gray
Write-Host "プロジェクトルート: $ProjectRoot" -ForegroundColor Gray

# 前提条件チェック
function Test-Prerequisites {
    Write-Host "前提条件をチェック中..." -ForegroundColor Yellow
    
    # TechGateスクリプトファイルの存在チェック
    $launcherScript = Join-Path $ProjectRoot "src" "TechGate.py"
    if (-not (Test-Path $launcherScript)) {
        Write-Host "[ERROR] TechGateスクリプトが見つかりません: $launcherScript" -ForegroundColor Red
        Write-Host "現在のディレクトリ内容:" -ForegroundColor Yellow
        Get-ChildItem -Path $DistPath -Name "*.py" | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
        return $false
    }
    
    # Python環境チェック
    try {
        $pythonVersion = & python --version 2>&1
        Write-Host "[OK] Python環境確認: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Python環境が見つかりません" -ForegroundColor Red
        return $false
    }
    
    # PyInstallerチェック
    try {
        & pip show pyinstaller | Out-Null
        Write-Host "[OK] PyInstaller確認完了" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] PyInstallerが見つかりません" -ForegroundColor Red
        Write-Host "pip install pyinstaller を実行してください" -ForegroundColor Yellow
        return $false
    }
    
    # 必要な依存関係チェック
    $requiredPackages = @("PyQt6")
    foreach ($package in $requiredPackages) {
        try {
            & pip show $package | Out-Null
            Write-Host "[OK] $package 確認完了" -ForegroundColor Green
        } catch {
            Write-Host "[ERROR] $package が見つかりません" -ForegroundColor Red
            Write-Host "pip install $package を実行してください" -ForegroundColor Yellow
            return $false
        }
    }
    
    Write-Host "[OK] 前提条件チェック完了" -ForegroundColor Green
    return $true
}

# クリーンビルド
function Clear-BuildArtifacts {
    Write-Host "ビルド成果物をクリア中..." -ForegroundColor Yellow
    
    # 削除対象（標準規則準拠）
    $cleanTargets = @(
        "TechGate.$Version",                # 既存のビルド成果物
        "TechGate_v*",                      # 旧バージョン
        "build",                            # PyInstallerの一時ファイル
        "__pycache__",                      # Pythonキャッシュ
        "*.spec",                          # PyInstallerのspecファイル
        "*.spec.bak"                       # specファイルのバックアップ
    )
    
    foreach ($target in $cleanTargets) {
        $fullPath = Join-Path $DistPath $target
        if (Test-Path $fullPath) {
            Remove-Item -Path $fullPath -Recurse -Force
            Write-Host "削除: $target" -ForegroundColor Gray
        }
    }
    
    Write-Host "[OK] クリーンアップ完了" -ForegroundColor Green
}

# バージョン情報ファイル作成
function New-VersionInfo {
    Write-Host "バージョン情報ファイルを作成中..." -ForegroundColor Yellow
    
    $versionInfoContent = @"
VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(0, 6, 0, 0),
        prodvers=(0, 6, 0, 0),
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
                StringStruct(u'FileDescription', u'TechGate 4ツール統合ランチャー'),
                StringStruct(u'FileVersion', u'$Version'),
                StringStruct(u'InternalName', u'TechGate'),
                StringStruct(u'LegalCopyright', u'© 2025 Claude Code Assistant'),
                StringStruct(u'OriginalFilename', u'TechGate.$Version.exe'),
                StringStruct(u'ProductName', u'TechGate 4ツール統合ランチャー'),
                StringStruct(u'ProductVersion', u'$Version')
                ]
            )
        ]),
        VarFileInfo([VarStruct(u'Translation', [1041, 1200])])
    ]
)
"@
    
    $versionInfoPath = Join-Path $DistPath "version_info.txt"
    $versionInfoContent | Out-File -FilePath $versionInfoPath -Encoding UTF8
    
    Write-Host "[OK] バージョン情報ファイル作成完了" -ForegroundColor Green
    return $versionInfoPath
}

# Windows Defender対応チェック
function Test-WindowsDefenderIssue {
    Write-Host "Windows Defender設定をチェック中..." -ForegroundColor Yellow
    
    # 現在のプロジェクトディレクトリが除外リストに含まれているかチェック
    try {
        $exclusions = Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
        $currentPath = $ProjectRoot.ToLower()
        
        $isExcluded = $exclusions | Where-Object { $_.ToLower() -eq $currentPath }
        
        if (-not $isExcluded) {
            Write-Host "[WARNING] プロジェクトディレクトリがWindows Defenderの除外リストに含まれていません" -ForegroundColor Red
            Write-Host "このため、PyInstallerの実行中にWindows Defenderによってブロックされる可能性があります" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "解決方法:" -ForegroundColor Cyan
            Write-Host "1. 管理者権限でPowerShellを開く" -ForegroundColor White
            Write-Host "2. 以下のコマンドを実行:" -ForegroundColor White
            Write-Host "   Add-MpPreference -ExclusionPath `"$ProjectRoot`"" -ForegroundColor Gray
            Write-Host "または" -ForegroundColor Cyan
            Write-Host "Windows Security → ウイルスと脅威の防止 → 設定の管理 → 除外の追加または削除" -ForegroundColor White
            Write-Host "でフォルダを除外リストに追加してください" -ForegroundColor White
            Write-Host ""
            
            $continue = Read-Host "除外設定後に続行しますか？ (y/N)"
            if ($continue -ne "y" -and $continue -ne "Y") {
                return $false
            }
        } else {
            Write-Host "[OK] プロジェクトディレクトリはWindows Defenderの除外リストに含まれています" -ForegroundColor Green
        }
    } catch {
        Write-Host "[WARNING] Windows Defender設定の確認に失敗しました: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "管理者権限が必要な可能性があります" -ForegroundColor Yellow
        
        $continue = Read-Host "続行しますか？ (y/N)"
        if ($continue -ne "y" -and $continue -ne "Y") {
            return $false
        }
    }
    
    return $true
}

# PyInstallerでEXE化（Defender対応版）
function Build-Executable {
    Write-Host "PyInstallerでEXE化中（フォルダ構成）..." -ForegroundColor Yellow
    
    # Windows Defender対応チェック
    if (-not (Test-WindowsDefenderIssue)) {
        Write-Host "[ERROR] Windows Defender設定を確認してください" -ForegroundColor Red
        return $false
    }
    
    # ビルドオプション（標準規則準拠）
    $launcherScript = Join-Path $ProjectRoot "src" "TechGate.py"
    $buildArgs = @(
        $launcherScript,
        "--clean",
        "--onedir",
        "--windowed",
        "--name", "TechGate.$Version",
        "--distpath", "."
    )
    
    # バージョン情報ファイルがあれば追加
    $versionInfoPath = Join-Path $DistPath "version_info.txt"
    if (Test-Path $versionInfoPath) {
        $buildArgs += "--version-file", $versionInfoPath
    }
    
    if ($Debug) {
        $buildArgs += "--debug", "all"
        Write-Host "デバッグモードでビルド" -ForegroundColor Yellow
    }
    
    Write-Host "フォルダ構成モードでビルド（高速起動対応）" -ForegroundColor Green
    
    # PyInstaller実行（Defender対応）
    try {
        Push-Location $DistPath
        
        Write-Host "PyInstaller実行中..." -ForegroundColor Cyan
        Write-Host "コマンド: pyinstaller $($buildArgs -join ' ')" -ForegroundColor Gray
        Write-Host "注意: Windows Defenderによりブロックされる可能性があります" -ForegroundColor Yellow
        
        # PyInstaller実行とエラーハンドリング
        $output = & pyinstaller @buildArgs 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            # Windows Defenderエラーの特定
            $defenderError = $output | Where-Object { $_ -match "ウイルス|virus|threat|blocked|225" }
            if ($defenderError) {
                Write-Host "[ERROR] Windows Defenderによってブロックされました" -ForegroundColor Red
                Write-Host "詳細エラー: $defenderError" -ForegroundColor Red
                Write-Host ""
                Write-Host "解決方法:" -ForegroundColor Cyan
                Write-Host "1. Windows Security → ウイルスと脅威の防止" -ForegroundColor White
                Write-Host "2. 設定の管理 → 除外の追加または削除" -ForegroundColor White
                Write-Host "3. フォルダを追加: $ProjectRoot" -ForegroundColor White
                Write-Host "4. または管理者権限で以下を実行:" -ForegroundColor White
                Write-Host "   Add-MpPreference -ExclusionPath `"$ProjectRoot`"" -ForegroundColor Gray
                throw "Windows Defenderによる実行ブロック"
            } else {
                throw "PyInstaller実行に失敗しました (終了コード: $LASTEXITCODE)"
            }
        }
        
    } catch {
        Write-Host "[ERROR] EXE化に失敗しました: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "PyInstaller出力:" -ForegroundColor Yellow
        $output | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        return $false
    } finally {
        Pop-Location
    }
    
    Write-Host "[OK] EXE化完了（フォルダ構成）" -ForegroundColor Green
    return $true
}

# ビルド後処理
function Complete-Build {
    Write-Host "ビルド後処理を実行中..." -ForegroundColor Yellow
    
    $builtPath = Join-Path $DistPath "TechGate.$Version"
    $exePath = Join-Path $builtPath "TechGate.$Version.exe"
    
    # ビルド成果物の存在確認
    if (-not (Test-Path $exePath)) {
        Write-Host "[ERROR] 生成されたEXEファイルが見つかりません: $exePath" -ForegroundColor Red
        return $false
    }
    
    # ファイルサイズチェック
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Host "EXEファイルサイズ: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    
    # 一時ファイルのクリーンアップ
    $tempPaths = @(
        (Join-Path $DistPath "build")
    )
    
    foreach ($tempPath in $tempPaths) {
        if (Test-Path $tempPath) {
            Remove-Item -Path $tempPath -Recurse -Force
            Write-Host "一時ディレクトリ削除: $tempPath" -ForegroundColor Gray
        }
    }
    
    return $true
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
    
    # バージョン情報ファイル作成
    $versionInfoPath = New-VersionInfo
    
    # EXE化実行
    if (-not (Build-Executable)) {
        exit 1
    }
    
    # ビルド後処理
    if (-not (Complete-Build)) {
        exit 1
    }
    
    # クリーンアップ
    $cleanupFiles = @("*.spec", "version_info.txt")
    foreach ($pattern in $cleanupFiles) {
        Get-ChildItem -Path $DistPath -Name $pattern | ForEach-Object {
            Remove-Item -Path (Join-Path $DistPath $_) -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Host ""
    Write-Host "[SUCCESS] TechGate EXE化ビルド完了！" -ForegroundColor Green
    Write-Host ""
    Write-Host "生成されたファイル:" -ForegroundColor Cyan
    Write-Host "- EXE: $DistPath\TechGate.$Version\TechGate.$Version.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "使用方法:" -ForegroundColor Yellow
    Write-Host "1. TechGate.$Version フォルダ内の EXE を実行" -ForegroundColor White
    Write-Host "2. 各ツールのバージョンが自動検出されます" -ForegroundColor White
    Write-Host "3. 個別起動またはワークフロー実行が可能です" -ForegroundColor White
    Write-Host ""
    Write-Host "完了時刻: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
} catch {
    Write-Host ""
    Write-Host "[ERROR] ビルド中にエラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($Debug) {
        Write-Host "スタックトレース:" -ForegroundColor Red
        Write-Host $_.Exception.StackTrace -ForegroundColor Red
    }
    
    exit 1
}