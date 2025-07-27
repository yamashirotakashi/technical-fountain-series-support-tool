@echo off
echo === Python環境修正とPyInstaller実行 ===
echo.

REM 現在の環境を確認
echo 1. 現在のPython環境をチェック...
where python
where pip
echo.

echo 2. PATH環境変数をチェック...
echo PATH=%PATH%
echo.

echo 3. 仮想環境のアクティベート...
call venv\Scripts\activate.bat

echo 4. アクティベート後のPython環境をチェック...
where python
where pip
python --version
echo.

echo 5. PyInstallerの確認とインストール...
pip show pyinstaller
if %ERRORLEVEL% neq 0 (
    echo PyInstallerが見つからないため、インストールします...
    pip install pyinstaller
)
echo.

echo 6. PyInstallerバージョン確認...
pyinstaller --version
echo.

echo 7. TECHZIP1.5.exeのビルド開始...
echo 使用するPython: 
python -c "import sys; print(sys.executable)"
echo.

echo PyInstallerでビルド実行...
pyinstaller techzip_windows.spec --clean --noconfirm --log-level=INFO

echo.
echo === ビルド完了確認 ===
if exist "dist\TECHZIP1.5\TECHZIP1.5.exe" (
    echo ✅ ビルド成功！
    echo 出力場所: %CD%\dist\TECHZIP1.5\TECHZIP1.5.exe
    dir "dist\TECHZIP1.5\TECHZIP1.5.exe"
) else (
    echo ❌ ビルド失敗
    echo dist\TECHZIP1.5\TECHZIP1.5.exe が見つかりません
    echo.
    echo ディレクトリ構造を確認:
    if exist "dist" (
        dir /s "dist"
    ) else (
        echo distディレクトリが存在しません
    )
)

pause