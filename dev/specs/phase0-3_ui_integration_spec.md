# Phase 0-3: 最小UI統合テスト仕様

## 目的
既存の技術の泉シリーズ制作支援ツールのUIに、TechBook27 Analyzerを統合する最小限のプロトタイプを作成。

## 実装要件

### 1. UI統合
- **メインウィンドウへのタブ追加**
  - 既存: 「処理実行」タブ
  - 追加: 「Book Analyzer」タブ
  
- **タブ切り替え機能**
  - CustomTkinterのCTkTabviewを使用
  - シームレスな画面遷移

### 2. 機能統合
- **TechBook27 Analyzerの組み込み**
  - 画像処理機能
  - Word文書処理機能
  - ZIPファイル処理

- **共通設定の活用**
  - settings.jsonの共有
  - 出力先ディレクトリの統一

### 3. Git認証の統合
- **認証設定画面**
  - メニューバー: ツール → Git認証設定
  - PAT入力ダイアログ
  - 認証状態表示

### 4. テスト項目
- [ ] タブ切り替えの動作確認
- [ ] TechBook27 Analyzer機能の動作確認
- [ ] Git認証フローの確認
- [ ] エラーハンドリングの確認

## 実装ファイル構造
```
app/
├── ui/
│   ├── main_window.py       # メインウィンドウ（タブ統合）
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── process_tab.py   # 既存の処理実行タブ
│   │   └── analyzer_tab.py  # Book Analyzerタブ
│   └── dialogs/
│       └── git_auth_dialog.py # Git認証設定ダイアログ
└── main.py                   # エントリーポイント
```

## 成功基準
1. 既存機能を壊さずに新機能を追加
2. UIの一貫性を保持
3. 最小限のコードでの実装
4. Windows環境での動作確認

## リスク緩和
- 既存コードの最小限の変更
- 新機能は独立したタブで実装
- エラー時は既存機能に影響しない設計