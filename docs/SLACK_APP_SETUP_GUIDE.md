# TechZip Slack App セットアップガイド

最終更新: 2025-01-27

## 📋 事前準備チェックリスト

- [ ] Slackワークスペースの管理者権限があることを確認
- [ ] 技術の泉プロジェクトのプライベートチャネル一覧を把握
- [ ] 作業用のWebブラウザを準備（Chrome/Firefox推奨）

## 🚀 Step 1: Slack App作成

### 1.1 Slack API サイトにアクセス

1. ブラウザで https://api.slack.com/apps にアクセス
2. 「Create New App」ボタンをクリック
3. 「From scratch」を選択

### 1.2 App基本情報の入力

```
App Name: TechZip PDF Bot
Development Slack Workspace: [あなたのワークスペース名]
```

「Create App」をクリック

### 1.3 Bot User作成

1. 左メニューから「OAuth & Permissions」を選択
2. 「Bot Token Scopes」セクションまでスクロール
3. 「Add an OAuth Scope」をクリック
4. 以下のスコープを追加:

#### Phase 1で必要なスコープ
- `files:write` - PDFファイルのアップロード
- `chat:write` - メッセージの投稿
- `groups:read` - プライベートチャネルの読み取り

#### Phase 2用に事前設定するスコープ
- `groups:write` - チャネルの作成・管理
- `incoming-webhook` - GitHub通知の受信

### 1.4 Appインストール

1. ページ上部の「Install to Workspace」をクリック
2. 権限確認画面で「許可する」をクリック
3. インストール完了後、以下のトークンが表示されます:

```
Bot User OAuth Token: xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxx
```

**⚠️ 重要: このトークンを安全な場所にコピーして保存してください**

## 🤖 Step 2: Bot IDの確認

### 2.1 Bot User IDを取得

1. 左メニューから「App Home」を選択
2. 「Show」タブの下部にある「App ID」と「Bot User ID」を確認
3. Bot User IDをメモ（例: U1234567890）

## 📢 Step 3: Bot一括チャネル登録

### 3.1 準備

1. 以下のファイルを作成: `slack_bot_invite.py`

