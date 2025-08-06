# 設定ファイルについて

## 重要: techzip_config.yaml

`techzip_config.yaml` ファイルには機密情報（APIトークン、パスワード等）が含まれているため、Gitリポジトリには含まれません。

### 初期セットアップ

1. `techzip_config.yaml.template` をコピーして `techzip_config.yaml` を作成：
   ```bash
   cp techzip_config.yaml.template techzip_config.yaml
   ```

2. 作成した `techzip_config.yaml` を編集して、以下の情報を設定：
   - GitHub Personal Access Token
   - Slack Bot Token
   - NextPublishing認証情報
   - Gmailアプリパスワード
   - その他必要な認証情報

### セキュリティに関する注意

- **絶対に** `techzip_config.yaml` をGitにコミットしないでください
- トークンやパスワードは定期的に更新してください
- 本番環境では環境変数の使用を検討してください

### トラブルシューティング

設定ファイルが見つからないエラーが出た場合：
1. このディレクトリに `techzip_config.yaml` が存在することを確認
2. ファイル名が正確であることを確認（拡張子は `.yaml`）
3. テンプレートファイルからコピーして再作成