# 古いビルドスクリプトのクリーンアップ

Write-Host "=== Cleanup Old Build Scripts ===" -ForegroundColor Cyan

# 削除対象
$filesToRemove = @(
    "C:\Users\tky99\DEV\technical-fountain-series-support-tool\tools\project_initializer\build.ps1",
    "C:\Users\tky99\DEV\technical-fountain-series-support-tool\clean_and_rebuild.ps1",
    "C:\Users\tky99\DEV\technical-fountain-series-support-tool\rebuild_now.ps1",
    "C:\Users\tky99\DEV\technical-fountain-series-support-tool\migrate_project_properly.ps1",
    "C:\Users\tky99\DEV\technical-fountain-series-support-tool\app"  # 不適切な場所
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed: $file" -ForegroundColor Red
    }
}

Write-Host "`nCleanup complete!" -ForegroundColor Green
Write-Host "`nCorrect build script location:" -ForegroundColor Cyan
Write-Host "  C:\Users\tky99\DEV\technical-fountain-series-support-tool\dist\PJinit.build.ps1" -ForegroundColor White