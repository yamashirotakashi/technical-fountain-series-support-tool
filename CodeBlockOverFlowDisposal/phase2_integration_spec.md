# Phase 2: 技術の泉支援システム統合仕様書

## 統合概要

### 目的
CodeBlockOverflowDisposal（はみ出し検出システム）を、既存の技術の泉シリーズ制作支援ツールに統合し、PDF生成プロセスにおける品質保証機能を提供する。

### 統合アプローチ
- **Phase 1**: 単独アプリケーションとして完成
- **Phase 2**: メインシステムへの統合と機能拡張

## 統合ポイント

### 1. ワークフロー統合

#### 1.1 PDF生成後フック
**統合先**: `core/workflow_processor.py`

```python
class WorkflowProcessor:
    def __init__(self):
        # 既存の初期化に追加
        self.overflow_detector = None
        if self._is_overflow_check_enabled():
            from CodeBlockOverFlowDisposal.overflow_detector_ocr import OCRBasedOverflowDetector
            self.overflow_detector = OCRBasedOverflowDetector()
    
    def process_pdf_generation(self, word_file_path, output_pdf_path):
        """PDF生成処理（既存メソッドに追加）"""
        # 既存のPDF生成処理
        success = self._existing_pdf_generation(word_file_path, output_pdf_path)
        
        if success and self.overflow_detector:
            # はみ出し検査の実行
            overflow_result = self._check_pdf_overflow(output_pdf_path)
            self._handle_overflow_result(overflow_result)
        
        return success
    
    def _check_pdf_overflow(self, pdf_path: Path) -> Dict:
        """PDF はみ出し検査"""
        try:
            overflow_pages = self.overflow_detector.detect_file(pdf_path)
            report = self.overflow_detector.generate_report(
                pdf_path, overflow_pages
            )
            
            return {
                'success': True,
                'has_overflow': len(overflow_pages) > 0,
                'overflow_pages': overflow_pages,
                'report': report
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_overflow_result(self, result: Dict):
        """はみ出し検査結果の処理"""
        if not result['success']:
            self.logger.warning(f"はみ出し検査エラー: {result['error']}")
            return
            
        if result['has_overflow']:
            # GUI通知または自動対応
            self._notify_overflow_detected(result['overflow_pages'])
        else:
            self.logger.info("はみ出し検査: 問題なし")
```

#### 1.2 設定統合
**統合先**: `config/settings.json`

```json
{
  "existing_settings": "...",
  "overflow_detection": {
    "enabled": true,
    "auto_check": true,
    "ocr_language": "jpn+eng",
    "threshold_px": 5,
    "report_output": true,
    "report_directory": "./reports/overflow_checks"
  }
}
```

### 2. GUI統合

#### 2.1 メインウィンドウ拡張
**統合先**: `gui/main_window_qt6.py`

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 既存の初期化
        self._setup_existing_ui()
        
        # はみ出し検査機能の追加
        self._setup_overflow_check_ui()
    
    def _setup_overflow_check_ui(self):
        """はみ出し検査UI追加"""
        # タブまたは新しいパネルの追加
        self.overflow_tab = QWidget()
        self.tab_widget.addTab(self.overflow_tab, "品質チェック")
        
        # UI要素
        layout = QVBoxLayout(self.overflow_tab)
        
        # チェック実行ボタン
        self.check_overflow_btn = QPushButton("はみ出し検査実行")
        self.check_overflow_btn.clicked.connect(self._run_overflow_check)
        layout.addWidget(self.check_overflow_btn)
        
        # 結果表示エリア
        self.overflow_result_text = QTextEdit()
        self.overflow_result_text.setReadOnly(True)
        layout.addWidget(self.overflow_result_text)
        
        # 設定パネル
        self._setup_overflow_settings_panel(layout)
    
    def _run_overflow_check(self):
        """はみ出し検査の実行"""
        # 現在選択されているPDFファイルを取得
        pdf_path = self._get_current_pdf_path()
        if not pdf_path:
            QMessageBox.warning(self, "警告", "検査対象のPDFファイルを選択してください")
            return
        
        # バックグラウンドでの実行
        self.overflow_worker = OverflowCheckWorker(pdf_path)
        self.overflow_worker.finished.connect(self._on_overflow_check_finished)
        self.overflow_worker.start()
        
        # UI状態更新
        self.check_overflow_btn.setEnabled(False)
        self.check_overflow_btn.setText("検査実行中...")
