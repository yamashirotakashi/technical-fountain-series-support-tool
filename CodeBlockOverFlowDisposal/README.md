# コードブロックはみ出し検出システム

技術の泉シリーズのPDFから、コードブロックが本文幅を超えてはみ出している箇所を自動検出するツールです。

## 概要

NextPublishing形式のPDFにおいて、コードブロック内のテキストが右端からはみ出す問題を自動検出し、編集者の手動確認作業を効率化します。

## インストール

```bash
# 追加ライブラリのインストール
pip install -r requirements_addon.txt  # PDF構造解析用
pip install -r requirements_image.txt  # 画像処理用
```

## 使用方法

### シンプル版（推奨）

```bash
python overflow_detector_simple.py sample.pdf

# レポートをファイルに保存
python overflow_detector_simple.py sample.pdf -o report.txt

# 検出結果を可視化
python overflow_detector_simple.py sample.pdf --visualize
```

### 画像処理版（高精度）

```bash
python overflow_detector_image.py sample.pdf
```

### PDF構造解析版（開発中）

```bash
python overflow_detector.py sample.pdf
```

## 実装アプローチ

### 1. PDF構造解析アプローチ（overflow_detector.py）
- pdfplumber + PyMuPDFを使用
- 灰色矩形を検出してテキスト位置を解析
- **課題**: NextPublishingのPDF構造により検出困難

### 2. 画像処理アプローチ（overflow_detector_image.py）
- OpenCV + PyMuPDFを使用
- PDFを画像化して視覚的に検出
- 灰色背景と罫線囲みの両方に対応
- **利点**: 確実な検出が可能
- **欠点**: 処理速度が遅い、誤検出の可能性

### 3. シンプルアプローチ（overflow_detector_simple.py）
- 右マージンエリアのテキスト検出に特化
- 連続性による判定で誤検出を削減
- **利点**: 高速、シンプル
- **課題**: 左右ページでマージンが異なる場合の対応

## 検出対象

1. **灰色背景コードブロック**
   - 背景色: RGB(0.85, 0.85, 0.85)前後
   - 技術の泉シリーズの標準形式

2. **白背景・罫線囲みコードブロック**
   - 黒い罫線で囲まれた領域
   - sample2.pdfの60ページに例あり

## 技術仕様

- **本文幅**: 約425.9pt（ページ幅515.9pt - 左右マージン）
- **判定基準**: 本文幅を超えるテキストが存在する場合
- **出力**: はみ出しが検出されたページ番号のリスト

## 今後の改善点

1. **左右ページの異なるマージンへの対応**
   - 奇数ページと偶数ページで異なるレイアウトの考慮

2. **OCR統合（Phase 2）**
   - Tesseractによる高精度テキスト認識
   - より正確なはみ出し位置の特定

3. **GUI統合**
   - 既存のTechZip編集支援システムへの統合
   - リアルタイムプレビュー機能

## トラブルシューティング

### "Unable to get page count"エラー
WSL環境では発生しません（PyMuPDFを使用するため）。

### 灰色矩形が検出されない
NextPublishingのPDF生成方法により、構造解析では検出困難な場合があります。画像処理版を使用してください。

### 処理が遅い
シンプル版（overflow_detector_simple.py）を使用するか、DPI設定を下げてください。

## ライセンス

本プロジェクトのライセンスに準拠