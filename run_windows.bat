@echo off
cd /d "%~dp0"
echo 技術の泉シリーズ制作支援ツールを起動しています...

REM 仮想環境が存在する場合は有効化
if exist venv_windows (
    call venv_windows\Scripts\activate.bat
    
    REM 仮想環境のPythonを明示的に使用
    if exist venv_windows\Scripts\python.exe (
        echo 仮想環境のPythonを使用します
        venv_windows\Scripts\python.exe main.py
    ) else (
        echo 警告: 仮想環境のPythonが見つかりません。システムのPythonを使用します。
        python.exe main.py
    )
    
    REM 仮想環境から抜ける
    call deactivate
) else (
    echo エラー: 仮想環境が見つかりません
    echo setup_windows.batを先に実行してください
)
pause