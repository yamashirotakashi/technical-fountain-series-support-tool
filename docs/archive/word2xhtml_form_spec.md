# Word2XHTML5サービス フォーム仕様書

## サービス情報
- **URL**: `http://trial.nextpublishing.jp/upload_46tate/`
- **メソッド**: POST
- **Content-Type**: multipart/form-data

## フォーム要素一覧（実際のHTML解析結果）

### 1. プロジェクト名
- **name**: `project_name`
- **type**: text
- **値**: "山城技術の泉" (固定)

### 2. 縦/横選択
- **name**: `direction` ※実際のname属性
- **type**: radio
- **値**: `-10` (横（B5技術書）)
- **注意**: この機能では横書きのみ対応

### 3. 扉の有無
- **name**: `tobira` ※実際のname属性
- **type**: radio
- **値**: `0` (なし - デフォルトchecked)

### 4. トンボの有無
- **name**: `tombo` ※実際のname属性
- **type**: radio
- **値**: `0` (なし - デフォルトchecked)

### 5. スタイル選択（横書きの場合）
- **name**: `syoko` ※実際のname属性（横書き用）
- **type**: radio
- **値**: `2` (本文（ソースコード）) ※実際の値
- **注意**: 縦書き用は`state`、横書き用は`syoko`

### 6. 索引の有無
- **name**: `index` ※実際のname属性
- **type**: radio
- **値**: `0` (なし - デフォルトchecked)

### 7. メールアドレス
- **name**: `mail`
- **type**: text
- **値**: `yamashiro.takashi@gmail.com`

### 8. メールアドレス確認
- **name**: `mailconf`
- **type**: text
- **値**: `yamashiro.takashi@gmail.com`

### 9. ファイルアップロード
- **name**: `userfile1` ※実際のname属性
- **type**: file
- **accept**: `.docx`

## 実装時の注意事項

1. **横書き専用**: この機能では横書き（B5技術書）のみ対応
2. **固定値**: プロジェクト名、各種オプション（扉、トンボ、索引）は固定
3. **メール**: 環境変数 `GMAIL_ADDRESS` から取得可能
4. **ファイル形式**: Word2013以降のdocx形式のみ対応

## フォームデータ例（実際のname属性使用）

```python
form_data = {
    'project_name': '山城技術の泉',
    'direction': -10,         # 横（B5技術書）
    'tobira': 0,             # 扉なし
    'tombo': 0,              # トンボなし
    'syoko': 2,              # 本文（ソースコード）- 横書き用
    'index': 0,              # 索引なし
    'mail': 'yamashiro.takashi@gmail.com',
    'mailconf': 'yamashiro.takashi@gmail.com'
}

files = {
    'userfile1': ('document.docx', file_content, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
}
```

## レスポンス処理

- 成功時: ジョブIDまたは受付番号がレスポンスに含まれる
- 失敗時: エラーメッセージがレスポンスに含まれる
- メール通知: 処理完了時にメールでダウンロードリンクが送信される