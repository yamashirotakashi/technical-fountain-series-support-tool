@echo off
REM WSL PATH汚染の根本的解決 - Windows実行用バッチファイル
REM 管理者権限での実行を推奨

echo ==============================================
echo WSL PATH汚染の根本的解決
echo ==============================================
echo.

REM 現在のディレクトリを確認
echo 現在のディレクトリ: %CD%
echo.

REM PowerShell実行ポリシー確認
echo PowerShell実行ポリシーを確認中...
powershell -Command "Get-ExecutionPolicy"
echo.

REM 解決スクリプト実行
echo WSL汚染解決スクリプトを実行します...
echo (この処理には数分かかる場合があります)
echo.

powershell -ExecutionPolicy Bypass -File "fix_wsl_contamination.ps1"

REM 結果確認
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ WSL汚染解決が完了しました
    echo.
    echo 次のステップ:
    echo   1. run_windows.ps1 でアプリケーションテスト
    echo   2. build_exe.ps1 でEXE化実行
    echo.
) else (
    echo.
    echo ❌ WSL汚染解決でエラーが発生しました
    echo.
    echo 対処方法:
    echo   1. 管理者権限でコマンドプロンプトを起動
    echo   2. このバッチファイルを再実行
    echo   3. または手動でPowerShellスクリプトを実行:
    echo      powershell -ExecutionPolicy Bypass -File fix_wsl_contamination.ps1 -Force
    echo.
)

pause