#!/usr/bin/env python3
"""
TechZip Bot自己招待スクリプト（Bot Token版）
"""

from slack_sdk import WebClient
import time
import sys

# ========== 設定項目 ==========
# Bot Token
BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

# ドライランモード
DRY_RUN = True
# ==============================

def main():
    client = WebClient(token=BOT_TOKEN)
    
    print("🔍 プライベートチャネル一覧を取得中...")
    
    try:
        # Botの情報を取得
        auth_response = client.auth_test()
        bot_user_id = auth_response['user_id']
        print(f"Bot User ID: {bot_user_id}")
        
        # チャネル一覧取得
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        channels = response['channels']
        
        print(f"📊 {len(channels)}個のプライベートチャネルが見つかりました")
        
        # Botがメンバーでないチャネルをフィルタ
        non_member_channels = [ch for ch in channels if not ch.get('is_member', False)]
        tech_channels = [ch for ch in non_member_channels if ch['name'].startswith(('n', 'N'))]
        
        print(f"🎯 Botが未参加の技術の泉チャネル: {len(tech_channels)}個")
        
        if len(tech_channels) == 0:
            print("✅ 全てのチャネルに参加済みです")
            return
        
        print("\n以下のチャネルに参加を試みます:")
        for ch in tech_channels[:10]:
            print(f"  - {ch['name']}")
        if len(tech_channels) > 10:
            print(f"  ... 他 {len(tech_channels) - 10}個\n")
        
        if DRY_RUN:
            print("\n⚠️  ドライランモード: 実際の参加は行いません")
            print("   本番実行するには DRY_RUN = False に設定してください")
            return
        
        success_count = 0
        error_count = 0
        
        # 各チャネルに参加を試みる
        for i, channel in enumerate(tech_channels):
            channel_name = channel['name']
            channel_id = channel['id']
            
            try:
                # conversations.joinを試す
                response = client.conversations_join(channel=channel_id)
                print(f"[{i+1}/{len(tech_channels)}] ✅ {channel_name}")
                success_count += 1
                time.sleep(1)
                
            except Exception as e:
                print(f"[{i+1}/{len(tech_channels)}] ❌ {channel_name}: {e}")
                error_count += 1
                time.sleep(0.5)
        
        # 結果サマリー
        print(f"\n✅ 成功: {success_count}個")
        print(f"❌ エラー: {error_count}個")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("\nBot Tokenではチャネル参加ができない場合は、")
        print("管理者に手動でBotを招待してもらう必要があります。")

if __name__ == "__main__":
    main()