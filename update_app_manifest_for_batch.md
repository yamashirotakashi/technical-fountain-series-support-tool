# App ManifestでUser Scopesを追加する方法

## 手順

1. **Slack APIページにアクセス**
   - https://api.slack.com/apps/A097K6HTULW/app-manifest

2. **現在のManifestをコピー**
   - YAMLまたはJSON形式で表示されている

3. **oauth_configセクションに以下を追加**:
```yaml
oauth_config:
  scopes:
    bot:
      # 既存のbot scopes
    user:  # これを追加
      - channels:read
      - groups:read
      - groups:write
      - users:read
```

4. **保存して、Reinstall**
   - https://api.slack.com/apps/A097K6HTULW/install-on-team
   - 「Reinstall to Workspace」をクリック

5. **User OAuth Tokenを取得**
   - Install Appページに表示される
   - `xoxp-`で始まるトークン

6. **batch_invite_with_admin.pyを実行**
   - ADMIN_TOKENに取得したUser Tokenを設定
   - `python batch_invite_with_admin.py`