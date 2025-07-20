# PowerShell Hotkey Removal for TechZip
# ホットキー設定を削除するスクリプト

Write-Host "技術の泉シリーズ制作支援ツール - ホットキー削除" -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Red

# プロファイルファイルのパスを取得
$profilePath = $PROFILE.CurrentUserAllHosts

if (!(Test-Path -Path $profilePath)) {
    Write-Host "プロファイルファイルが存在しません。" -ForegroundColor Yellow
    exit 0
}

# 既存のプロファイルを読み込む
$existingProfile = Get-Content -Path $profilePath -Raw

# ホットキー設定が存在するかチェック
if ($existingProfile -match "TechZip.*Ctrl\+Shift\+i") {
    Write-Host "TechZipのホットキー設定が見つかりました。" -ForegroundColor Yellow
    $response = Read-Host "削除してもよろしいですか？ (Y/N)"
    
    if ($response -eq 'Y' -or $response -eq 'y') {
        # 設定を削除（複数行にまたがる設定を削除）
        $newProfile = $existingProfile -replace "(?ms)# TechZip.*?InvokePrompt\(\)\s*\}\s*", ""
        
        # 空行を整理
        $newProfile = $newProfile -replace "(\r?\n){3,}", "`n`n"
        
        # プロファイルに書き込む
        Set-Content -Path $profilePath -Value $newProfile.TrimEnd() -Encoding UTF8
        
        Write-Host "`n✅ ホットキー設定を削除しました！" -ForegroundColor Green
        Write-Host "PowerShellを再起動するか、以下のコマンドを実行してください:" -ForegroundColor Yellow
        Write-Host ". `$PROFILE" -ForegroundColor White
    } else {
        Write-Host "削除をキャンセルしました。" -ForegroundColor Red
    }
} else {
    Write-Host "TechZipのホットキー設定は見つかりませんでした。" -ForegroundColor Yellow
}