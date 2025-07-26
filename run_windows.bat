@echo off
cd /d "%~dp0"
echo 技術の泉シリーズ制作支援ツールを起動しています...

REM 仮想環境のPythonを直接実行
if exist venv_windows\Scripts\python.exe (
    echo 仮想環境のPythonを使用します
    
    REM PYTHONPATH を設定（仮想環境のライブラリを優先）
    set PYTHONPATH=%~dp0venv_windows\Lib\site-packages
    
    REM 仮想環境のPythonを直接実行（activateスクリプトを使わない）
    venv_windows\Scripts\python.exe main.py
) else if exist venv_windows (
    echo 警告: 仮想環境のPythonが見つかりません。システムのPythonを使用します。
    python.exe main.py
) else (
    echo エラー: 仮想環境が見つかりません
    echo setup_windows.batを先に実行してください
)
pause