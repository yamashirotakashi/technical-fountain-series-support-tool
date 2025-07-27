#!/usr/bin/env python3
"""
正しいBot Tokenでのテスト
"""
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 技術の泉シリーズワークスペースの正しいBot Token
BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

def main():
    # 環境変数を設定
    os.environ['SLACK_BOT_TOKEN'] = BOT_TOKEN
    
    # WebClientを直接使用
    client = WebClient(token=BOT_TOKEN)
    
    print("=== Slack接続テスト ===")
    try:
        auth_response = client.auth_test()
        print(f"✅ 接続成功")
        print(f"Team: {auth_response['team']}")
        print(f"User: {auth_response['user']}")
        print(f"Bot ID: {auth_response['user_id']}")
        print(f"URL: {auth_response['url']}")
    except SlackApiError as e:
        print(f"❌ 接続失敗: {e}")
        return
    
    print("\n=== 参加チャネル一覧 ===")
    try:
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        
        channels = response.get('channels', [])
        print(f"📊 {len(channels)}個のプライベートチャネルに参加中:")
        
        # n で始まるチャネルを探す
        for ch in channels:
            if ch['name'].startswith(('n', 'N')):
                print(f"  ✅ {ch['name']} (ID: {ch['id']})")
        
        # n9999-bottestを探す
        n9999_channel = next((ch for ch in channels if ch['name'] == 'n9999-bottest'), None)
        if n9999_channel:
            print(f"\n🎯 n9999-bottest が見つかりました！")
            print(f"   ID: {n9999_channel['id']}")
            
            # テスト投稿
            print("\n=== テスト投稿 ===")
            test_pdf_path = "test_direct.pdf"
            
            # 簡単なPDFを作成
            with open(test_pdf_path, 'wb') as f:
                pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(TechZip Test) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000229 00000 n 
0000000328 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
420
%%EOF"""
                f.write(pdf_content)
            
            # files_upload_v2を使用
            try:
                response = client.files_upload_v2(
                    channel=n9999_channel['id'],
                    file=test_pdf_path,
                    filename="test_direct.pdf",
                    initial_comment="🎉 TechZip Bot のテスト投稿成功！\n\nPDF投稿機能が正常に動作しています。"
                )
                
                print(f"✅ 投稿成功！")
                
                # レスポンスから情報を取得
                file_info = response.get('files', [{}])[0] if response.get('files') else response.get('file', {})
                if file_info.get('permalink'):
                    print(f"URL: {file_info['permalink']}")
                
            except SlackApiError as e:
                print(f"❌ 投稿失敗: {e}")
            finally:
                # テストファイル削除
                if os.path.exists(test_pdf_path):
                    os.remove(test_pdf_path)
        else:
            print(f"\n⚠️  n9999-bottest チャネルが見つかりません")
            print("Slack上でBotをチャネルに招待してください")
            
    except SlackApiError as e:
        print(f"❌ チャネル一覧取得失敗: {e}")

if __name__ == "__main__":
    main()