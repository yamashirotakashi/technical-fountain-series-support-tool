# Quick Launch Script for TechZip
# 一時的なホットキー設定（現在のセッションのみ有効）

Write-Host "`n🎯 TechZip クイック起動設定 (現在のセッションのみ)" -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta

# PSReadLineモジュールの確認
if (!(Get-Module PSReadLine)) {
    Import-Module PSReadLine -ErrorAction SilentlyContinue
    if (!$?) {
        Write-Host "❌ PSReadLineモジュールが利用できません" -ForegroundColor Red
        exit 1
    }
}

# ホットキー設定
Set-PSReadLineKeyHandler -Chord 'Ctrl+Shift+i' -ScriptBlock {
    $currentPath = Get-Location
    $techzipPath = "C:\Users\tky99\DEV\technical-fountain-series-support-tool"
    
    # 現在のコマンドラインをクリア
    [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
    
    # アプリ起動メッセージを表示
    Write-Host "`n🚀 技術の泉シリーズ制作支援ツールを起動しています..." -ForegroundColor Cyan
    
    # アプリのディレクトリに移動して起動
    Set-Location $techzipPath
    
    # 新しいウィンドウでアプリを起動
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "& '.\run_windows.ps1'" -WorkingDirectory $techzipPath
    
    # 元のディレクトリに戻る
    Set-Location $currentPath
    
    # 起動完了メッセージ
    Write-Host "✅ アプリケーションを新しいウィンドウで起動しました" -ForegroundColor Green
    Write-Host ""
    
    # プロンプトを再描画
    [Microsoft.PowerShell.PSConsoleReadLine]::InvokePrompt()
}

Write-Host "`n✅ ホットキー設定完了！" -ForegroundColor Green
Write-Host "📌 Ctrl+Shift+I でTechZipを起動できます" -ForegroundColor Cyan
Write-Host "⚠️  この設定は現在のPowerShellウィンドウでのみ有効です" -ForegroundColor Yellow
Write-Host ""