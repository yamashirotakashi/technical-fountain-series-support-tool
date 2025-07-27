#!/bin/bash
# Slack CLI による一括招待スクリプト

BOT_USER_ID="U098ADT46E4"

echo "🔧 Slack CLIのインストール確認..."
if ! command -v slack &> /dev/null; then
    echo "Slack CLIがインストールされていません"
    echo "インストール方法:"
    echo "curl -fsSL https://downloads.slack-edge.com/slack-cli/install.sh | bash"
    exit 1
fi

echo "🔐 Slack認証..."
slack auth list | grep -q "技術の泉シリーズ"
if [ $? -ne 0 ]; then
    echo "認証が必要です。以下のコマンドを実行してください:"
    echo "slack login"
    exit 1
fi

echo "📊 プライベートチャネル一覧を取得中..."
channels=$(slack conversations list --types private_channel --json | jq -r '.[] | select(.name | startswith("n")) | .id + ":" + .name')

echo "🎯 技術の泉チャネル一覧:"
echo "$channels" | while IFS=: read -r id name; do
    echo "  - $name ($id)"
done

echo ""
read -p "Botを全てのチャネルに招待しますか？ (y/N): " confirm
if [ "$confirm" != "y" ]; then
    echo "キャンセルしました"
    exit 0
fi

echo "🤖 Botを招待中..."
echo "$channels" | while IFS=: read -r id name; do
    echo -n "招待中: $name ... "
    slack conversations invite --channel "$id" --users "$BOT_USER_ID" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅"
    else
        echo "⏭️  (既に参加済み)"
    fi
    sleep 1
done

echo "✨ 完了しました！"