#!/usr/bin/env python3
"""
自動テスト投稿（インタラクティブ入力なし）
"""
import os
from datetime import datetime
from src.slack_integration import SlackIntegration

def main():
    # 環境変数からBot Token取得
    bot_token = os.environ.get('SLACK_BOT_TOKEN', os.environ.get('SLACK_BOT_TOKEN'))
    
    # Slack統合の初期化
    slack = SlackIntegration(bot_token)
    
    # 接続テスト
    print("=== Slack接続テスト ===")
    result = slack.test_connection()
    if not result['success']:
        print(f"❌ 接続失敗: {result['error']}")
        return
    
    print(f"✅ 接続成功")
    print(f"Team: {result['team']}")
    print(f"Bot: {result['user']}")
    print(f"Bot ID: {result['bot_id']}")
    
    # テスト用PDFの作成
    print("\n=== テストPDF作成 ===")
    test_pdf_path = "test_techzip.pdf"
    with open(test_pdf_path, 'wb') as f:
        # 簡単なPDFヘッダー（最小限のPDF）
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
    
    print(f"✅ テストPDF作成完了: {test_pdf_path}")
    
    # n-ネトコン作品検討にテスト投稿
    target_channel = "n-ネトコン作品検討"
    print(f"\n=== {target_channel} への投稿テスト ===")
    
    result = slack.post_pdf_to_channel(
        pdf_path=test_pdf_path,
        repo_name=target_channel,
        book_title="TechZip Slack統合テスト",
        message_template="🧪 TechZip Slack統合のテスト投稿です\n\n生成日時: {timestamp}\nリポジトリ: {repo_name}\n\n※このメッセージはテストです"
    )
    
    if result['success']:
        print(f"✅ 投稿成功！")
        print(f"チャネル: {result['channel']}")
        print(f"ファイルID: {result['file_id']}")
        print(f"URL: {result['permalink']}")
    else:
        print(f"❌ 投稿失敗: {result['error']}")
        if 'action_required' in result:
            print(f"必要なアクション: {result['action_required']}")
        if 'instruction' in result:
            print(result['instruction'])
    
    # テストファイルの削除
    if os.path.exists(test_pdf_path):
        os.remove(test_pdf_path)
        print("\n✅ テストファイルを削除しました")

if __name__ == "__main__":
    main()