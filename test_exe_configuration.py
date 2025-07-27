"""TECHZIP1.5.exe設定機能の動作テスト"""

import os
import sys
import subprocess
from pathlib import Path
import time
import json

def test_exe_settings():
    """EXE実行環境での設定機能テスト"""
    
    exe_path = Path("dist/TECHZIP1.5.exe")
    
    if not exe_path.exists():
        print(f"❌ EXEファイルが見つかりません: {exe_path}")
        return False
        
    print(f"✅ EXEファイル確認: {exe_path}")
    print(f"   サイズ: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    # ユーザーディレクトリの確認
    user_dir = Path.home() / '.techzip'
    print(f"\n📁 ユーザーディレクトリ確認: {user_dir}")
    
    if user_dir.exists():
        print("   ✅ ディレクトリが存在します")
        
        # 既存の設定ファイルを確認
        env_file = user_dir / '.env'
        if env_file.exists():
            print(f"   ✅ .envファイル存在: {env_file}")
            
        config_dir = user_dir / 'config'
        if config_dir.exists():
            print(f"   ✅ configディレクトリ存在: {config_dir}")
            
            settings_file = config_dir / 'settings.json'
            if settings_file.exists():
                print(f"   ✅ settings.json存在: {settings_file}")
                
                # 設定内容を確認
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                        print("   📄 settings.json内容:")
                        for key, value in settings.items():
                            print(f"      - {key}: {type(value).__name__}")
                except Exception as e:
                    print(f"   ⚠️ settings.json読み込みエラー: {e}")
                    
    else:
        print("   ⚠️ ユーザーディレクトリが存在しません（初回起動時に作成されます）")
    
    # EXE実行テスト用のヘルパースクリプト作成
    test_script = Path("test_exe_settings_helper.py")
    test_script.write_text("""
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
    print("\\n認証情報の状態:")
    for key, value in creds_info.items():
        print(f"  {key}: {'✓ 設定済み' if value else '✗ 未設定'}")
    
    print("\\n✅ 設定ダイアログ作成成功")
    print("ダイアログを閉じてテスト終了...")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()
""", encoding='utf-8')
    
    print("\n🚀 EXE動作テストを実行します...")
    print("=" * 50)
    
    # 実際のEXEは別プロセスで起動する必要があるため、ここでは準備のみ
    print("\n📝 EXEテスト手順:")
    print("1. PowerShellまたはコマンドプロンプトで以下を実行:")
    print(f"   cd {Path.cwd()}")
    print(f"   .\\dist\\TECHZIP1.5.exe")
    print("\n2. アプリケーションが起動したら:")
    print("   - メニューバー > ツール > 設定 を選択")
    print("   - 設定ダイアログが開くことを確認")
    print("   - 各タブの内容を確認:")
    print("     - 基本設定: Gmail、ディレクトリ設定")
    print("     - Google API: Sheets、OAuth設定")
    print("     - Slack連携: Bot Token設定")
    print("     - 詳細設定: NextPublishing、デバッグ設定")
    print("     - 環境情報: 実行環境の詳細情報")
    print("\n3. 設定を変更して保存:")
    print("   - 適当な値を入力してOKボタンをクリック")
    print("   - %USERPROFILE%\\.techzip\\.env が作成/更新されることを確認")
    
    # テスト用バッチファイル作成
    batch_file = Path("test_techzip15_exe.bat")
    batch_file.write_text(f"""@echo off
echo === TECHZIP1.5.exe 設定機能テスト ===
echo.
cd /d "{Path.cwd()}"
echo 現在のディレクトリ: %CD%
echo.
echo EXEを起動します...
start "" "dist\\TECHZIP1.5.exe"
echo.
echo アプリケーションが起動したら:
echo 1. メニューバー ^> ツール ^> 設定 を選択
echo 2. 各種設定を確認・変更
echo 3. 保存後、%%USERPROFILE%%\\.techzip を確認
echo.
pause
""", encoding='cp932')
    
    print(f"\n✅ テスト用バッチファイル作成: {batch_file}")
    print("   このバッチファイルをダブルクリックしてEXEをテストできます")
    
    return True

if __name__ == "__main__":
    print("TECHZIP1.5.exe 設定機能テスト")
    print("=" * 60)
    
    success = test_exe_settings()
    
    if success:
        print("\n✅ テスト準備完了")
    else:
        print("\n❌ テスト準備失敗")