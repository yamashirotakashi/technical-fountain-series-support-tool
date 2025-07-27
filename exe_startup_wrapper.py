"""EXE起動時の初期設定とエラーハンドリング"""

import sys
import os
import traceback
from pathlib import Path

def setup_exe_environment():
    """EXE環境の初期設定"""
    if getattr(sys, 'frozen', False):
        # EXE環境
        # 作業ディレクトリを実行ファイルのディレクトリに設定
        exe_dir = Path(sys.executable).parent
        os.chdir(exe_dir)
        
        # ユーザー設定ディレクトリの作成
        user_config_dir = Path.home() / '.techzip'
        user_config_dir.mkdir(exist_ok=True)
        
        # ログディレクトリの作成
        log_dir = user_config_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 環境変数の設定（ログ出力先）
        os.environ['TECHZIP_LOG_DIR'] = str(log_dir)

def show_error_dialog(error_msg: str, details: str = None):
    """エラーダイアログを表示"""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        
        if not QApplication.instance():
            app = QApplication(sys.argv)
        
        msg = QMessageBox()
        msg.setWindowTitle("TechZip - エラー")
        msg.setText(error_msg)
        msg.setIcon(QMessageBox.Icon.Critical)
        
        if details:
            msg.setDetailedText(details)
        
        msg.exec()
        
    except Exception:
        # GUI表示に失敗した場合はコンソールに出力
        print(f"エラー: {error_msg}")
        if details:
            print(f"詳細:\n{details}")

def main():
    """メインエントリーポイント"""
    try:
        # EXE環境の初期設定
        setup_exe_environment()
        
        # メインアプリケーションのインポートと実行
        from main import main as app_main
        app_main()
        
    except ImportError as e:
        error_msg = "必要なモジュールの読み込みに失敗しました。"
        details = f"ImportError: {str(e)}\n\n{traceback.format_exc()}"
        show_error_dialog(error_msg, details)
        sys.exit(1)
        
    except FileNotFoundError as e:
        error_msg = "必要なファイルが見つかりません。"
        details = f"FileNotFoundError: {str(e)}\n\n{traceback.format_exc()}"
        show_error_dialog(error_msg, details)
        sys.exit(1)
        
    except Exception as e:
        error_msg = "予期しないエラーが発生しました。"
        details = f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}"
        show_error_dialog(error_msg, details)
        sys.exit(1)

if __name__ == "__main__":
    main()