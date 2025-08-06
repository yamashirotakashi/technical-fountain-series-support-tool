# NextPublishingアップロード実装ガイド

## 検証結果サマリー
- **検証日時**: 2025-08-07
- **検証結果**: ✅ 成功（ZIPファイルのアップロード）
- **推奨実装方式**: HTTP Requestsアプローチ

## 実装の要点

### 1. ファイル形式
- **必須**: ZIPファイルのみ受け付ける
- **MIMEタイプ**: `application/zip`
- **拡張子**: `.zip`

### 2. 認証方式
```python
import base64

# Basic認証の実装
credentials = f"{username}:{password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    'Authorization': f'Basic {encoded_credentials}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
}
```

### 3. アップロード実装
```python
import requests

def upload_to_nextpublishing(zip_file_path, email, username, password):
    """NextPublishingへのアップロード"""
    base_url = "http://trial.nextpublishing.jp/rapture/"
    
    # セッション作成
    session = requests.Session()
    
    # Basic認証設定
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 1. フォームページにアクセス（認証確認）
    response = session.get(base_url, headers=headers)
    if response.status_code != 200:
        return False, "認証失敗"
    
    # 2. ファイルアップロード
    with open(zip_file_path, 'rb') as f:
        files = {
            'userfile': (zip_file_path.name, f, 'application/zip')
        }
        data = {
            'mail': email,
            'mailconf': email  # 確認用も同じメールアドレス
        }
        
        response = session.post(
            base_url,
            files=files,
            data=data,
            headers=headers
        )
    
    # 3. 成功判定（同じURLで内容が変化）
    if response.status_code == 200:
        # 成功パターンの検出（文字化けパターンも含む）
        success_patterns = [
            'アップロード完了',
            'ã¢ããã­ã¼ããå®äºãã¾ããã',  # 文字化けパターン
            '変換'
        ]
        
        for pattern in success_patterns:
            if pattern in response.text:
                return True, "アップロード成功"
    
    return False, "アップロード失敗"
```

### 4. 重要な注意点

#### 4.1 文字エンコーディング
- レスポンスはUTF-8 BOM付き
- 日本語が文字化けする場合がある
- 成功判定は複数パターンで行う

#### 4.2 成功判定
- **リダイレクトなし**: 同じURLで成功メッセージが表示される
- **ステータスコード**: 成功時も200が返される
- **コンテンツで判定**: HTMLの内容変化で成功を判定

#### 4.3 必須フィールド
- `userfile`: ZIPファイル（multipart/form-data）
- `mail`: メールアドレス
- `mailconf`: メールアドレス（確認用、同じ値）

### 5. エラーハンドリング
```python
def handle_upload_error(response_text):
    """エラーメッセージの解析"""
    error_patterns = {
        '許可されていない種類': 'ファイル形式エラー（ZIPファイルのみ）',
        'ファイルサイズ': 'ファイルサイズ制限超過',
        '認証': '認証エラー'
    }
    
    for pattern, message in error_patterns.items():
        if pattern in response_text:
            return message
    
    return "不明なエラー"
```

## メインアプリケーションへの統合

`services/nextpublishing_service.py`の改修ポイント：

1. **upload_zip_file()メソッドの修正**
   - Selenium WebDriverアプローチからHTTP Requestsアプローチへ変更
   - Basic認証ヘッダーの追加
   - multipart/form-dataでのファイル送信

2. **成功判定ロジックの改善**
   - リダイレクトを期待しない
   - HTMLコンテンツの変化で判定
   - 文字化けパターンも考慮

3. **エラーハンドリングの強化**
   - ファイル形式チェック（ZIPのみ）
   - 認証エラーの適切な処理
   - タイムアウト処理の追加

## テスト方法

```python
# テスト用スクリプト
from pathlib import Path
import zipfile

# テストZIPファイル作成
test_file = Path("test.txt")
test_file.write_text("Test content")
with zipfile.ZipFile("test.zip", "w") as zf:
    zf.write(test_file)

# アップロードテスト
success, message = upload_to_nextpublishing(
    Path("test.zip"),
    "test@example.com",
    "ep_user",
    "password"
)
print(f"結果: {success} - {message}")
```

## 結論

Selenium WebDriverは不要で、シンプルなHTTP Requestsアプローチで実装可能です。ただし、以下の点に注意：
1. ZIPファイルのみ受け付ける
2. Basic認証はBase64エンコードしたヘッダーで対応
3. 成功判定は同じURLでのコンテンツ変化で行う
4. 文字エンコーディングの問題に対応する