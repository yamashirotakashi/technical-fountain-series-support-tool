@echo off
cd /d "%~dp0"
echo 技術の泉シリーズ制作支援ツールを起動しています...

REM 仮想環境が存在する場合は有効化
if exist venv_windows (
    call venv_windows\Scripts\activate.bat
    python main.py
) else (
    echo エラー: 仮想環境が見つかりません
    echo setup_windows.batを先に実行してください
)
pause