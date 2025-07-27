#!/usr/bin/env python3
"""
チャネル検索のデバッグテスト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from unittest.mock import Mock
from src.slack_pdf_poster import SlackPDFPoster

def test_z1798_channel_search():
    """z1798-nuxt3-tailwindcssの検索テスト"""
    
    # SlackPDFPosterを初期化
    poster = SlackPDFPoster()
    
    # モックのSlack統合を設定
    mock_slack_integration = Mock()
    mock_slack_integration.get_bot_channels.return_value = [
        {"name": "z1798-nuxt3-tailwindcss"},
        {"name": "n1234-test-book"},
        {"name": "general"},
    ]
    
    poster.slack_integration = mock_slack_integration
    
    print("=== チャネル検索デバッグテスト ===")
    print(f"利用可能チャネル:")
    for channel in mock_slack_integration.get_bot_channels():
        print(f"  - {channel['name']}")
    
    print(f"\nN01798からのチャネル検索:")
    
    # N番号からチャネル番号を抽出
    channel_number = poster.extract_channel_number("N01798")
    print(f"抽出された番号: {channel_number}")
    
    # チャネル検索を実行
    result = poster.find_slack_channel(channel_number)
    print(f"検索結果: {result}")
    
    if result:
        print("✅ 検索成功")
    else:
        print("❌ 検索失敗")
        
        # 手動でパターン確認
        print("\n=== 手動パターン確認 ===")
        test_channel = "z1798-nuxt3-tailwindcss"
        
        patterns = [
            f"n{channel_number}-",
            f"{channel_number}-", 
            f"-{channel_number}-",
            channel_number
        ]
        
        for pattern in patterns:
            if pattern == channel_number:
                match = pattern in test_channel
                print(f"パターン '{pattern}' (contains): {match}")
            else:
                match = test_channel.startswith(pattern) or pattern in test_channel
                print(f"パターン '{pattern}': startswith={test_channel.startswith(pattern)}, contains={pattern in test_channel}")

if __name__ == "__main__":
    test_z1798_channel_search()