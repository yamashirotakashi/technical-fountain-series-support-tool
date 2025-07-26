@echo off
cd /d "%~dp0"
echo 技術の泉シリーズ制作支援ツールを起動しています...
echo ネイティブ・グローバル環境で実行します

REM システムのPythonを直接使用（exe化対応）
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python環境を確認中...
    python --version
    echo アプリケーションを起動します
    python main.py
) else (
    REM フォールバック: python.exeを試行
    python.exe --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Python環境を確認中...
        python.exe --version
        echo アプリケーションを起動します
        python.exe main.py
    ) else (
        echo エラー: Pythonが見つかりません
        echo Pythonがグローバル環境にインストールされていることを確認してください
        echo 必要なパッケージもpip install -r requirements.txtでインストールしてください
    )
)
pause