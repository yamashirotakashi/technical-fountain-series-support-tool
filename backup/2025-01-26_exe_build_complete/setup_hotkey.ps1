# PowerShell Hotkey Setup for TechZip
# Ctrl+Shift+I でアプリを起動するスクリプト

Write-Host "技術の泉シリーズ制作支援ツール - ホットキー設定" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# PSReadLineモジュールがインストールされているか確認
if (!(Get-Module -ListAvailable -Name PSReadLine)) {
    Write-Host "PSReadLineモジュールがインストールされていません。" -ForegroundColor Red
    Write-Host "以下のコマンドでインストールしてください:" -ForegroundColor Yellow
    Write-Host "Install-Module -Name PSReadLine -Force -SkipPublisherCheck" -ForegroundColor Green
    exit 1
}

# プロファイルファイルのパスを取得
$profilePath = $PROFILE.CurrentUserAllHosts
$profileDir = Split-Path -Parent $profilePath

# プロファイルディレクトリが存在しない場合は作成
if (!(Test-Path -Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    Write-Host "プロファイルディレクトリを作成しました: $profileDir" -ForegroundColor Green
}

# ホットキー設定のコード
$hotkeyCode = @'

# TechZip - 技術の泉シリーズ制作支援ツール起動 (Ctrl+Shift+I)
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

'@

# 既存のプロファイルを読み込む
$existingProfile = ""
if (Test-Path -Path $profilePath) {
    $existingProfile = Get-Content -Path $profilePath -Raw
}

# ホットキー設定が既に存在するかチェック
if ($existingProfile -match "TechZip.*Ctrl\+Shift\+i") {
    Write-Host "ホットキー設定は既に存在します。" -ForegroundColor Yellow
    $response = Read-Host "上書きしますか？ (Y/N)"
    if ($response -ne 'Y' -and $response -ne 'y') {
        Write-Host "設定をキャンセルしました。" -ForegroundColor Red
        exit 0
    }
    # 既存の設定を削除
    $existingProfile = $existingProfile -replace "(?ms)# TechZip.*?InvokePrompt\(\)\s*\}", ""
}

# 新しい設定を追加
$newProfile = $existingProfile.TrimEnd() + "`n`n" + $hotkeyCode

# プロファイルに書き込む
Set-Content -Path $profilePath -Value $newProfile -Encoding UTF8

Write-Host "`n✅ ホットキー設定が完了しました！" -ForegroundColor Green
Write-Host "`n使用方法:" -ForegroundColor Cyan
Write-Host "  1. PowerShellを再起動するか、以下のコマンドを実行:" -ForegroundColor White
Write-Host "     . `$PROFILE" -ForegroundColor Yellow
Write-Host "  2. Ctrl+Shift+I を押すとアプリが起動します" -ForegroundColor White
Write-Host "`n現在のプロファイルパス: $profilePath" -ForegroundColor Gray