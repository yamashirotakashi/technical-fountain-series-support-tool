
import sys
from PyQt6.QtWidgets import QApplication
from pathlib import Path
import time

# EXE環境をシミュレート
sys._MEIPASS = str(Path(__file__).parent)

# パスを通す
sys.path.insert(0, str(Path(__file__).parent))

print("🔧 設定ダイアログテスト開始...")

try:
    from utils.path_resolver import PathResolver
    from utils.env_manager import EnvManager
    from gui.comprehensive_settings_dialog import ComprehensiveSettingsDialog
    
    # 環境初期化
    EnvManager.initialize()
    
    print(f"実行環境: {'EXE' if PathResolver.is_exe_environment() else '開発環境'}")
    print(f"ユーザーディレクトリ: {PathResolver.get_user_dir()}")
    
    # 設定ダイアログを開く
    app = QApplication(sys.argv)
    dialog = ComprehensiveSettingsDialog()
    
    # 現在の認証情報状態を表示
    creds_info = EnvManager.get_credentials_info()
    print("\n認証情報の状態:")
    for key, value in creds_info.items():
        print(f"  {key}: {'✓ 設定済み' if value else '✗ 未設定'}")
    
    print("\n✅ 設定ダイアログ作成成功")
    print("ダイアログを閉じてテスト終了...")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()
