# Gmail API統合提案書

## 現状分析

### 現在の実装
- **通常のReVIEW変換**: `EmailMonitor` (IMAP使用)
- **エラー検知処理**: `GmailOAuthMonitor` (Gmail API使用)

### 問題点
1. IMAPは2段階認証やアプリパスワードが必要
2. 同じ機能（メール監視）に2つの異なる実装が存在
3. Gmail APIの方が安全でメンテナンスしやすい

## 提案内容

### 1. 統一的なメール監視インターフェース
```python
class EmailMonitorInterface:
    """メール監視の共通インターフェース"""
    def wait_for_email(self, timeout=1200, check_interval=30, **kwargs):
        raise NotImplementedError
    
    def close(self):
        pass
```

### 2. Gmail API実装への段階的移行

#### Phase 1: 設定による切り替え（推奨）
```python
@property
def email_monitor(self):
    """EmailMonitorの遅延初期化（設定に基づく実装選択）"""
    if self._email_monitor is None and self.email_password:
        use_gmail_api = self.config.get('email', {}).get('use_gmail_api', False)
        
        if use_gmail_api:
            # Gmail API使用
            from core.gmail_oauth_monitor import GmailOAuthMonitor
            self._email_monitor = GmailOAuthMonitor()
            self._email_monitor.authenticate()
        else:
            # 従来のIMAP使用
            from core.email_monitor import EmailMonitor
            self._email_monitor = EmailMonitor(self.email_address, self.email_password)
            self._email_monitor.connect()
    return self._email_monitor
```

#### Phase 2: Gmail APIをデフォルトに
- 設定ファイルで`use_gmail_api: true`をデフォルト値に
- IMAPは後方互換性のために残す

#### Phase 3: IMAP実装の廃止（将来）
- 十分な移行期間後、IMAP実装を削除

### 3. 実装上の考慮事項

#### 利点
- **セキュリティ**: OAuth2.0による安全な認証
- **保守性**: アプリパスワード不要
- **機能性**: より詳細なメール情報取得可能

#### 注意点
- **初回設定**: OAuth認証フローが必要
- **権限**: Gmail APIの有効化が必要
- **互換性**: 既存ユーザーへの影響を最小限に

## 実装手順

1. **設定ファイルの拡張**
   ```json
   {
     "email": {
       "use_gmail_api": false,  // デフォルトは従来のIMAP
       "gmail_credentials_path": "config/gmail_oauth_credentials.json"
     }
   }
   ```

2. **WorkflowProcessorの修正**
   - email_monitorプロパティを上記のように修正
   - 両方の実装で共通のインターフェースを保証

3. **ドキュメント更新**
   - Gmail API設定手順の追加
   - 移行ガイドの作成

4. **テスト**
   - 両方の実装でE2Eテストが通ることを確認
   - 設定切り替えが正しく動作することを確認

## 推奨事項

1. **段階的移行**: まず設定による切り替えを実装し、ユーザーフィードバックを収集
2. **デフォルト維持**: 当面は従来のIMAPをデフォルトとし、安定性を確保
3. **明確な文書化**: Gmail API設定の利点と手順を明確に文書化

## まとめ

Gmail API統合により、より安全で保守しやすいメール監視機能を提供できます。段階的な移行により、既存ユーザーへの影響を最小限に抑えつつ、新機能の利点を享受できます。