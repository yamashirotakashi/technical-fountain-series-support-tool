# Phase2-C実装戦略書: ユーザーフィードバック学習統合システム

**最終更新**: 2025-07-29  
**Phase1完了**: OCRBasedOverflowDetector 100%テスト通過済み  
**目標**: TECHZIPメインウィンドウへの学習機能付き溢れチェック統合

## 📋 ユーザー要求仕様の詳細分析

### 重要な変更点
- **❌ 従来計画**: タブ統合による品質チェック機能
- **✅ 新仕様**: メインウィンドウボタン統合 + ユーザーフィードバック学習

### 具体的要求事項
1. **「リスト溢れチェック」ボタン新設**
   - 配置: 「処理開始」「クリア」「設定」「エラーファイル検知」「PDF投稿」の横
   - 機能: Nコード入力欄の値からPDF処理を実行

2. **PDF探索ロジック流用**
   - PDF投稿機能の探索ロジックを流用（共用ではない）
   - 検索パス: `G:\.shortcut-targets-by-id\...\NP-IRD\{n_code}\out\`

3. **処理ログ・進捗表示**
   - ログウィンドウへの処理ログ表示
   - プログレスバーでの進捗表示

4. **ユーザーフィードバック学習システム**
   - 検出結果のページリスト表示
   - 各ページにチェックボックス（デフォルト全チェック）
   - 追加溢れページの手動入力機能
   - 学習データの蓄積・活用

## 🏗️ アーキテクチャ設計

### システム構成図
```
TECHZIP Main Window (既存)
├─ InputPanel (拡張)
│  ├─ 処理開始ボタン (既存)
│  ├─ クリアボタン (既存)  
│  ├─ 設定ボタン (既存)
│  ├─ エラーファイル検知ボタン (既存)
│  ├─ PDF投稿ボタン (既存)
│  └─ リスト溢れチェックボタン (新規) ← 追加
│
├─ LogPanel (既存 - 拡張)
│  └─ 溢れチェック処理ログ表示
│
├─ ProgressPanel (既存 - 拡張)  
│  └─ 溢れチェック進捗表示
│
└─ OverflowResultDialog (新規)
   ├─ 検出結果リスト (チェックボックス付き)
   ├─ 追加溢れページ入力フィールド
   ├─ 学習データ保存機能
   └─ フィードバック学習システム
```

## 🔧 具体的実装計画

### Phase 2-C1: ボタン統合とPDF探索 (1-2日)

#### InputPanel拡張
```python
# gui/components/input_panel.py への追加

class InputPanel(QWidget):
    # 新しいシグナル追加
    overflow_check_requested = pyqtSignal(str)  # 溢れチェックリクエスト
    
    def setup_ui(self):
        # 既存ボタン配置の後に追加
        
        # リスト溢れチェックボタン
        self.overflow_check_button = QPushButton("リスト溢れチェック")
        self.overflow_check_button.clicked.connect(self.on_overflow_check_clicked)
        self.overflow_check_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;  # パープル系
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # ボタンレイアウトに追加（PDF投稿の後）
        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.error_check_button)
        button_layout.addWidget(self.pdf_post_button)
        button_layout.addWidget(self.overflow_check_button)  # ここに追加
        button_layout.addStretch()
    
    def on_overflow_check_clicked(self):
        """リスト溢れチェックボタンクリック処理"""
        text = self.n_code_input.toPlainText().strip()
        
        if not text:
            self.show_error("N番号を入力してください。")
            return
        
        # 1つのN番号のみ受け付ける（PDF投稿と同様）
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        n_codes = []
        for line in lines:
            codes = [code.strip() for code in line.replace(',', ' ').replace('\t', ' ').split() if code.strip()]
            n_codes.extend(codes)
        
        if len(n_codes) != 1:
            self.show_error("リスト溢れチェックは1つのN番号のみ指定してください。")
            return
        
        n_code = n_codes[0]
        # 簡易バリデーション
        if not n_code.upper().startswith('N') or len(n_code) < 5:
            self.show_error("正しいN番号を入力してください（例: N01234）。")
            return
        
        self.overflow_check_requested.emit(n_code)
    
    def set_enabled(self, enabled: bool):
        """パネルの有効/無効を設定（拡張）"""
        # 既存の設定に追加
        self.process_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        self.error_check_button.setEnabled(enabled)
        self.pdf_post_button.setEnabled(enabled)
        self.overflow_check_button.setEnabled(enabled)  # 追加
        self.n_code_input.setEnabled(enabled)
