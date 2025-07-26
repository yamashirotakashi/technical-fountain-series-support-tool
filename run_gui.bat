@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================================
echo   TechZip Pre-flight Checker - 統合テストGUI起動
echo ================================================================
echo.

:: Pythonインストール確認
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [エラー]Pythonがインストールされていません
    echo Python 3.8以降をインストールしてください
    pause
    exit /b 1
)

echo ✓ Python環境確認済み
for /f "tokens=*" %%a in ('python --version') do set PYTHON_VERSION=%%a
echo   %PYTHON_VERSION%
echo.

:: 作業ディレクトリの確認
if not exist "main_gui.py" (
    echo [エラー]main_gui.pyが見つかりません
    echo プロジェクトルートディレクトリで実行してください
    pause
    exit /b 1
)

echo ✓ プロジェクトルート確認済み
echo.

:: 仮想環境の確認と有効化（オプション）
if exist "venv\Scripts\activate.bat" (
    echo 仮想環境を検出しました。使用しますか？
    set /p use_venv="仮想環境を使用する (y/N): "
    if /i "!use_venv!"=="y" (
        echo 仮想環境を有効化中...
        call venv\Scripts\activate.bat
        echo ✓ 仮想環境有効化完了
    )
) else (
    echo 仮想環境が見つかりません。システムPythonを使用します。
)
echo.

:: 依存関係の確認
echo 依存関係チェック中...
python -c "import tkinter; import psutil; import dotenv; import requests" 2>nul
if %errorLevel% neq 0 (
    echo [警告]一部の依存関係が不足している可能性があります
    echo 依存関係をインストールしますか？
    set /p install_deps="依存関係をインストールする (y/N): "
    if /i "!install_deps!"=="y" (
        echo 依存関係をインストール中...
        pip install -r requirements.txt
        if %errorLevel% neq 0 (
            echo [エラー]依存関係のインストールに失敗しました
            pause
            exit /b 1
        )
        echo ✓ 依存関係インストール完了
    )
) else (
    echo ✓ 依存関係確認済み
)
echo.

:: GUI起動
echo 統合テストGUIを起動中...
echo.
echo ================================================================
echo   使用方法:
echo   1. 環境チェック - システム環境と依存関係を確認
echo   2. ファイル選択 - テスト対象のDOCXファイルを選択
echo   3. 設定調整 - 検証モードとメール設定を確認
echo   4. テスト実行 - 完全テストスイートを実行
echo ================================================================
echo.

python main_gui.py

if %errorLevel% neq 0 (
    echo.
    echo [エラー]GUIアプリケーションの起動に失敗しました
    echo エラー詳細を確認して、必要に応じて依存関係を再インストールしてください
    pause
    exit /b 1
)

echo.
echo GUI起動完了
pause