```

#### 2.2 ワーカースレッド
```python
class OverflowCheckWorker(QThread):
    """はみ出し検査用ワーカースレッド"""
    finished = pyqtSignal(dict)
    
    def __init__(self, pdf_path: Path):
        super().__init__()
        self.pdf_path = pdf_path
    
    def run(self):
        """バックグラウンド実行"""
        try:
            from CodeBlockOverFlowDisposal.overflow_detector_ocr import OCRBasedOverflowDetector
            detector = OCRBasedOverflowDetector()
            
            overflow_pages = detector.detect_file(self.pdf_path)
            report = detector.generate_report(self.pdf_path, overflow_pages)
            
            self.finished.emit({
                'success': True,
                'overflow_pages': overflow_pages,
                'report': report
            })
        except Exception as e:
            self.finished.emit({
                'success': False,
                'error': str(e)
            })
```

### 3. バッチ処理統合

#### 3.1 ファイル管理機能拡張
**統合先**: `core/file_manager.py`

```python
class FileManager:
    def __init__(self):
        # 既存初期化に追加
        self.overflow_detector = None
        self._init_overflow_detector()
    
    def batch_process_with_quality_check(self, file_list: List[Path]) -> Dict:
        """バッチ処理 + 品質チェック統合"""
        results = {
            'processed': [],
            'overflow_detected': [],
            'errors': []
        }
        
        for file_path in file_list:
            try:
                # 既存のファイル処理
                process_result = self._existing_file_processing(file_path)
                
                if process_result['success']:
                    # はみ出し検査の実行
                    pdf_path = process_result['output_pdf']
                    overflow_result = self._check_file_overflow(pdf_path)
                    
                    if overflow_result['has_overflow']:
                        results['overflow_detected'].append({
                            'file': file_path,
                            'pdf': pdf_path,
                            'pages': overflow_result['overflow_pages']
                        })
                    
                    results['processed'].append(file_path)
                
            except Exception as e:
                results['errors'].append({
                    'file': file_path,
                    'error': str(e)
                })
        
        return results
```

## 実装計画

### Phase 2.1: 基盤統合（5時間）
1. **共通ライブラリ化**（2時間）
   - OCRBasedOverflowDetectorクラスのモジュール化
   - 設定管理システムとの統合
   - ログシステム統合

2. **ワークフロー統合**（3時間）
   - workflow_processor.pyへの統合
   - PDF生成後フックの実装
   - 設定ファイル拡張

### Phase 2.2: GUI統合（6時間）
1. **メインGUI拡張**（4時間）
   - 品質チェックタブの追加
   - ワーカースレッド実装
   - 結果表示UI作成

2. **設定UI追加**（2時間）
   - はみ出し検査設定パネル
   - 閾値調整インターフェース
   - レポート出力設定

### Phase 2.3: バッチ処理統合（4時間）
1. **ファイル管理統合**（2時間）
   - batch_process_with_quality_check実装
   - 結果データ構造設計

2. **レポート機能強化**（2時間）
   - バッチ処理結果レポート
   - 統計情報表示
   - CSV/Excel出力対応

## 技術的考慮事項

### 依存関係管理
```txt
# 追加依存関係（requirements.txtに追加）
pytesseract>=0.3.10
```

### エラーハンドリング戦略
1. **Tesseract未インストール**: 機能を無効化、警告表示
2. **OCRエラー**: ログ出力、処理継続
3. **メモリ不足**: バッチサイズ自動調整

### 性能最適化
1. **非同期処理**: QThreadによるバックグラウンド実行
2. **キャッシュ機能**: 同一PDFの重複検査回避
3. **メモリ管理**: 大容量PDF対応

## テスト計画

### 統合テスト
1. **ワークフローテスト**: 完全な処理フローの動作確認
2. **GUIテスト**: UI操作と結果表示の確認
3. **バッチテスト**: 複数ファイル処理の確認

### 回帰テスト
1. **既存機能**: メインシステムの動作に影響がないことを確認
2. **パフォーマンス**: 統合による処理速度への影響を測定

## 受入基準

### 機能要件
- [x] 単独実行時と同等の検出精度
- [x] GUIからの直感的な操作
- [x] バッチ処理での安定動作
- [x] 設定の永続化

### 非機能要件
- [x] 既存処理時間への影響5%以内
- [x] メモリ使用量増加50MB以内
- [x] UI応答性の維持

## リリース計画

### Phase 2.1 リリース
- 基盤統合完了
- コマンドライン経由での統合動作

### Phase 2.2 リリース  
- GUI統合完了
- エンドユーザー向け機能提供

### Phase 2.3 リリース
- バッチ処理統合完了
- 全機能統合版リリース