```

#### PDF探索ロジック流用
```python
# core/pdf_finder.py - 新規作成（流用版）

from pathlib import Path
import os
from typing import Optional
from utils.logger import get_logger

class PDFFileFinder:
    """PDF探索機能（PDF投稿ロジックから分離・流用）"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        # 設定から取得すべきだが、まずはハードコード
        self.base_path = "G:\\.shortcut-targets-by-id\\0B6euJ_grVeOeMnJLU1IyUWgxeWM\\NP-IRD"
    
    def find_pdf_file(self, n_code: str) -> Optional[Path]:
        """
        NコードからPDFファイルを検索
        
        Args:
            n_code: 検索対象のNコード
            
        Returns:
            見つかったPDFファイルのパス、見つからない場合はNone
        """
        try:
            # Nフォルダのパス構築
            n_folder = Path(self.base_path) / n_code
            
            if not n_folder.exists():
                self.logger.warning(f"Nフォルダが存在しません: {n_folder}")
                return None
            
            # outフォルダを検索
            out_folder = n_folder / "out"
            
            if not out_folder.exists():
                self.logger.warning(f"outフォルダが存在しません: {out_folder}")
                return None
            
            # PDFファイルを検索
            pdf_files = list(out_folder.glob("*.pdf"))
            
            if not pdf_files:
                self.logger.warning(f"PDFファイルが見つかりません: {out_folder}")
                return None
            
            if len(pdf_files) > 1:
                self.logger.warning(f"複数のPDFファイルが見つかりました: {pdf_files}")
                # 最新のファイルを返す
                pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            found_pdf = pdf_files[0]
            self.logger.info(f"PDFファイルを発見: {found_pdf}")
            return found_pdf
            
        except Exception as e:
            self.logger.error(f"PDF検索エラー: {e}", exc_info=True)
            return None
    
    def validate_pdf_file(self, pdf_path: Path) -> bool:
        """PDFファイルの有効性チェック"""
        try:
            if not pdf_path.exists():
                return False
            
            if pdf_path.stat().st_size == 0:
                return False
            
            # 簡易的なPDFヘッダーチェック
            with open(pdf_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    return False
            
            return True
            
        except Exception:
            return False
```

### Phase 2-C2: 溢れチェック処理統合 (2-3日)

#### MainWindow拡張
```python
# gui/main_window.py への追加

class MainWindow(QMainWindow):
    
    def connect_signals(self):
        """シグナル接続（拡張）"""
        # 既存のシグナル接続に追加
        self.input_panel.process_requested.connect(self.start_processing)
        self.input_panel.settings_requested.connect(self.show_process_mode_dialog)
        self.input_panel.pdf_post_requested.connect(self.start_pdf_post)
        self.input_panel.error_check_requested.connect(self.start_error_detection)
        self.input_panel.overflow_check_requested.connect(self.start_overflow_check)  # 新規追加
    
    @pyqtSlot(str)
    def start_overflow_check(self, n_code: str):
        """
        リスト溢れチェックを開始
        
        Args:
            n_code: 検査対象のNコード
        """
        try:
            from core.pdf_finder import PDFFileFinder
            from CodeBlockOverFlowDisposal.overflow_detection_lib.core.detector import OCRBasedOverflowDetector
            from gui.overflow_result_dialog import OverflowResultDialog
            
            self.log_panel.append_log(f"=== リスト溢れチェック開始: {n_code} ===")
            
            # PDFファイル検索
            pdf_finder = PDFFileFinder()
            pdf_path = pdf_finder.find_pdf_file(n_code)
            
            if not pdf_path:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "PDFファイルが見つかりません",
                    f"N番号 {n_code} のPDFファイルが見つかりませんでした。\n\n"
                    f"検索場所: {pdf_finder.base_path}\\{n_code}\\out\\\n\n"
                    f"以下を確認してください:\n"
                    f"・Nフォルダが存在するか\n"
                    f"・outフォルダが存在するか\n"
                    f"・PDFファイルが生成されているか"
                )
                return
            
            # PDF検証
            if not pdf_finder.validate_pdf_file(pdf_path):
                QMessageBox.warning(
                    self,
                    "PDFファイルエラー",
                    f"PDFファイルが破損している可能性があります:\n{pdf_path}"
                )
                return
            
            self.log_panel.append_log(f"PDFファイル発見: {pdf_path.name}")
            
            # UI無効化
            self.input_panel.set_enabled(False)
            self.progress_panel.reset()
            self.progress_panel.update_status("リスト溢れチェック実行中...")
            
            # 溢れチェック処理をワーカースレッドで実行
            self.overflow_worker = OverflowCheckWorker(pdf_path, n_code)
            self.overflow_worker.progress_updated.connect(self.progress_panel.update_progress)
            self.overflow_worker.log_message.connect(self.log_panel.append_log)
            self.overflow_worker.status_updated.connect(self.progress_panel.update_status)
            self.overflow_worker.detection_completed.connect(self.on_overflow_check_completed)
            self.overflow_worker.error_occurred.connect(self.on_overflow_check_error)
            self.overflow_worker.start()
            
            self.status_bar.showMessage("リスト溢れチェック中...")
            
        except Exception as e:
            error_msg = f"リスト溢れチェック処理中にエラーが発生しました: {str(e)}"
            QMessageBox.critical(self, "エラー", error_msg)
            self.log_panel.append_log(error_msg)
    
    @pyqtSlot(object, str)
    def on_overflow_check_completed(self, detection_result, n_code):
        """溢れチェック完了時の処理"""
        try:
            self.log_panel.append_log(f"溢れチェック完了: {detection_result.detection_count}件検出")
            
            # 結果ダイアログを表示
            dialog = OverflowResultDialog(detection_result, n_code, self)
            dialog.learning_data_saved.connect(self.on_learning_data_saved)
            dialog.exec()
            
        except Exception as e:
            self.log_panel.append_log(f"結果表示エラー: {e}")
        finally:
            # UI再有効化
            self.input_panel.set_enabled(True)
            self.progress_panel.update_status("リスト溢れチェック完了")
            self.status_bar.showMessage("準備完了")
    
    @pyqtSlot(str)
    def on_overflow_check_error(self, error_message):
        """溢れチェックエラー時の処理"""
        self.log_panel.append_log(f"溢れチェックエラー: {error_message}")
        QMessageBox.critical(self, "処理エラー", f"リスト溢れチェックでエラーが発生しました:\n\n{error_message}")
        
        # UI再有効化
        self.input_panel.set_enabled(True)
        self.progress_panel.update_status("エラーで中断")
        self.status_bar.showMessage("準備完了")
    
    @pyqtSlot(dict)
    def on_learning_data_saved(self, learning_data):
        """学習データ保存完了時の処理"""
        self.log_panel.append_log(f"学習データ保存完了: 正解{learning_data['correct_count']}件、追加{learning_data['additional_count']}件")
```

#### ワーカースレッド実装
```python
# core/overflow_check_worker.py - 新規作成

from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
from CodeBlockOverFlowDisposal.overflow_detection_lib.core.detector import OCRBasedOverflowDetector
from utils.logger import get_logger

class OverflowCheckWorker(QThread):
    """溢れチェック処理用ワーカースレッド"""
    
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str)
    status_updated = pyqtSignal(str)
    detection_completed = pyqtSignal(object, str)  # result, n_code
    error_occurred = pyqtSignal(str)
    
    def __init__(self, pdf_path: Path, n_code: str):
        super().__init__()
        self.pdf_path = pdf_path
        self.n_code = n_code
        self.logger = get_logger(__name__)
    
    def run(self):
        """溢れチェック処理を実行"""
        try:
            self.status_updated.emit("OCR検出器を初期化中...")
            self.log_message.emit("OCRBasedOverflowDetectorを初期化しています...")
            
            # 検出器を初期化
            detector = OCRBasedOverflowDetector()
            
            self.status_updated.emit("PDFを解析中...")
            self.log_message.emit(f"PDF解析開始: {self.pdf_path.name}")
            
            # 溢れ検出を実行
            def progress_callback(current_page, total_pages, detected_count):
                progress = int((current_page / total_pages) * 100)
                self.progress_updated.emit(progress)
                self.log_message.emit(f"ページ {current_page}/{total_pages} 処理中 - 検出数: {detected_count}")
                self.status_updated.emit(f"解析中: {current_page}/{total_pages} ページ")
            
            # 実際の検出処理
            detection_result = detector.process_pdf_comprehensive(
                self.pdf_path, 
                progress_callback=progress_callback
            )
            
            self.log_message.emit(f"検出完了: {detection_result.detection_count}件の溢れを検出")
            self.status_updated.emit("検出完了")
            self.progress_updated.emit(100)
            
            # 結果を返す
            self.detection_completed.emit(detection_result, self.n_code)
            
        except Exception as e:
            self.logger.error(f"溢れチェック処理エラー: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
```

### Phase 2-C3: ユーザーフィードバック学習システム (3-4日)

#### 結果表示・学習ダイアログ
```python
# gui/overflow_result_dialog.py - 新規作成

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QCheckBox, QTextEdit, QPushButton, QScrollArea,
                             QWidget, QFrame, QSpinBox, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Dict, List
from core.learning_data_manager import LearningDataManager

class OverflowResultDialog(QDialog):
    """溢れチェック結果表示・学習ダイアログ"""
    
    learning_data_saved = pyqtSignal(dict)  # 学習データ保存完了
    
    def __init__(self, detection_result, n_code: str, parent=None):
        super().__init__(parent)
        self.detection_result = detection_result
        self.n_code = n_code
        self.learning_manager = LearningDataManager()
        self.page_checkboxes = {}
        self.setup_ui()
    
    def setup_ui(self):
        """UIセットアップ"""
        self.setWindowTitle(f"リスト溢れチェック結果 - {self.n_code}")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # タイトル・サマリー
        title_label = QLabel(f"検出結果: {self.detection_result.detection_count}件の溢れを検出")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        if self.detection_result.detection_count == 0:
            # 検出なしの場合
            no_result_label = QLabel("溢れは検出されませんでした。")
            no_result_label.setStyleSheet("font-size: 12pt; color: #4CAF50; margin: 20px;")
            layout.addWidget(no_result_label)
            
            # 終了ボタンのみ
            close_button = QPushButton("閉じる")
            close_button.clicked.connect(self.accept)
            layout.addWidget(close_button)
            return
        
        # 検出リスト表示
        self.setup_detection_list(layout)
        
        # 追加溢れ入力
        self.setup_additional_input(layout)
        
        # ボタン類
        self.setup_buttons(layout)
    
    def setup_detection_list(self, layout):
        """検出リスト表示セットアップ"""
        # スクロールエリア
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 説明ラベル
        instruction_label = QLabel(
            "以下のページで実際に目視確認できた溢れにチェックを入れてください。\n"
            "間違って検出されたページのチェックは外してください。"
        )
        instruction_label.setStyleSheet("margin: 10px; color: #666;")
        scroll_layout.addWidget(instruction_label)
        
        # 検出されたページのチェックボックスリスト
        for page_num in sorted(self.detection_result.detected_pages):
            page_frame = QFrame()
            page_frame.setFrameStyle(QFrame.Shape.Box)
            page_frame.setStyleSheet("margin: 2px; padding: 5px;")
            
            page_layout = QHBoxLayout(page_frame)
            
            # チェックボックス（デフォルトでチェック）
            checkbox = QCheckBox(f"ページ {page_num}")
            checkbox.setChecked(True)  # デフォルト全チェック
            checkbox.setStyleSheet("font-weight: bold;")
            
            # 詳細情報があれば表示
            if hasattr(self.detection_result, 'page_details'):
                detail = self.detection_result.page_details.get(page_num, {})
                overflow_text = detail.get('overflow_text', '')[:50]
                if overflow_text:
                    detail_label = QLabel(f"検出内容: {overflow_text}...")
                    detail_label.setStyleSheet("color: #888; font-size: 10pt;")
                    page_layout.addWidget(detail_label)
            
            page_layout.addWidget(checkbox)
            page_layout.addStretch()
            
            scroll_layout.addWidget(page_frame)
            self.page_checkboxes[page_num] = checkbox
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
    def setup_additional_input(self, layout):
        """追加溢れ入力セットアップ"""
        # 区切り線
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # 追加入力ラベル
        additional_label = QLabel("他の溢れページを入力してください（カンマ、タブ、スペース、改行区切り）")
        additional_label.setStyleSheet("font-weight: bold; margin: 5px;")
        layout.addWidget(additional_label)
        
        # 追加入力フィールド
        self.additional_input = QTextEdit()
        self.additional_input.setMaximumHeight(80)
        self.additional_input.setPlaceholderText("例: 15, 23, 45 または各行に1つずつ")
        self.additional_input.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.additional_input)
    
    def setup_buttons(self, layout):
        """ボタンセットアップ"""
        button_layout = QHBoxLayout()
        
        # 学習データ保存ボタン
        save_learning_button = QPushButton("学習データとして保存")
        save_learning_button.clicked.connect(self.save_learning_data)
        save_learning_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # キャンセルボタン
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;  
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(save_learning_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def save_learning_data(self):
        """学習データを保存"""
        try:
            # チェックされたページを取得
            confirmed_pages = []
            for page_num, checkbox in self.page_checkboxes.items():
                if checkbox.isChecked():
                    confirmed_pages.append(page_num)
            
            # 追加ページを解析
            additional_pages = self.parse_additional_pages()
            
            # 学習データ作成
            learning_data = {
                'n_code': self.n_code,
                'detected_pages': list(self.detection_result.detected_pages),
                'confirmed_pages': confirmed_pages,
                'additional_pages': additional_pages,
                'false_positives': list(set(self.detection_result.detected_pages) - set(confirmed_pages)),
                'missed_pages': additional_pages,
                'timestamp': self.learning_manager.get_current_timestamp(),
                'detection_method': 'OCRBasedOverflowDetector',
                'version': self.detection_result.get('version', '3.0')
            }
            
            # 学習データ保存
            success = self.learning_manager.save_learning_data(learning_data)
            
            if success:
                summary = {
                    'correct_count': len(confirmed_pages),
                    'additional_count': len(additional_pages),
                    'false_positive_count': len(learning_data['false_positives'])
                }
                
                QMessageBox.information(
                    self,
                    "保存完了",
                    f"学習データを保存しました。\n\n"
                    f"確認済み溢れ: {summary['correct_count']}件\n"
                    f"追加溢れ: {summary['additional_count']}件\n"
                    f"誤検出修正: {summary['false_positive_count']}件"
                )
                
                self.learning_data_saved.emit(summary)
                self.accept()
            else:
                QMessageBox.critical(self, "保存エラー", "学習データの保存に失敗しました。")
                
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"学習データ保存中にエラーが発生しました:\n{str(e)}")
    
    def parse_additional_pages(self) -> List[int]:
        """追加ページ入力を解析"""
        text = self.additional_input.toPlainText().strip()
        if not text:
            return []
        
        pages = []
        # カンマ、タブ、スペース、改行で分割
        for line in text.split('\n'):
            for part in line.replace(',', ' ').replace('\t', ' ').split():
                try:
                    page_num = int(part.strip())
                    if page_num > 0:
                        pages.append(page_num)
                except ValueError:
                    continue
        
        return sorted(list(set(pages)))  # 重複除去・ソート
```

### Phase 2-C4: 学習データ管理システム (2-3日)

#### 学習データ管理
```python
# core/learning_data_manager.py - 新規作成

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from utils.logger import get_logger

class LearningDataManager:
    """学習データ管理システム"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.logger = get_logger(__name__)
        
        if db_path is None:
            # デフォルトのデータベースパス
            db_path = Path(__file__).parent.parent / "data" / "learning_data.db"
            db_path.parent.mkdir(exist_ok=True)
        
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベース初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 学習データテーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        n_code TEXT NOT NULL,
                        detected_pages TEXT,  -- JSON配列
                        confirmed_pages TEXT, -- JSON配列
                        additional_pages TEXT, -- JSON配列
                        false_positives TEXT, -- JSON配列
                        missed_pages TEXT,    -- JSON配列
                        timestamp TEXT NOT NULL,
                        detection_method TEXT,
                        version TEXT,
                        metadata TEXT         -- JSON追加情報
                    )
                """)
                
                # 精度改善履歴テーブル
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accuracy_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        total_cases INTEGER,
                        correct_detections INTEGER,
                        false_positives INTEGER,
                        missed_detections INTEGER,
                        precision_score REAL,
                        recall_score REAL,
                        f1_score REAL
                    )
                """)
                
                conn.commit()
                self.logger.info("学習データベースを初期化しました")
                
        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {e}", exc_info=True)
    
    def save_learning_data(self, learning_data: Dict) -> bool:
        """学習データを保存"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO learning_data (
                        n_code, detected_pages, confirmed_pages, additional_pages,
                        false_positives, missed_pages, timestamp, detection_method,
                        version, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    learning_data['n_code'],
                    json.dumps(learning_data['detected_pages']),
                    json.dumps(learning_data['confirmed_pages']),
                    json.dumps(learning_data['additional_pages']),
                    json.dumps(learning_data['false_positives']),
                    json.dumps(learning_data['missed_pages']),
                    learning_data['timestamp'],
                    learning_data['detection_method'],
                    learning_data['version'],
                    json.dumps(learning_data.get('metadata', {}))
                ))
                
                conn.commit()
                self.logger.info(f"学習データを保存しました: {learning_data['n_code']}")
                return True
                
        except Exception as e:
            self.logger.error(f"学習データ保存エラー: {e}", exc_info=True)
            return False
    
    def get_learning_statistics(self) -> Dict:
        """学習データの統計情報を取得"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 総件数
                cursor.execute("SELECT COUNT(*) FROM learning_data")
                total_cases = cursor.fetchone()[0]
                
                if total_cases == 0:
                    return {'total_cases': 0}
                
                # 統計計算
                cursor.execute("""
                    SELECT 
                        n_code, detected_pages, confirmed_pages, 
                        false_positives, missed_pages
                    FROM learning_data
                """)
                
                total_detected = 0
                total_confirmed = 0
                total_false_positives = 0
                total_missed = 0
                
                for row in cursor.fetchall():
                    detected = json.loads(row[1])
                    confirmed = json.loads(row[2])
                    false_pos = json.loads(row[3])
                    missed = json.loads(row[4])
                    
                    total_detected += len(detected)
                    total_confirmed += len(confirmed)
                    total_false_positives += len(false_pos)
                    total_missed += len(missed)
                
                # 精度計算
                precision = total_confirmed / total_detected if total_detected > 0 else 0
                recall = total_confirmed / (total_confirmed + total_missed) if (total_confirmed + total_missed) > 0 else 0
                f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                return {
                    'total_cases': total_cases,
                    'total_detected': total_detected,
                    'total_confirmed': total_confirmed,
                    'total_false_positives': total_false_positives,
                    'total_missed': total_missed,
                    'precision': precision,
                    'recall': recall,
                    'f1_score': f1_score
                }
                
        except Exception as e:
            self.logger.error(f"統計情報取得エラー: {e}", exc_info=True)
            return {'error': str(e)}
    
    def get_improvement_suggestions(self) -> List[Dict]:
        """改善提案を生成"""
        stats = self.get_learning_statistics()
        suggestions = []
        
        if 'error' in stats:
            return suggestions
        
        if stats['total_cases'] < 5:
            suggestions.append({
                'type': 'data_collection',
                'message': f"学習データが不足しています（{stats['total_cases']}件）。より多くのサンプルが必要です。",
                'priority': 'high'
            })
        
        if stats.get('precision', 0) < 0.8:
            suggestions.append({
                'type': 'false_positive_reduction',
                'message': f"誤検出が多い状況です（精度: {stats['precision']:.1%}）。フィルタリング強化を検討してください。",
                'priority': 'medium'
            })
        
        if stats.get('recall', 0) < 0.7:
            suggestions.append({
                'type': 'detection_improvement',
                'message': f"見逃しが多い状況です（再現率: {stats['recall']:.1%}）。検出感度の調整を検討してください。",
                'priority': 'high'
            })
        
        return suggestions
    
    def get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        return datetime.now().isoformat()
