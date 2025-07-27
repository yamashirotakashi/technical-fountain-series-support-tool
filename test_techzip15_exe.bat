@echo off
echo === TECHZIP1.5.exe 設定機能テスト ===
echo.
cd /d "/mnt/c/Users/tky99/dev/technical-fountain-series-support-tool"
echo 現在のディレクトリ: %CD%
echo.
echo EXEを起動します...
start "" "dist\TECHZIP1.5.exe"
echo.
echo アプリケーションが起動したら:
echo 1. メニューバー ^> ツール ^> 設定 を選択
echo 2. 各種設定を確認・変更
echo 3. 保存後、%%USERPROFILE%%\.techzip を確認
echo.
pause
