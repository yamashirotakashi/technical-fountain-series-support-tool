# Claude Code認証エラー対策・復旧システム
作成日: 2025-07-28

## 🚨 **問題概要**
Claude CodeでAPI Error 401 (OAuth token has expired)が発生し、MCP設定・CLAUDE.md設定が全てクリアされる問題への完全対策システム。

## 🎯 **解決策**

### 1. **自動バックアップシステム**

#### 初回起動時自動バックアップ
```bash
# 日次起動チェック（自動実行推奨）
python scripts/daily_startup_check.py
```

#### 手動バックアップ
```bash
# 特殊コマンド（推奨）
［バックアップ］

# または直接実行
python scripts/claude_code_backup_system.py backup
```

#### バックアップ対象
- **Claude Code設定**: `~/.config/claude/` 全体
  - `mcp_servers.json` (MCP設定)
  - `settings.json` (Claude設定)
  - `auth.json` (認証情報)
  - `sessions/` (セッションデータ)
- **CLAUDE.mdファイル群**: 全プロジェクトのCLAUDE.md
- **システム情報**: バージョン、MCP状況等

### 2. **認証エラー完全復旧システム**

#### 完全復旧（認証エラー時）
```bash
python scripts/claude_code_recovery_system.py full-recovery
```

**復旧プロセス**:
1. **問題診断** - 認証状況・設定ファイル確認
2. **バックアップ確認** - 利用可能バックアップ検索
3. **設定クリーンアップ** - `~/.config/claude/` 完全削除
4. **再認証待機** - ブラウザでの再ログイン待機
5. **バックアップ復元** - 全設定・CLAUDE.mdファイル復元
6. **復旧確認** - MCP設定動作確認

#### クイック復旧（認証OK時）
```bash
python scripts/claude_code_recovery_system.py quick-recovery
```

### 3. **診断・メンテナンス**

#### 現在状況診断
```bash
python scripts/claude_code_recovery_system.py diagnose
```

#### バックアップ一覧確認
```bash
python scripts/claude_code_backup_system.py list
```

#### 設定クリーンアップのみ
```bash
python scripts/claude_code_recovery_system.py clean
```

## 🔧 **実装詳細**

### スクリプト構成
```
/mnt/c/Users/tky99/dev/
├── clauderestore.ps1                            # PowerShell復旧コマンド（推奨）
└── technical-fountain-series-support-tool/scripts/
    ├── claude_code_backup_system.py             # バックアップシステム本体
    ├── claude_code_recovery_system.py           # 復旧システム本体  
    └── daily_startup_check.py                   # 日次起動チェック
```

### バックアップ保存場所
```
/mnt/c/Users/tky99/dev/.claude_code_backups/
├── daily_backup_20250728_231220.zip  # タイムスタンプ付きバックアップ
├── daily_backup_20250728.zip         # 日次リンク（最新）
└── emergency_backup_*.zip            # 緊急バックアップ
```

### バックアップ内容構造
```
backup.zip
├── claude_config/                    # Claude設定
│   ├── mcp_config/mcp_servers.json
│   ├── claude_settings/settings.json
│   └── auth_config/auth.json
├── claude_md_files/                  # CLAUDE.mdファイル群
│   ├── mnt/c/Users/tky99/dev/CLAUDE.md
│   └── mnt/c/Users/tky99/dev/*/CLAUDE.md
├── mcp_status/mcp_list_output.txt    # MCP設定状況
└── system_info.json                 # システム情報
```

## 🚀 **使用方法**

### 日常運用
1. **Claude Code起動時**:
   ```bash
   python scripts/daily_startup_check.py
   ```
   - 初回起動時自動バックアップチェック・実行
   - 12時間以上経過、設定変更時に自動バックアップ

2. **重要作業前の緊急バックアップ**:
   ```powershell
   # PowerShell（devフォルダで実行）
   .\clauderestore.ps1 backup
   
   # または特殊コマンド
   ［バックアップ］
   ```

### 認証エラー発生時
1. **症状確認**:
   - `API Error: 401 OAuth token has expired`
   - `claude mcp list` でエラー
   - MCP設定消失

2. **完全復旧実行**（devフォルダで実行）:
   ```powershell
   # PowerShell（推奨）
   .\clauderestore.ps1 full-recovery
   
   # またはWSLコマンド直接実行
   python scripts/claude_code_recovery_system.py full-recovery
   ```

3. **復旧手順**:
   - スクリプトの指示に従い再認証
   - 自動的にバックアップから全設定復元
   - MCP設定・CLAUDE.mdファイル完全復旧

## ⚡ **特殊コマンド統合**

### CLAUDE.mdへの統合
`［バックアップ］` 特殊コマンドが利用可能:

```markdown
### 特殊プロンプト一覧
- ［バックアップ］ - Claude Code設定・CLAUDE.mdファイル群の緊急バックアップ実行
```

### 実装詳細
- **緊急バックアップ**: 設定・CLAUDE.mdファイル即座バックアップ
- **自動チェック**: 初回起動時必要性自動判定
- **完全復旧**: 認証エラー時の設定削除→再認証→復元

## 🛡️ **予防・保守**

### 自動化推奨設定
1. **起動時チェック**: 
   - WSL起動スクリプトに組み込み
   - PowerShellプロファイルに組み込み

2. **定期バックアップ**:
   - 重要作業前の手動バックアップ習慣化
   - 設定変更後の即座バックアップ

3. **バックアップ管理**:
   - 古いバックアップの定期クリーンアップ
   - 重要バックアップの別保存

## 🔍 **トラブルシューティング**

### よくある問題

#### バックアップ失敗
```bash
# 権限確認
ls -la ~/.config/claude/
# 手動バックアップディレクトリ作成
mkdir -p /mnt/c/Users/tky99/dev/.claude_code_backups
```

#### 復旧失敗
```bash
# 診断実行
python scripts/claude_code_recovery_system.py diagnose
# 手動設定クリーンアップ
rm -rf ~/.config/claude/
```

#### MCP設定復元問題
```bash
# MCP設定状況確認
claude mcp list
# 手動MCP再追加が必要な場合あり
```

## 📋 **システム動作確認**

### テスト手順
1. **バックアップテスト**:
   ```bash
   python scripts/claude_code_backup_system.py backup
   python scripts/claude_code_backup_system.py list
   ```

2. **復旧テスト**（注意: 設定が削除されます）:
   ```bash
   python scripts/claude_code_recovery_system.py diagnose
   # 必要に応じてテスト実行
   ```

3. **特殊コマンドテスト**:
   ```
   ［バックアップ］
   ```

---

**重要**: 本システムにより、Claude Code認証エラーが発生しても、最短時間で全設定・CLAUDE.mdファイルを完全復旧できます。日常的なバックアップ習慣により、データ損失リスクを完全に回避可能です。