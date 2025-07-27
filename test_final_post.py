#!/usr/bin/env python3
"""
最終的なPDF投稿テスト（メッセージ付き）
"""
import os
from datetime import datetime
from slack_sdk import WebClient
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ SLACK_BOT_TOKEN環境変数が設定されていません")
    exit(1)

def main():
    client = WebClient(token=BOT_TOKEN)
    
    print("=== 技術の泉シリーズ PDF投稿テスト ===")
    
    # テスト用PDFの作成
    test_pdf_path = "techzip_test.pdf"
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
<< /Length 60 >>
stream
BT
/F1 12 Tf
100 700 Td
(Technical Fountain Series) Tj
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
436
%%EOF"""
        f.write(pdf_content)
    
    # PDF投稿
    try:
        response = client.files_upload_v2(
            channel="C097H72S49H",  # n9999-bottest
            file=test_pdf_path,
            filename="techzip_test.pdf",
            initial_comment=f"""📚 技術の泉シリーズ PDF Bot テスト

🎯 Bot名変更確認
⏰ 投稿時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ PDF投稿機能は正常に動作しています
💡 Slackでの表示名を確認してください"""
        )
        
        print(f"✅ 投稿成功！")
        
        # レスポンスから情報を取得
        file_info = response.get('files', [{}])[0] if response.get('files') else response.get('file', {})
        if file_info.get('permalink'):
            print(f"URL: {file_info['permalink']}")
            print(f"\n👀 Slackで以下を確認してください:")
            print(f"1. Botの表示名が「技術の泉シリーズ」になっているか")
            print(f"2. PDFが正しくアップロードされているか")
            print(f"3. メッセージが表示されているか")
        
    except Exception as e:
        print(f"❌ 投稿失敗: {e}")
    finally:
        # テストファイル削除
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
            print("\n✅ テストファイルを削除しました")

if __name__ == "__main__":
    main()