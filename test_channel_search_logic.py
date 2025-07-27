#!/usr/bin/env python3
"""
チャネル検索ロジックの詳細テスト
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.slack_pdf_poster import SlackPDFPoster

def test_channel_search_logic():
    """チャネル検索ロジックの詳細テスト"""
    
    # 環境変数の確認
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    if not slack_token:
        print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
        return
    
    print("=== チャネル検索ロジック詳細テスト ===")
    print(f"Bot Token: {slack_token[:10]}...")
    
    try:
        # SlackPDFPosterを初期化
        poster = SlackPDFPoster()
        
        print("\n1. N01798の検索テスト:")
        
        # 実際のfind_slack_channel()を呼び出し
        result = poster.find_slack_channel("N01798")
        
        if result:
            print(f"  ✅ 検索成功!")
            print(f"    チャネル名: {result}")
        else:
            print("  ❌ 検索失敗!")
            
            # 手動でチャネル一覧を取得して詳細確認
            print("\n  詳細デバッグ: 利用可能チャネル一覧")
            slack_integration = poster.slack_integration
            bot_channels = slack_integration.get_bot_channels()
            
            print(f"  Bot参加チャネル数: {len(bot_channels)}")
            
            # 1798を含むチャネルを検索
            channels_with_1798 = [ch for ch in bot_channels if '1798' in ch.get('name', '')]
            
            if channels_with_1798:
                print("  1798を含むチャネル:")
                for ch in channels_with_1798:
                    print(f"    - {ch['name']} (ID: {ch.get('id', 'N/A')})")
            
            # 検索パターンを手動で実行
            print("\n  手動検索パターンテスト:")
            channel_number = "1798"  # N01798から1798を抽出
            
            search_patterns = [
                (f"n{channel_number}-", "starts"),      # n1798-xxx (前方一致)
                (f"{channel_number}-", "starts"),       # 1798-xxx (前方一致)
                (f"-{channel_number}-", "contains"),    # xxx-1798-xxx (部分一致)
                (channel_number, "contains")            # 1798を含む任意のパターン
            ]
            
            for pattern, match_type in search_patterns:
                print(f"    パターン '{pattern}' ({match_type}):")
                
                for channel in bot_channels:
                    channel_name = channel.get('name', '')
                    
                    if match_type == "starts":
                        if channel_name.startswith(pattern):
                            print(f"      ✓ マッチ: {channel_name}")
                    elif match_type == "contains":
                        if pattern in channel_name:
                            print(f"      ✓ マッチ: {channel_name}")
        
        print("\n2. その他のNコードテスト:")
        test_codes = ["N09999", "N01234", "N99999"]
        
        for code in test_codes:
            result = poster.find_slack_channel(code)
            if result:
                print(f"  {code}: ✅ {result}")
            else:
                print(f"  {code}: ❌ 見つからず")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_channel_search_logic()