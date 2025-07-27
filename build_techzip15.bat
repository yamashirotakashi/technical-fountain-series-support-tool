@echo off
echo === TECHZIP1.5.exe ビルド開始 ===
echo.

REM 仮想環境をアクティベート
echo 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

REM PyInstallerでEXEビルド
echo.
echo PyInstallerでビルド中...
pyinstaller techzip_windows.spec --clean --noconfirm

REM ビルド結果の確認
echo.
echo === ビルド結果確認 ===
if exist "dist\TECHZIP1.5\TECHZIP1.5.exe" (
    echo ✅ ビルド成功！
    echo.
    echo 出力場所: %CD%\dist\TECHZIP1.5\TECHZIP1.5.exe
    dir "dist\TECHZIP1.5\TECHZIP1.5.exe"
    echo.
    echo 📁 ディストリビューション内容:
    dir /s "dist\TECHZIP1.5" | findstr /v "ディレクトリ"
) else (
    echo ❌ ビルド失敗
    echo dist\TECHZIP1.5\TECHZIP1.5.exe が見つかりません
)

echo.
echo === ビルド完了 ===
pause