# -*- coding: utf-8 -*-
"""
結果表示・学習データ収集ダイアログ

Phase 2C-1 実装
ユーザーフィードバック機能付きの結果表示
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QCheckBox, QGroupBox,
                             QScrollArea, QWidget, QGridLayout, QMessageBox,
                             QPlainTextEdit, QSplitter, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPen, QColor
from pathlib import Path
from typing import Dict, List
import fitz  # PyMuPDF
from PIL import Image
import io

from core.learning_manager import WindowsLearningDataManager
from utils.windows_utils import is_windows

class OverflowResultDialog(QDialog):
    """溢れチェック結果表示・学習ダイアログ（ページ画像表示機能付き）"""
    
    learning_data_saved = pyqtSignal(dict)
    
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.result = result
        self.page_checkboxes = {}
        self.page_images = {}  # ページ番号 -> QPixmap のキャッシュ
        self.current_page_display = None  # 現在表示中のページ画像ラベル
        self.learning_manager = WindowsLearningDataManager()
        
        self.setup_ui()
        self.populate_results()
        self._load_page_images()
        
    def setup_ui(self):
        """UI構築（画像表示機能付き）"""
        self.setWindowTitle(f"溢れチェック結果 - {self.result.pdf_name}")
        self.setMinimumSize(1200, 800)  # ページ画像表示のためサイズ拡大
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # ヘッダー情報
        header_group = self.create_header_group()
        layout.addWidget(header_group)
        
        # メインコンテンツ（結果リスト + ページ画像表示）
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setSizes([350, 650])  # 左:結果リスト（縮小）, 右:画像表示（拡大）
        
        # 左側：検出結果とフォーム
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 検出結果リスト
        results_group = self.create_results_group()
        left_layout.addWidget(results_group)
        
        # 追加ページ入力
        additional_group = self.create_additional_pages_group()
        left_layout.addWidget(additional_group)
        
        # コメント入力
        comment_group = self.create_comment_group()
        left_layout.addWidget(comment_group)
        
        main_splitter.addWidget(left_widget)
        
        # 右側：ページ画像表示
        image_group = self.create_page_image_group()
        main_splitter.addWidget(image_group)
        
        layout.addWidget(main_splitter)
        
        # ボタン部分
        button_layout = self.create_button_layout()
        layout.addLayout(button_layout)
        
    def create_header_group(self) -> QGroupBox:
        """ヘッダー情報グループ作成（左寄せレイアウト）"""
        group_box = QGroupBox("処理結果サマリー")
        group_box.setStyleSheet(self.get_group_box_style())
        
        # 水平レイアウトに変更（左寄せ）
        layout = QHBoxLayout(group_box)
        
        # 各情報項目を水平に配置
        # PDFファイル名
        layout.addWidget(QLabel("ファイル:"))
        file_label = QLabel(self.result.pdf_name)
        file_label.setStyleSheet("font-weight: bold; margin-right: 15px;")
        layout.addWidget(file_label)
        
        # 総ページ数
        layout.addWidget(QLabel("ページ:"))
        pages_label = QLabel(f"{self.result.total_pages}")
        pages_label.setStyleSheet("margin-right: 15px;")
        layout.addWidget(pages_label)
        
        # 検出件数
        layout.addWidget(QLabel("検出:"))
        detection_label = QLabel(f"{self.result.detection_count}件")
        if self.result.detection_count > 0:
            detection_label.setStyleSheet("color: #e74c3c; font-weight: bold; margin-right: 15px;")
        else:
            detection_label.setStyleSheet("color: #27ae60; font-weight: bold; margin-right: 15px;")
        layout.addWidget(detection_label)
        
        # 処理時間
        layout.addWidget(QLabel("時間:"))
        time_label = QLabel(f"{self.result.processing_time:.2f}秒")
        time_label.setStyleSheet("margin-right: 15px;")
        layout.addWidget(time_label)
        
        # 左寄せのため右側にストレッチを追加
        layout.addStretch()
        
        return group_box
        
    def create_results_group(self) -> QGroupBox:
        """検出結果グループ作成"""
        group_box = QGroupBox("検出された溢れページ（チェックを外すと誤検出として学習されます）")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        if not self.result.overflow_pages:
            # 溢れが検出されなかった場合
            no_overflow_label = QLabel("✅ 溢れは検出されませんでした")
            no_overflow_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-size: 14pt;
                    font-weight: bold;
                    padding: 20px;
                    text-align: center;
                }
            """)
            layout.addWidget(no_overflow_label)
        else:
            # スクロール可能な結果リスト
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setMinimumHeight(200)
            
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout(scroll_widget)
            
            for page_data in self.result.overflow_pages:
                page_widget = self.create_page_result_widget(page_data)
                scroll_layout.addWidget(page_widget)
            
            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)
            
        return group_box
    
    def create_page_result_widget(self, page_data: Dict) -> QWidget:
        """個別ページ結果ウィジェット作成（画像表示機能付き）"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                border: 1px solid #bdc3c7;
                border-radius: 6px;
                margin: 2px;
                padding: 8px;
                background-color: #f8f9fa;
            }
            QWidget:hover {
                background-color: #e8f4f8;
                border-color: #3498db;
            }
        """)
        
        layout = QHBoxLayout(widget)
        
        # チェックボックス（デフォルトはチェック済み）
        page_number = page_data['page_number']
        checkbox = QCheckBox(f"ページ {page_number}")
        checkbox.setChecked(True)  # デフォルトで「実際に溢れがある」として設定
        checkbox.setStyleSheet("font-weight: bold; font-size: 11pt;")
        self.page_checkboxes[page_number] = checkbox
        
        # 溢れ内容
        overflow_text = page_data.get('overflow_text', '')[:50]  # 最初の50文字
        if len(page_data.get('overflow_text', '')) > 50:
            overflow_text += "..."
            
        content_label = QLabel(f"内容: {overflow_text}")
        content_label.setWordWrap(True)
        
        # 溢れ量
        overflow_amount = page_data.get('overflow_amount', 0.0)
        amount_label = QLabel(f"溢れ量: {overflow_amount:.1f}pt")
        amount_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        
        # ページ表示ボタン
        view_page_btn = QPushButton("表示")
        view_page_btn.setFixedSize(60, 25)
        view_page_btn.clicked.connect(lambda: self.display_page_image(page_number))
        view_page_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout.addWidget(checkbox)
        layout.addWidget(content_label, 1)
        layout.addWidget(amount_label)
        layout.addWidget(view_page_btn)
        
        return widget
    
    def create_additional_pages_group(self) -> QGroupBox:
        """追加ページ入力グループ作成"""
        group_box = QGroupBox("見落とされた溢れページ（カンマ、タブ、スペース、改行区切り）")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        # 説明
        description_label = QLabel(
            "検出されなかったが実際には溢れがあるページ番号を入力してください。\n"
            "例: 5, 12, 18 または 5 12 18 または各行に1つずつ"
        )
        description_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        
        # 入力エリア
        self.additional_pages_edit = QPlainTextEdit()
        self.additional_pages_edit.setMaximumHeight(80)
        self.additional_pages_edit.setPlaceholderText("追加のページ番号を入力...")
        self.additional_pages_edit.setStyleSheet("""
            QPlainTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QPlainTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        layout.addWidget(description_label)
        layout.addWidget(self.additional_pages_edit)
        
        return group_box
    
    def create_comment_group(self) -> QGroupBox:
        """コメント入力グループ作成"""
        group_box = QGroupBox("備考・コメント（任意）")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        self.comment_edit = QPlainTextEdit()
        self.comment_edit.setMaximumHeight(80)
        self.comment_edit.setPlaceholderText("このPDFや検出結果についてコメントがあれば入力してください...")
        self.comment_edit.setStyleSheet("""
            QPlainTextEdit {
                font-size: 10pt;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QPlainTextEdit:focus {
                border-color: #3498db;
            }
        """)
        
        layout.addWidget(self.comment_edit)
        
        return group_box
    
    def create_page_image_group(self) -> QGroupBox:
        """ページ画像表示グループ作成"""
        group_box = QGroupBox("ページ画像表示（判定支援）")
        group_box.setStyleSheet(self.get_group_box_style())
        
        layout = QVBoxLayout(group_box)
        
        # 使用方法の説明
        instruction_label = QLabel(
            "左側のページリストから「表示」ボタンをクリックしてページ画像を確認できます。\n"
            "画像は右端3分の1のみ表示され、赤い線が本文幅の右端です。この線を超えているテキストが溢れです。"
        )
        instruction_label.setStyleSheet("color: #666; font-size: 9pt; margin-bottom: 10px;")
        instruction_label.setWordWrap(True)
        
        # 画像表示エリア（ウィンドウ高さいっぱいに拡張）
        image_scroll = QScrollArea()
        image_scroll.setWidgetResizable(True)
        image_scroll.setMinimumHeight(750)  # さらに高くしてウィンドウいっぱいに
        
        self.current_page_display = QLabel("ページを選択してください")
        self.current_page_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_page_display.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 8px;
                padding: 20px;
                color: #7f8c8d;
                font-size: 14pt;
                background-color: white;
            }
        """)
        
        image_scroll.setWidget(self.current_page_display)
        
        # キーボードショートカット説明
        shortcut_label = QLabel(
            "💡 キーボードショートカット: Y=正解確認, N=誤検出, Space=次のページ"
        )
        shortcut_label.setStyleSheet("color: #27ae60; font-size: 9pt; font-weight: bold;")
        
        layout.addWidget(instruction_label)
        layout.addWidget(image_scroll)
        layout.addWidget(shortcut_label)
        
        return group_box
    
    def _load_page_images(self):
        """PDFからページ画像を読み込み（バックグラウンド処理）"""
        if not hasattr(self.result, 'pdf_path') or not self.result.pdf_path:
            return
        
        try:
            # PyMuPDFでPDFを開く
            doc = fitz.open(str(self.result.pdf_path))
            
            # 検出されたページの画像のみ読み込み
            for page_data in self.result.overflow_pages:
                page_number = page_data['page_number']
                
                if page_number <= len(doc):
                    page = doc[page_number - 1]  # 0-indexed
                    
                    # 高解像度で画像変換（より鮮明に）
                    mat = fitz.Matrix(3.0, 3.0)  # 3倍ズームで高解像度
                    pix = page.get_pixmap(matrix=mat, alpha=False)  # アルファチャンネル無効でより鮮明
                    
                    # QPixmapに変換
                    img_data = pix.pil_tobytes(format="PNG")
                    pixmap = QPixmap()
                    pixmap.loadFromData(img_data)
                    
                    # ページの右端3分の1のみを切り出し（溢れ確認用）
                    pixmap = self._crop_right_third(pixmap)
                    
                    # 本文幅の線を描画
                    pixmap = self._draw_text_boundary(pixmap, page_number)
                    
                    self.page_images[page_number] = pixmap
            
            doc.close()
            
        except Exception as e:
            print(f"ページ画像読み込みエラー: {e}")
    
    def _crop_right_third(self, pixmap: QPixmap) -> QPixmap:
        """ページ画像の右端3分の1を切り出し（溢れ確認用）"""
        img_width = pixmap.width()
        img_height = pixmap.height()
        
        # 右端3分の1の範囲を計算
        crop_start_x = int(img_width * 2 / 3)  # 左から3分の2の位置から開始
        crop_width = img_width - crop_start_x  # 右端まで
        
        # 切り出し実行
        cropped_pixmap = pixmap.copy(crop_start_x, 0, crop_width, img_height)
        return cropped_pixmap
    
    def _draw_text_boundary(self, pixmap: QPixmap, page_number: int) -> QPixmap:
        """ページ画像に本文幅の境界線を描画（切り出し後の座標系に対応）"""
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 赤い線で本文幅の右端を描画（太くして視認性向上）
        pen = QPen(QColor(255, 0, 0), 5)  # 赤、5px幅に拡大
        painter.setPen(pen)
        
        # 切り出し後の画像サイズ
        img_width = pixmap.width()
        img_height = pixmap.height()
        
        # 右ページ（奇数）か左ページ（偶数）かで右マージンが異なる
        is_right_page = (page_number % 2 == 1)
        
        # マージン設定（mm -> px, 3x zoom適用）
        dpi = 300 * 3  # 3倍ズーム
        mm_to_px = dpi / 25.4
        
        if is_right_page:
            right_margin_mm = 20  # 右ページの右マージン
        else:
            right_margin_mm = 15  # 左ページの右マージン
        
        right_margin_px = int(right_margin_mm * mm_to_px)
        
        # 元のページ幅（3倍ズーム）を計算
        original_page_width = int(182 * mm_to_px)  # B5判幅182mm
        
        # 切り出し開始位置（元ページの3分の2地点）
        crop_start_x = int(original_page_width * 2 / 3)
        
        # 本文幅右端の位置（切り出し後の座標系で）
        text_right_edge_original = original_page_width - right_margin_px
        text_right_edge_in_crop = text_right_edge_original - crop_start_x
        
        # 境界線が切り出し範囲内にある場合のみ描画
        if 0 <= text_right_edge_in_crop <= img_width:
            # 垂直線を描画（上下に余白を設ける）
            margin_top = int(20 * mm_to_px)  # 上マージン
            margin_bottom = int(20 * mm_to_px)  # 下マージン
            
            painter.drawLine(
                text_right_edge_in_crop, margin_top,
                text_right_edge_in_crop, img_height - margin_bottom
            )
            
            # 境界線の説明テキスト（背景付きで視認性向上）
            text_x = text_right_edge_in_crop + 10
            text_y = margin_top + 30
            
            # 白い背景の矩形を描画
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.setBrush(QColor(255, 255, 255, 200))  # 半透明の白背景
            text_rect = painter.fontMetrics().boundingRect("本文幅右端")
            painter.drawRect(text_x - 5, text_y - text_rect.height(), 
                           text_rect.width() + 10, text_rect.height() + 5)
            
            # 黒いテキストで説明を描画
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            painter.drawText(text_x, text_y, "本文幅右端")
        
        painter.end()
        return pixmap
    
    def display_page_image(self, page_number: int):
        """指定ページの画像を表示"""
        if page_number in self.page_images:
            pixmap = self.page_images[page_number]
            
            # スケール調整（より大きく表示、高品質変換）
            label_size = self.current_page_display.size()
            # 余白を少なくして画像を大きく表示
            scaled_pixmap = pixmap.scaled(
                label_size.width() - 10,  # 余白を減らして大きく表示
                label_size.height() - 10,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation  # 高品質スケーリング
            )
            
            self.current_page_display.setPixmap(scaled_pixmap)
            self.current_page_display.setText("")  # プレースホルダーテキストを削除
            
            # グループボックスのタイトルを更新
            for widget in self.findChildren(QGroupBox):
                if "ページ画像表示" in widget.title():
                    widget.setTitle(f"ページ画像表示 - ページ {page_number}")
                    break
        else:
            self.current_page_display.setText(f"ページ {page_number} の画像を読み込み中...")
    
    def keyPressEvent(self, event):
        """キーボードショートカット処理"""
        key = event.key()
        
        if key == Qt.Key.Key_Y:
            # Y: 現在選択中のページを正解として確認
            self._toggle_current_page_confirmation(True)
        elif key == Qt.Key.Key_N:
            # N: 現在選択中のページを誤検出として設定
            self._toggle_current_page_confirmation(False)
        elif key == Qt.Key.Key_Space:
            # Space: 次のページを表示
            self._show_next_page()
        else:
            super().keyPressEvent(event)
    
    def _toggle_current_page_confirmation(self, is_confirmed: bool):
        """現在表示中のページの確認状態を切り替え"""
        # 現在表示中のページ番号を取得
        current_page = self._get_current_displayed_page()
        if current_page and current_page in self.page_checkboxes:
            checkbox = self.page_checkboxes[current_page]
            checkbox.setChecked(is_confirmed)
            
            # 視覚的フィードバック
            status = "正解確認" if is_confirmed else "誤検出設定"
            print(f"ページ {current_page}: {status}")
    
    def _get_current_displayed_page(self) -> int:
        """現在表示中のページ番号を取得"""
        for widget in self.findChildren(QGroupBox):
            if "ページ画像表示" in widget.title() and " - ページ " in widget.title():
                try:
                    return int(widget.title().split("ページ ")[-1])
                except ValueError:
                    pass
        return None
    
    def _show_next_page(self):
        """次のページを表示"""
        current_page = self._get_current_displayed_page()
        if current_page:
            # 次の検出ページを探す
            page_numbers = [p['page_number'] for p in self.result.overflow_pages]
            page_numbers.sort()
            
            try:
                current_index = page_numbers.index(current_page)
                if current_index + 1 < len(page_numbers):
                    next_page = page_numbers[current_index + 1]
                    self.display_page_image(next_page)
                else:
                    # 最初のページに戻る
                    self.display_page_image(page_numbers[0])
            except ValueError:
                # 現在のページが見つからない場合は最初のページを表示
                if page_numbers:
                    self.display_page_image(page_numbers[0])
    
    def create_button_layout(self) -> QHBoxLayout:
        """ボタンレイアウト作成"""
        layout = QHBoxLayout()
        
        # 学習データ保存ボタン
        save_learning_btn = QPushButton("学習データとして保存")
        save_learning_btn.clicked.connect(self.save_learning_data)
        save_learning_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        # キャンセルボタン
        cancel_btn = QPushButton("キャンセル")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        # 結果のみ確認ボタン
        ok_btn = QPushButton("結果確認のみ")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout.addWidget(save_learning_btn)
        layout.addStretch()
        layout.addWidget(ok_btn)
        layout.addWidget(cancel_btn)
        
        return layout
    
    def get_group_box_style(self) -> str:
        """グループボックス共通スタイル"""
        return """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
        """
    
    def populate_results(self):
        """結果データを画面に反映"""
        # 結果が既に setup_ui で処理されているため、
        # 追加の処理が必要な場合はここに記述
        pass
    
    def parse_additional_pages(self) -> List[int]:
        """追加ページ番号を解析"""
        text = self.additional_pages_edit.toPlainText().strip()
        if not text:
            return []
        
        page_numbers = []
        
        # カンマ、タブ、スペース、改行で分割
        import re
        tokens = re.split(r'[,\t\s\n]+', text)
        
        for token in tokens:
            token = token.strip()
            if token.isdigit():
                page_num = int(token)
                if 1 <= page_num <= self.result.total_pages:
                    page_numbers.append(page_num)
        
        return sorted(list(set(page_numbers)))  # 重複除去・ソート
    
    def save_learning_data(self):
        """学習データを保存"""
        try:
            # 確認されたページ（チェックが入っているページ）
            confirmed_pages = []
            false_positives = []
            
            for page_number, checkbox in self.page_checkboxes.items():
                if checkbox.isChecked():
                    confirmed_pages.append(page_number)
                else:
                    false_positives.append(page_number)
            
            # 追加ページ
            additional_pages = self.parse_additional_pages()
            
            # 学習データの構築
            learning_data = {
                'pdf_path': str(self.result.pdf_path),
                'pdf_name': self.result.pdf_name,
                'detected_pages': [p['page_number'] for p in self.result.overflow_pages],
                'confirmed_pages': confirmed_pages,
                'additional_pages': additional_pages,
                'false_positives': false_positives,
                'user_notes': self.comment_edit.toPlainText().strip(),
                'app_version': '1.0.0',
                'processing_time': self.result.processing_time
            }
            
            # データベースに保存
            success = self.learning_manager.save_learning_data(learning_data)
            
            if success:
                QMessageBox.information(
                    self, 
                    "保存完了", 
                    f"学習データを保存しました。\n\n"
                    f"確認済み: {len(confirmed_pages)}件\n"
                    f"追加: {len(additional_pages)}件\n"
                    f"誤検出: {len(false_positives)}件"
                )
                
                # シグナル発出
                self.learning_data_saved.emit(learning_data)
                self.accept()
            else:
                QMessageBox.warning(self, "保存エラー", "学習データの保存に失敗しました。")
                
        except Exception as e:
            QMessageBox.critical(
                self, 
                "保存エラー", 
                f"学習データの保存中にエラーが発生しました:\n\n{str(e)}"
            )