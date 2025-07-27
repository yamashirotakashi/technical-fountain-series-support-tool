# TECHZIPプロセスを強制終了するスクリプト

Write-Host "=== TECHZIP プロセス強制終了 ===" -ForegroundColor Red
Write-Host ""

# 管理者権限の確認
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️ 管理者権限で実行することを推奨します" -ForegroundColor Yellow
}

# TECHZIPプロセスを検索
$processes = Get-Process | Where-Object { 
    $_.Name -like "*TECHZIP*" -or 
    $_.ProcessName -like "*TECHZIP*" -or
    $_.MainWindowTitle -like "*技術の泉*"
}

if ($processes) {
    Write-Host "以下のプロセスを終了します:" -ForegroundColor Yellow
    foreach ($proc in $processes) {
        Write-Host "  - $($proc.Name) (PID: $($proc.Id))" -ForegroundColor Red
    }
    
    Write-Host ""
    $response = Read-Host "本当に終了しますか？ (y/n)"
    
    if ($response -eq 'y') {
        foreach ($proc in $processes) {
            try {
                $proc | Stop-Process -Force -ErrorAction Stop
                Write-Host "✓ PID $($proc.Id) を終了しました" -ForegroundColor Green
            } catch {
                Write-Host "✗ PID $($proc.Id) の終了に失敗: $_" -ForegroundColor Red
                
                # WMIを使用した強制終了を試みる
                try {
                    $result = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)").Terminate()
                    if ($result.ReturnValue -eq 0) {
                        Write-Host "✓ WMI経由でPID $($proc.Id) を終了しました" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "✗ WMI経由でも終了できませんでした" -ForegroundColor Red
                }
            }
        }
    }
} else {
    Write-Host "実行中のTECHZIPプロセスはありません" -ForegroundColor Green
}

# EXEファイルのロック確認
Write-Host ""
Write-Host "EXEファイルのロック状態を確認中..." -ForegroundColor Yellow
$exePath = ".\dist\TECHZIP1.5.exe"

if (Test-Path $exePath) {
    try {
        # ファイルを開いてみてロックを確認
        $file = [System.IO.File]::Open($exePath, 'Open', 'ReadWrite', 'None')
        $file.Close()
        Write-Host "✓ EXEファイルはロックされていません" -ForegroundColor Green
    } catch {
        Write-Host "✗ EXEファイルがロックされています" -ForegroundColor Red
        Write-Host "  タスクマネージャーで関連プロセスを確認してください" -ForegroundColor Yellow
        
        # handle.exeがある場合は使用（SysInternals）
        if (Get-Command handle -ErrorAction SilentlyContinue) {
            Write-Host ""
            Write-Host "ファイルをロックしているプロセスを検索中..." -ForegroundColor Yellow
            handle $exePath
        }
    }
}

Write-Host ""
Write-Host "完了しました。" -ForegroundColor Cyan