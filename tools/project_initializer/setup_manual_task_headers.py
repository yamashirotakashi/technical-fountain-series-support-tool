#!/usr/bin/env python3
"""
手動タスク管理シートのヘッダー設定バッチ
1行目に各列の項目名を設定する単独実行可能なスクリプト
"""

import os
import sys
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def setup_manual_task_headers():
    """手動タスク管理シートの1行目にヘッダーを設定"""
    
    # Google Sheets設定
    SHEET_ID = "17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ"
    SHEET_NAME = "手動タスク管理"
    
    # サービスアカウントファイルのパス
    service_account_path = Path(__file__).parent.parent.parent / "config" / "service_account.json"
    
    if not service_account_path.exists():
        print(f"❌ サービスアカウントファイルが見つかりません: {service_account_path}")
        return False
    
    try:
        # Google Sheets APIクライアント初期化
        credentials = service_account.Credentials.from_service_account_file(
            str(service_account_path),
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        sheets = service.spreadsheets()
        
        # ヘッダー行データ
        header_data = [
            "実行日時",
            "Nコード", 
            "ステータス",
            "Slackチャンネル", 
            "GitHubリポジトリ",
            "手動タスク数",
            "要対応内容",
            "実行結果詳細"
        ]
        
        print("🔧 手動タスク管理シートにヘッダーを設定中...")
        print(f"📊 対象シート: {SHEET_ID}")
        print(f"📝 シート名: {SHEET_NAME}")
        print(f"📋 設定項目: {', '.join(header_data)}")
        
        # 1行目にヘッダーを設定
        range_name = f'{SHEET_NAME}!A1:H1'
        body = {'values': [header_data]}
        
        result = sheets.values().update(
            spreadsheetId=SHEET_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        updated_cells = result.get('updatedCells', 0)
        print(f"✅ ヘッダー設定完了: {updated_cells}個のセルを更新しました")
        print(f"🔗 シート確認URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid=1736405482#gid=1736405482")
        
        return True
        
    except HttpError as e:
        print(f"❌ Google Sheets API エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("🛠️  手動タスク管理シート ヘッダー設定バッチ")
    print("=" * 60)
    
    success = setup_manual_task_headers()
    
    if success:
        print("\n🎉 ヘッダー設定が正常に完了しました")
        print("\n📋 設定された項目:")
        headers = [
            "A列: 実行日時",
            "B列: Nコード", 
            "C列: ステータス",
            "D列: Slackチャンネル", 
            "E列: GitHubリポジトリ",
            "F列: 手動タスク数",
            "G列: 要対応内容",
            "H列: 実行結果詳細"
        ]
        for header in headers:
            print(f"  • {header}")
        print("\n✨ 手動タスク管理シートが使用準備完了です")
    else:
        print("\n💥 ヘッダー設定に失敗しました")
        print("📋 確認事項:")
        print("  • サービスアカウントファイルが正しく配置されているか")
        print("  • Google Sheets APIが有効になっているか")
        print("  • シートへのアクセス権限があるか")
        sys.exit(1)

if __name__ == "__main__":
    main()