# コードブロックはみ出し検出システム インストールガイド

## システム要件

### 必須コンポーネント
- **Python**: 3.8以上
- **Tesseract OCR**: 4.0以上（システムレベルインストール必須）
- **メモリ**: 2GB以上推奨
- **ディスク容量**: 500MB以上

## インストール手順

### 1. Tesseract OCRのインストール

#### Ubuntu/Debian系
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

#### CentOS/RHEL系
```bash
sudo yum install epel-release
sudo yum install tesseract tesseract-langpack-jpn
```

#### Windows
1. [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)をダウンロード
2. インストール時に「Japanese」言語パックを選択
3. 環境変数PATHにTesseractのパスを追加

#### macOS
```bash
brew install tesseract
brew install tesseract-lang
```

### 2. Python依存関係のインストール

```bash
# 仮想環境の有効化（推奨）
source venv/bin/activate

# 依存ライブラリのインストール
pip install -r requirements_ocr.txt
```

### 3. 動作確認

#### Tesseractの確認
```bash
tesseract --version
tesseract --list-langs | grep jpn
```

期待される出力:
```
tesseract 4.1.1
jpn
```

#### Pythonライブラリの確認
```bash
python -c "import pytesseract; print('pytesseract version:', pytesseract.get_tesseract_version())"
```

### 4. 実行テスト

```bash
# ヘルプ表示
python overflow_detector_ocr.py --help

# サンプルPDFでのテスト（Tesseractインストール後）
python overflow_detector_ocr.py sample.pdf
```

## トラブルシューティング

### Tesseract関連

#### 「tesseract command not found」エラー
- **原因**: Tesseractがシステムにインストールされていない
- **解決**: 上記のインストール手順を実行

#### 「Error opening data file jpn.traineddata」エラー
- **原因**: 日本語言語パックがインストールされていない
- **解決**: 
  ```bash
  # Ubuntu/Debian
  sudo apt-get install tesseract-ocr-jpn
  
  # Windows: 再インストール時に言語パックを選択
  ```

#### パスの問題（Windows）
```python
# Windows環境でのパス設定例
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Python環境関連

#### 「No module named 'pytesseract'」エラー
```bash
# 仮想環境の確認
which python
pip show pytesseract

# 必要に応じて再インストール
pip install --upgrade pytesseract
```

#### メモリ不足エラー
- 大容量PDFの場合、メモリ使用量が増加
- 解決策: バッチサイズを調整、または分割処理

### OCR精度関連

#### 日本語が認識されない
```bash
# 言語設定の確認
python overflow_detector_ocr.py sample.pdf --lang jpn+eng
```

#### 処理が遅い
- 解像度を下げる（ただし精度低下）
- CPUリソースの確認
- メモリ十分性の確認

## 開発環境セットアップ

### 1. プロジェクトクローン
```bash
cd /path/to/technical-fountain-series-support-tool/CodeBlockOverFlowDisposal
```

### 2. 仮想環境セットアップ
```bash
# 親ディレクトリの仮想環境を使用
cd ..
source venv/bin/activate
cd CodeBlockOverFlowDisposal
```

### 3. 開発用ツールのインストール
```bash
# 品質チェックツール（オプション）
pip install flake8 mypy black isort
```

### 4. 品質チェック実行
```bash
python quality_check.py
```

## 本番環境デプロイ

### Docker環境（推奨）
```dockerfile
# Dockerfile例
FROM ubuntu:20.04

# Tesseractインストール
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-jpn python3 python3-pip

# アプリケーションコピー
COPY . /app
WORKDIR /app

# Python依存関係インストール
RUN pip3 install -r requirements_ocr.txt

ENTRYPOINT ["python3", "overflow_detector_ocr.py"]
```

### サーバー環境
1. システム管理者権限でTesseractをインストール
2. Python仮想環境での依存関係インストール
3. 適切なファイル権限設定

## パフォーマンス最適化

### 推奨設定
```python
# OCR設定の最適化
detector = OCRBasedOverflowDetector()
detector.DPI = 200  # 解像度を下げて高速化（デフォルト: 300）
```

### 大容量PDF対応
- メモリ監視機能の有効化
- バッチ処理サイズの調整
- 必要に応じて一時ファイルの活用

## サポート

### 技術サポート
- プロジェクトIssues: [GitHub Issues](リンク)
- ドキュメント: README_OCR.md
- 仕様書: requirements.md, design.md

### よくある質問
1. **Q**: 処理時間はどの程度？
   **A**: 1ページあたり2-3秒（環境依存）

2. **Q**: 対応するPDF形式は？
   **A**: 標準的なPDF（テキスト含む）、画像PDF（OCRで解析）

3. **Q**: 精度はどの程度？
   **A**: 95%以上（PDF品質に依存）