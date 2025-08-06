#!/usr/bin/env python3
"""
ハードコーディング検知システムのデモンストレーション

このスクリプトは以下を実行します：
1. HardcodingDetectorクラスのテスト
2. 主要ファイルのハードコーディングスキャン
3. ConfigManagerの設定検証
4. 修正提案の表示
"""

import sys
import os
from pathlib import Path

# プロジェクトルートを追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.slack_pdf_poster import HardcodingDetector, ConfigManager
    print("✅ ConfigManager インポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    sys.exit(1)

def main():
    """ハードコーディング検知デモのメイン実行"""
    
    print("="*60)
    print("🔍 TECHZIP ハードコーディング検知システム デモ")
    print("="*60)
    
    # 1. ConfigManagerのテスト
    print("\n1️⃣ ConfigManager テスト")
    print("-" * 30)
    
    try:
        config_manager = ConfigManager()
        print("✅ ConfigManager 初期化成功")
        
        # 設定検証
        validation_results = config_manager.validate_config()
        print(f"📊 設定検証結果:")
        print(f"   エラー: {len(validation_results['errors'])}")
        print(f"   警告: {len(validation_results['warnings'])}")
        print(f"   不足環境変数: {len(validation_results['missing_env_vars'])}")
        
        if validation_results['errors']:
            print("❌ 設定エラー:")
            for error in validation_results['errors']:
                print(f"   - {error}")
        
        if validation_results['warnings']:
            print("⚠️ 設定警告:")
            for warning in validation_results['warnings']:
                print(f"   - {warning}")
                
    except Exception as e:
        print(f"❌ ConfigManager エラー: {e}")
    
    # 2. ハードコーディング検知テスト
    print("\n2️⃣ ハードコーディング検知テスト")
    print("-" * 30)
    
    # スキャン対象ファイル
    scan_targets = [
        "src/slack_pdf_poster.py",
        "services/error_check_validator.py", 
        "core/api_processor.py",
        "services/nextpublishing_service.py",
        "core/preflight/word2xhtml_scraper.py"
    ]
    
    total_hardcoded_items = 0
    
    for target_file in scan_targets:
        file_path = project_root / target_file
        
        if not file_path.exists():
            print(f"⚠️ ファイルが見つかりません: {target_file}")
            continue
            
        print(f"\n📄 スキャン中: {target_file}")
        
        try:
            detected = HardcodingDetector.scan_hardcoding(str(file_path))
            
            file_total = sum(len(items) for items in detected.values())
            total_hardcoded_items += file_total
            
            if file_total == 0:
                print("   ✅ ハードコーディングなし")
            else:
                print(f"   🔍 検出: {file_total}個のハードコーディング")
                
                for category, items in detected.items():
                    if items:
                        print(f"   📁 {category}: {len(items)}個")
                        for item in items[:3]:  # 最初の3個のみ表示
                            print(f"      - {item}")
                        if len(items) > 3:
                            print(f"      - ... 他{len(items)-3}個")
                            
        except Exception as e:
            print(f"   ❌ スキャンエラー: {e}")
    
    # 3. 修正提案
    print(f"\n3️⃣ 修正提案")
    print("-" * 30)
    print(f"📊 総計: {total_hardcoded_items}個のハードコーディングを検出")
    
    if total_hardcoded_items > 0:
        print("\n💡 推奨対応:")
        print("1. .env.template を参考に .env ファイルを作成")
        print("2. ハードコーディングされた値を環境変数に移行")
        print("3. ConfigManager を使用して設定値を取得するよう修正")
        print("4. config/techzip_config.yaml で詳細設定を管理")
        
        print("\n🔧 修正例:")
        print("   修正前: base_path = Path('G:/.shortcut-targets-by-id/...')")
        print("   修正後: base_path = Path(config_manager.get('paths.base_repository_path'))")
        
    else:
        print("✅ 全ファイルがハードコーディングフリーです！")
    
    # 4. 設定情報表示
    print(f"\n4️⃣ 現在の設定情報")
    print("-" * 30)
    
    try:
        config_manager = ConfigManager()
        
        print("📁 パス設定:")
        paths = config_manager.get_path_config()
        for key, value in paths.items():
            print(f"   {key}: {value}")
        
        print("\n🔗 API設定:")
        nextpub_config = config_manager.get_api_config('nextpublishing')
        print(f"   NextPublishing URL: {nextpub_config.get('base_url', 'N/A')}")
        print(f"   タイムアウト: {nextpub_config.get('timeout', 'N/A')}秒")
        
        slack_config = config_manager.get_api_config('slack')
        print(f"   Slack Token: {'設定済み' if slack_config.get('bot_token') else '未設定'}")
        
    except Exception as e:
        print(f"❌ 設定情報取得エラー: {e}")
    
    print("\n" + "="*60)
    print("🎉 ハードコーディング検知システム デモ完了")
    print("="*60)

if __name__ == "__main__":
    main()