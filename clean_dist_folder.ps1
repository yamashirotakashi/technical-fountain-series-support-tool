# distフォルダのクリーンアップ - 標準規則に準拠

Write-Host "=== Clean Dist Folder ===" -ForegroundColor Cyan

$distPath = "C:\Users\tky99\DEV\technical-fountain-series-support-tool\dist"

# 保持すべきファイル（ビルドスクリプトのみ）
$keepFiles = @(
    "PJinit.build.ps1",
    "TECHZIP.build.ps1",
    "TECHZIP.1.7.build.ps1",
    "OverflowChecker.build.ps1",
    "TechBridge_Unified_Launcher.build.ps1"
)

Write-Host "`nKeeping build scripts:" -ForegroundColor Green
$keepFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }

Write-Host "`nRemoving test and temporary scripts..." -ForegroundColor Yellow

# すべての.ps1ファイルを取得
Get-ChildItem -Path $distPath -Filter "*.ps1" | ForEach-Object {
    if ($keepFiles -notcontains $_.Name) {
        Remove-Item -Path $_.FullName -Force
        Write-Host "  Removed: $($_.Name)" -ForegroundColor Red
    }
}

# 一時的なログファイルも削除
Get-ChildItem -Path $distPath -Filter "*.log" | ForEach-Object {
    Remove-Item -Path $_.FullName -Force
    Write-Host "  Removed: $($_.Name)" -ForegroundColor Red
}

# toolsディレクトリが存在する場合は削除
$toolsDir = "$distPath\tools"
if (Test-Path $toolsDir) {
    Remove-Item -Path $toolsDir -Recurse -Force
    Write-Host "  Removed: tools directory" -ForegroundColor Red
}

Write-Host "`nCleanup complete!" -ForegroundColor Green
Write-Host "`nDist folder now contains:" -ForegroundColor Cyan
Get-ChildItem -Path $distPath | Select-Object Name, @{Name="Type";Expression={if($_.PSIsContainer){"Directory"}else{"File"}}} | Format-Table -AutoSize