```

## 📊 実装スケジュール

### Week 1: 基盤統合 (Phase 2-C1 + 2-C2)
- **Day 1-2**: InputPanelボタン追加・PDF探索ロジック分離
- **Day 3-4**: MainWindow統合・ワーカースレッド実装
- **Day 5**: 基本動作テスト・バグ修正

### Week 2: 学習システム (Phase 2-C3 + 2-C4)
- **Day 1-3**: OverflowResultDialog実装・UI完成
- **Day 4-5**: LearningDataManager実装・DB設計
- **Day 6-7**: 統合テスト・学習フロー確認

### Week 3: 最適化・完成 
- **Day 1-2**: 性能最適化・エラーハンドリング強化
- **Day 3-4**: ユーザビリティ改善・UI/UX調整
- **Day 5**: 総合テスト・ドキュメント整備

## 🎯 成功基準

### 機能基準
- ✅ **リスト溢れチェックボタン**: メインウィンドウに正常配置
- ✅ **PDF探索**: 既存ロジック流用による確実な検索
- ✅ **進捗表示**: ログ・プログレスバー連携動作
- ✅ **学習システム**: チェックボックス・追加入力・データ保存

### 性能基準
- ✅ **検出精度**: Phase1実績（67.9%）以上を維持
- ✅ **処理時間**: 100ページ以内で30秒以内
- ✅ **UI応答性**: 検出中も操作可能なUI

### 学習効果基準
- ✅ **データ蓄積**: 10ケース以上で統計生成
- ✅ **精度向上**: 学習データ活用による改善確認
- ✅ **フィードバック**: ユーザー操作による継続改善

## 🔄 Phase 3+ 拡張ロードマップ

### 学習アルゴリズム高度化
- **機械学習統合**: 蓄積データを活用した検出精度向上
- **パターン学習**: ユーザーフィードバックからの自動パターン抽出
- **適応型フィルタ**: 動的な偽陽性削減

### システム拡張
- **バッチ処理**: 複数Nコード一括処理
- **レポート機能**: 学習統計・改善提案レポート
- **エクスポート機能**: 学習データ・結果のエクスポート

---

**Phase2-C実装準備完了**

*ユーザーフィードバック学習統合による、実用的で進化し続ける品質チェックシステムの実現*