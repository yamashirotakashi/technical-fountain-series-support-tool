# CodeBlock Overflow Checker - 独立版

Phase 2C-1 実装: Windows PowerShell環境対応の独立した溢れチェックアプリケーション

## 概要

技術書の右端コードブロック溢れを検出し、ユーザーフィードバックを通じて学習データを蓄積する独立アプリケーションです。

## 特徴

- **Windows PowerShell環境対応**: 文字コード、BOM、パス処理の問題に完全対応
- **OCR検出器統合**: Phase 1完成の高精度検出アルゴリズムを統合
- **学習システム**: ユーザーフィードバックによる継続的な精度向上
- **直感的GUI**: Qt6ベースの使いやすいインターフェース

## インストール

### 前提条件

- Python 3.8以上
- Windows 10/11 (PowerShell環境)
- Tesseract OCR

### 依存関係のインストール

```powershell
cd CodeBlockOverFlowDisposal/overflow_checker_standalone
pip install -r requirements.txt
```

### Tesseract OCRの設定

1. [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)をダウンロード・インストール
2. インストールパス（通常 `C:\Program Files\Tesseract-OCR`）を環境変数PATHに追加

## セットアップ（初回のみ）

### 自動セットアップ（推奨）

```powershell
.\setup_and_run.ps1
```

このスクリプトは以下を自動実行します：
- 仮想環境の作成
- 必要なライブラリのインストール
- Tesseract OCRの確認
- アプリケーションの起動

## 使用方法

### クイック起動（2回目以降）

```powershell
.\quick_run.ps1
```

### 手動起動

1. **仮想環境のアクティベート**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **アプリケーション起動**
   ```powershell
   python run_ultimate.py
   ```

2. **PDFファイル選択**
   - ブラウズボタンでファイル選択、または直接パス入力

3. **溢れチェック実行**
   - 「溢れチェック実行」ボタンをクリック
   - 進捗バーで処理状況を確認

4. **結果確認・学習データ入力**
   - 検出結果を確認
   - 誤検出のチェックを外す
   - 見落としがあれば追加ページを入力
   - 「学習データとして保存」で学習に貢献

### 学習データについて

- **確認済み溢れ**: チェックが入っているページは「実際に溢れがある」として学習
- **誤検出**: チェックを外したページは「誤検出」として学習
- **追加ページ**: 検出されなかった溢れページを手動入力
- **SQLiteデータベース**: `%APPDATA%\OverflowChecker\learning_data.db` に保存

## アーキテクチャ

```
overflow_checker_standalone/
├── main.py                    # アプリケーションエントリーポイント
├── gui/
│   ├── main_window.py         # メインウィンドウ
│   └── result_dialog.py       # 結果表示・学習データ収集
├── core/
│   ├── pdf_processor.py       # PDF処理メイン
│   └── learning_manager.py    # 学習データ管理
├── utils/
│   └── windows_utils.py       # Windows環境対応ユーティリティ
├── data/                      # データディレクトリ（自動作成）
├── requirements.txt           # 依存関係
└── README.md                  # このファイル
```

## Windows環境対応

### 文字コード処理
- UTF-8 BOM付きファイル対応
- PowerShell環境でのUTF-8出力
- Shift-JISフォールバック

### パス処理
- バックスラッシュの正規化
- Windows UNCパス対応
- パス長制限の考慮

### 設定ファイル保存場所
- **設定**: `%APPDATA%\OverflowChecker\config.json`
- **学習データ**: `%APPDATA%\OverflowChecker\learning_data.db`

## 学習統計

アプリケーションは以下の統計情報を自動収集：

- **検出精度**: Precision（適合率）
- **検出漏れ**: Recall（再現率）
- **総合評価**: F1-Score
- **学習ケース数**: 蓄積された学習データ数

## トラブルシューティング

### よくある問題

1. **Tesseract OCRが見つからない**
   ```
   TesseractNotFoundError: tesseract is not installed
   ```
   → Tesseract OCRをインストールし、PATHを設定

2. **PyQt6インポートエラー**
   ```
   ModuleNotFoundError: No module named 'PyQt6'
   ```
   → `pip install PyQt6` でインストール

3. **文字化け・エンコーディングエラー**
   → PowerShellで `chcp 65001` を実行してUTF-8に設定

### ログの確認

アプリケーションログは標準出力に表示されます。詳細な動作確認が必要な場合は、PowerShellから起動してください。

## Phase 2C-2への移行準備

このアプリケーションは以下の機能でPhase 2C-2（学習データ収集・検証フェーズ）をサポート：

- **データエクスポート**: 学習データのJSON出力
- **統計レポート**: 検出精度の継続的監視
- **バッチ処理**: 複数PDFの効率的処理（今後実装）

## ライセンス

Technical Fountain Series Support Tool の一部として、プロジェクトライセンスに従います。