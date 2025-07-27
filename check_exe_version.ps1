# EXEファイルのバージョンとビルド情報を確認

Write-Host "=== TECHZIP EXEファイル情報 ===" -ForegroundColor Cyan
Write-Host ""

$exePath = ".\dist\TECHZIP1.5.exe"

if (Test-Path $exePath) {
    $exeInfo = Get-Item $exePath
    
    Write-Host "1. ファイル情報:" -ForegroundColor Yellow
    Write-Host "   パス: $($exeInfo.FullName)"
    Write-Host "   サイズ: $([math]::Round($exeInfo.Length / 1MB, 2)) MB"
    Write-Host "   作成日時: $($exeInfo.CreationTime)"
    Write-Host "   更新日時: $($exeInfo.LastWriteTime)" -ForegroundColor Cyan
    
    # ファイルバージョン情報
    Write-Host ""
    Write-Host "2. バージョン情報:" -ForegroundColor Yellow
    $versionInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($exePath)
    Write-Host "   ファイルバージョン: $($versionInfo.FileVersion)"
    Write-Host "   製品バージョン: $($versionInfo.ProductVersion)"
    Write-Host "   製品名: $($versionInfo.ProductName)"
    Write-Host "   会社名: $($versionInfo.CompanyName)"
    
    # 関連ファイルの確認
    Write-Host ""
    Write-Host "3. 関連ファイル:" -ForegroundColor Yellow
    
    # runtime_hook_enhanced.pyの確認
    $hookFile = ".\runtime_hook_enhanced.py"
    if (Test-Path $hookFile) {
        $hookInfo = Get-Item $hookFile
        Write-Host "   runtime_hook_enhanced.py:"
        Write-Host "     更新日時: $($hookInfo.LastWriteTime)"
        
        # EXEよりも新しいか確認
        if ($hookInfo.LastWriteTime -gt $exeInfo.LastWriteTime) {
            Write-Host "     ⚠️ EXEよりも新しいです！再ビルドが必要" -ForegroundColor Red
        } else {
            Write-Host "     ✓ EXEに含まれています" -ForegroundColor Green
        }
    }
    
    # utils/config.pyの確認
    $configFile = ".\utils\config.py"
    if (Test-Path $configFile) {
        $configInfo = Get-Item $configFile
        Write-Host "   utils\config.py:"
        Write-Host "     更新日時: $($configInfo.LastWriteTime)"
        
        if ($configInfo.LastWriteTime -gt $exeInfo.LastWriteTime) {
            Write-Host "     ⚠️ EXEよりも新しいです！再ビルドが必要" -ForegroundColor Red
        } else {
            Write-Host "     ✓ EXEに含まれています" -ForegroundColor Green
        }
    }
    
    # specファイルの確認
    Write-Host ""
    Write-Host "4. ビルド設定ファイル:" -ForegroundColor Yellow
    $specFiles = Get-ChildItem -Filter "*.spec" | Sort-Object LastWriteTime -Descending
    foreach ($spec in $specFiles) {
        Write-Host "   $($spec.Name):"
        Write-Host "     更新日時: $($spec.LastWriteTime)"
    }
    
    # ビルドの必要性判定
    Write-Host ""
    Write-Host "5. 判定結果:" -ForegroundColor Yellow
    
    $needsRebuild = $false
    $criticalFiles = @(
        ".\runtime_hook_enhanced.py",
        ".\utils\config.py",
        ".\utils\path_resolver.py",
        ".\utils\startup_logger.py"
    )
    
    foreach ($file in $criticalFiles) {
        if (Test-Path $file) {
            $fileInfo = Get-Item $file
            if ($fileInfo.LastWriteTime -gt $exeInfo.LastWriteTime) {
                $needsRebuild = $true
                break
            }
        }
    }
    
    if ($needsRebuild) {
        Write-Host "   ⚠️ 再ビルドが必要です" -ForegroundColor Red
        Write-Host "   最新の修正がEXEに反映されていません" -ForegroundColor Red
        Write-Host ""
        Write-Host "   推奨コマンド:" -ForegroundColor Yellow
        Write-Host "   pyinstaller techzip15_proven.spec --clean" -ForegroundColor Cyan
    } else {
        Write-Host "   ✓ EXEは最新です" -ForegroundColor Green
    }
    
} else {
    Write-Host "EXEファイルが見つかりません: $exePath" -ForegroundColor Red
}

Write-Host ""
Write-Host "確認完了。" -ForegroundColor Cyan
pause