@echo off
cd /d "%~dp0"
echo Python仮想環境をセットアップしています...

REM 仮想環境を作成
python -m venv venv_windows

REM 仮想環境を有効化
call venv_windows\Scripts\activate.bat

REM 依存関係をインストール
echo 依存関係をインストールしています...
pip install -r requirements.txt

echo セットアップが完了しました！
echo run_windows.batを実行してアプリケーションを起動してください。
pause