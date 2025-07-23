@echo off
setlocal

echo ReVIEW API テスト実行スクリプト
echo ===============================
echo.

:: テストケースを選択
if "%1"=="" (
    echo 使用方法: test_review_api.bat [success^|partial^|failure^|all]
    echo.
    echo   success - 成功ケーステスト（警告なし）
    echo   partial - 一部成功ケーステスト（警告あり）
    echo   failure - 失敗ケーステスト
    echo   all     - 全てのケースをテスト
    echo.
    exit /b 1
)

:: Python環境を有効化
call venv_windows\Scripts\activate.bat

:: テスト実行
if /i "%1"=="all" (
    echo === 成功ケーステスト ===
    python tests\test_api_workflow.py success
    echo.
    echo === 一部成功ケーステスト ===
    python tests\test_api_workflow.py partial
    echo.
    echo === 失敗ケーステスト ===
    python tests\test_api_workflow.py failure
) else (
    python tests\test_api_workflow.py %1
)

echo.
echo テスト完了
pause