```python
#!/usr/bin/env python3
"""
TechZip Bot一括チャネル登録スクリプト

使い方:
1. USER_TOKENとBOT_USER_IDを設定
2. python slack_bot_invite.py を実行
"""

from slack_sdk import WebClient
import time
import sys

# ========== 設定項目 ==========
# 管理者のUser OAuth Token（※Bot Tokenとは別）
# 取得方法: https://api.slack.com/authentication/token-types#user
USER_TOKEN = "xoxp-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxx"

# Bot User ID（Step 2.1で取得したもの）
BOT_USER_ID = "U1234567890"

# ドライランモード（True: 実際には招待しない、False: 実際に招待する）
DRY_RUN = True
# ==============================

def main():
    if not USER_TOKEN or USER_TOKEN.startswith("xoxp-xxx"):
        print("❌ エラー: USER_TOKENを設定してください")
        print("   管理者権限のあるユーザーのトークンが必要です")
        print("   取得方法: https://api.slack.com/authentication/token-types#user")
        sys.exit(1)
    
    if not BOT_USER_ID or BOT_USER_ID == "U1234567890":
        print("❌ エラー: BOT_USER_IDを設定してください")
        print("   Slack App設定画面で確認できます")
        sys.exit(1)
    
    client = WebClient(token=USER_TOKEN)
    
    print("🔍 プライベートチャネル一覧を取得中...")
    
    try:
        # プライベートチャネル一覧取得
        response = client.conversations_list(
            types="private_channel",
            limit=1000
        )
        channels = response['channels']
        
        print(f"📊 {len(channels)}個のプライベートチャネルが見つかりました")
        
        if DRY_RUN:
            print("\n⚠️  ドライランモード: 実際の招待は行いません")
            print("   本番実行するには DRY_RUN = False に設定してください\n")
        
        # 技術の泉プロジェクトのチャネルをフィルタ（必要に応じて条件を調整）
        tech_channels = [ch for ch in channels if ch['name'].startswith(('n', 'N'))]
        
        print(f"🎯 技術の泉プロジェクトと思われるチャネル: {len(tech_channels)}個")
        print("\n以下のチャネルにBotを招待します:")
        for ch in tech_channels[:10]:  # 最初の10個を表示
            print(f"  - {ch['name']}")
        if len(tech_channels) > 10:
            print(f"  ... 他 {len(tech_channels) - 10}個\n")
        
        if not DRY_RUN:
            confirm = input("続行しますか？ (y/N): ")
            if confirm.lower() != 'y':
                print("キャンセルしました")
                sys.exit(0)
        
        success_count = 0
        already_count = 0
        error_count = 0
        
        # 各チャネルにBotを招待
        for i, channel in enumerate(tech_channels):
            channel_name = channel['name']
            channel_id = channel['id']
            
            if DRY_RUN:
                print(f"[{i+1}/{len(tech_channels)}] 🔍 {channel_name} (スキップ: ドライラン)")
                continue
            
            try:
                response = client.conversations_invite(
                    channel=channel_id,
                    users=BOT_USER_ID
                )
                print(f"[{i+1}/{len(tech_channels)}] ✅ {channel_name}")
                success_count += 1
                time.sleep(1)  # Rate limit対策
                
            except Exception as e:
                error_msg = str(e)
                if "already_in_channel" in error_msg:
                    print(f"[{i+1}/{len(tech_channels)}] ⏭️  {channel_name} (既に参加済み)")
                    already_count += 1
                else:
                    print(f"[{i+1}/{len(tech_channels)}] ❌ {channel_name}: {error_msg}")
                    error_count += 1
                time.sleep(0.5)
        
        # 結果サマリー
        print("\n" + "="*50)
        print("📊 実行結果サマリー")
        print("="*50)
        if not DRY_RUN:
            print(f"✅ 成功: {success_count}個")
            print(f"⏭️  既に参加済み: {already_count}個")
            print(f"❌ エラー: {error_count}個")
            print(f"📊 合計: {len(tech_channels)}個")
        else:
            print(f"🔍 ドライラン完了: {len(tech_channels)}個のチャネルを確認")
            print("   本番実行するには DRY_RUN = False に設定してください")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        print("\n考えられる原因:")
        print("1. USER_TOKENが正しくない")
        print("2. 管理者権限がない")
        print("3. ネットワークエラー")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 3.2 User OAuth Tokenの取得方法

**⚠️ 重要: Bot TokenではなくUser Tokenが必要です**

1. https://api.slack.com/legacy/custom-integrations/legacy-tokens にアクセス
2. または、Slack Appの設定で「User Token Scopes」を設定:
   - `users:read`
   - `groups:read`
   - `groups:write`
3. 「Install to Workspace」を再度クリック
4. User OAuth Tokenをコピー（xoxp-で始まる）

### 3.3 スクリプトの実行

1. slack-sdkをインストール:
   ```bash
   pip install slack-sdk
   ```

2. スクリプトを編集:
   - `USER_TOKEN`に管理者のUser OAuth Tokenを設定
   - `BOT_USER_ID`にBotのUser IDを設定
   - `DRY_RUN = True`でテスト実行

3. テスト実行:
   ```bash
   python slack_bot_invite.py
   ```

4. 問題なければ`DRY_RUN = False`に変更して本番実行

## 📝 Step 4: TechZipへの設定

### 4.1 環境変数の設定（推奨）

```bash
# Windows (PowerShell)
$env:SLACK_BOT_TOKEN = "xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxx"

# Linux/Mac
export SLACK_BOT_TOKEN="xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxx"
```

### 4.2 または設定ファイルに保存

TechZipを起動し、「ツール」→「Slack設定」から:
1. Bot Tokenを入力
2. 「接続テスト」をクリック
3. 成功したら「保存」

## ✅ 動作確認

1. TechZipでPDF生成を実行
2. 「完了後Slackに投稿」にチェック
3. PDF生成完了後、該当チャネルに投稿されることを確認

## 🚨 トラブルシューティング

### Bot Tokenが無効と表示される
- トークンが正しくコピーされているか確認
- Appが正しくインストールされているか確認

### チャネルが見つからない
- チャネル名とリポジトリ名が一致しているか確認
- Botがチャネルに参加しているか確認

### 投稿に失敗する
- インターネット接続を確認
- Slack APIのステータスを確認: https://status.slack.com/

## 📞 サポート

問題が解決しない場合は、以下の情報と共にお問い合わせください:
- エラーメッセージのスクリーンショット
- 使用しているTechZipのバージョン
- 実行した手順の詳細