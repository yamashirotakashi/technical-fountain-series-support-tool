# Windows PowerShell環境セットアップガイド

## 📋 概要

このガイドでは、技術の泉シリーズ制作支援ツールのPre-flight Quality Check機能をWindows PowerShell環境で実行するためのセットアップ手順を説明します。

## 🎯 前提条件

### システム要件
- **OS**: Windows 10/11 (PowerShell 5.1以上)
- **Python**: Python 3.8以上
- **メモリ**: 4GB以上推奨
- **ディスク容量**: 1GB以上の空き容量

### 必要なアカウント
- **Gmail**: アプリパスワード対応のGoogleアカウント
- **Word2XHTML5サービス**: 認証情報（既存のReVIEW変換と同じ）

## 🚀 セットアップ手順

### Step 1: Python環境の準備

#### Python のインストール確認
```powershell
# Python バージョン確認
python --version

# pip の確認
pip --version
```

#### Python がインストールされていない場合
1. [Python公式サイト](https://www.python.org/downloads/)からダウンロード
2. インストール時に「Add Python to PATH」をチェック
3. インストール後、PowerShellを再起動

### Step 2: プロジェクトのセットアップ

#### プロジェクトディレクトリに移動
```powershell
cd C:\Users\[ユーザー名]\DEV\technical-fountain-series-support-tool
```

#### 仮想環境の作成と有効化
```powershell
# 仮想環境作成
python -m venv venv

# 仮想環境有効化
.\venv\Scripts\Activate.ps1
```

**注意**: PowerShellの実行ポリシーエラーが発生した場合：
```powershell
# 実行ポリシーを一時的に変更
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 仮想環境有効化を再実行
.\venv\Scripts\Activate.ps1
```

#### 依存関係のインストール
```powershell
# 依存パッケージのインストール
pip install -r requirements.txt

# 主要パッケージの個別インストール（必要に応じて）
pip install requests psutil python-dotenv
```

### Step 3: 環境変数の設定

#### .env ファイルの作成
プロジェクトルートに `.env` ファイルを作成：

```env
# Gmail設定（必須）
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# ログレベル（オプション）
LOG_LEVEL=INFO

# Word2XHTML5サービス設定（デフォルト値で通常は不要）
WORD2XHTML_URL=http://trial.nextpublishing.jp/upload_46tate/
WORD2XHTML_USER=ep_user
WORD2XHTML_PASSWORD=Nn7eUTX5
```

#### Gmail アプリパスワードの取得方法

1. **Googleアカウントの2段階認証を有効化**
   - [Googleアカウント設定](https://myaccount.google.com/)にアクセス
   - 「セキュリティ」→「2段階認証プロセス」を有効化

2. **アプリパスワードの生成**
   - 「セキュリティ」→「アプリパスワード」
   - アプリ: 「メール」、デバイス: 「Windowsコンピュータ」を選択
   - 生成された16文字のパスワードを `.env` ファイルに設定

3. **Gmail IMAP設定の有効化**
   - Gmail設定 → 「転送とPOP/IMAP」
   - 「IMAP を有効にする」をチェック

### Step 4: テスト実行

#### 自動テストランナーの実行
```powershell
# 完全テストスイートの実行
.\scripts\windows_test_runner.ps1

# 詳細出力付きでテスト実行
.\scripts\windows_test_runner.ps1 -Verbose

# ログ保存なしでテスト実行
.\scripts\windows_test_runner.ps1 -SaveLogs:$false
```

#### 手動テスト実行
```powershell
# Python テストスクリプトの直接実行
python tests\test_windows_powershell.py
```

## 🔧 設定のカスタマイズ

### コンフィグファイルの場所
Pre-flightシステムの設定は以下の場所に保存されます：
```
C:\Users\[ユーザー名]\.techzip\preflight\config.json
```

### 主要設定項目

#### メール設定
```json
{
  "email": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "imap_server": "imap.gmail.com",
    "imap_port": 993,
    "username": "your-email@gmail.com",
    "password": "your-app-password",
    "use_ssl": true,
    "timeout_seconds": 30
  }
}
```

#### 検証設定
```json
{
  "validation": {
    "mode": "standard",
    "max_file_size_mb": 50,
    "min_file_size_bytes": 512,
    "allowed_extensions": [".docx", ".doc"],
    "enable_security_check": true
  }
}
```

#### 監視設定
```json
{
  "monitoring": {
    "email_check_interval_minutes": 5,
    "max_wait_minutes": 20,
    "search_hours": 24
  }
}
```

## 🛠️ トラブルシューティング

### よくある問題と解決方法

#### 1. PowerShell実行ポリシーエラー
```
実行ポリシーによってこのスクリプトの実行が拒否されました
```

**解決方法:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Python パッケージのインストールエラー
```
pip install でエラーが発生する
```

**解決方法:**
```powershell
# pip のアップグレード
python -m pip install --upgrade pip

# キャッシュをクリアして再インストール
pip install --no-cache-dir -r requirements.txt
```

#### 3. Gmail 認証エラー
```
IMAP connection failed
```

**解決方法:**
- 2段階認証が有効になっているか確認
- アプリパスワードが正しく設定されているか確認
- Gmail IMAP設定が有効になっているか確認

#### 4. ファイル検証エラー
```
File validation failed
```

**解決方法:**
- ファイルが.docx形式で512バイト以上であることを確認
- ファイルパスに日本語や特殊文字が含まれていないか確認
- ファイルが他のアプリケーションで開かれていないか確認

### ログファイルの確認

#### ログの場所
```
technical-fountain-series-support-tool\logs\
```

#### 主要ログファイル
- `windows_test_[timestamp].log`: テスト実行ログ
- `preflight_[date].log`: Pre-flight実行ログ
- `performance_[date].log`: パフォーマンス監視ログ

## 📊 パフォーマンス最適化

### システムリソース監視

Pre-flightシステムは自動的にシステムリソースを監視します：

- **CPU使用率**: 90%超過時にアラート
- **メモリ使用率**: 95%超過時にアラート
- **ディスクI/O**: 500MB/s超過時にアラート

### 推奨設定

#### 大量ファイル処理時
```json
{
  "validation": {
    "mode": "quick"
  },
  "monitoring": {
    "email_check_interval_minutes": 10,
    "max_wait_minutes": 30
  }
}
```

#### 高精度検証時
```json
{
  "validation": {
    "mode": "thorough",
    "enable_security_check": true,
    "enable_content_analysis": true
  }
}
```

## 🔍 実働テストシナリオ

### 基本動作確認
1. 単一DOCXファイルの検証と送信
2. 複数ファイルのバッチ処理
3. エラーファイルの適切な処理

### 負荷テスト
1. 10ファイル同時処理
2. 大容量ファイル（50MB）の処理
3. 長時間監視（20分）の動作確認

### エラー回復テスト
1. ネットワーク接続エラーの処理
2. メールサービス一時停止の対応
3. システムリソース不足時の動作

## 📝 実用的な使用例

### コマンドラインからの実行
```powershell
# Pre-flightマネージャーの直接実行
python -c "
from core.preflight.unified_preflight_manager import create_preflight_manager
manager = create_preflight_manager()
result = manager.process_files_sync(['path/to/file.docx'], 'user@example.com')
print(f'Job results: {result}')
"
```

### スクリプトでの自動化例
```powershell
$files = @("document1.docx", "document2.docx")
$email = "your-email@gmail.com"

foreach ($file in $files) {
    Write-Host "Processing: $file"
    python -c "
from core.preflight.unified_preflight_manager import create_preflight_manager
manager = create_preflight_manager()
result = manager.process_files_sync(['$file'], '$email')
print(f'Processed {len(result)} jobs')
"
}
```

## 🚀 次のステップ

1. **基本テストの実行**: `.\scripts\windows_test_runner.ps1`
2. **実際のファイルでテスト**: 本番DOCXファイルを使用
3. **カスタマイズ**: 設定ファイルを環境に合わせて調整
4. **自動化**: バッチ処理スクリプトの作成
5. **監視**: 長期間の動作監視と最適化

## 📞 サポート

問題が発生した場合は以下の情報を収集してサポートに連絡してください：

1. **環境情報**: Python・OS・PowerShellのバージョン
2. **エラーログ**: logs/ディレクトリ内のログファイル
3. **設定ファイル**: .envファイル（認証情報は除く）
4. **テスト結果**: windows_powershell_test_results.json

Windows PowerShell環境でのPre-flight Quality Check機能の実働が成功することを祈っています！