"""
TechDisposal Analyzer メインウィンドウ - Qt6ベース
単一責任: アプリケーションのメインUI管理
"""
from typing import Optional
from threading import Thread, Event
import logging

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QFrame, QRadioButton, QButtonGroup, QCheckBox,
    QLineEdit, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from .base_window import BaseWindow, FramedSection
from .widgets import ScrollableTextOutput, FileSelector, FolderSelector, ProgressDialog, OptionsPanel
from ..core.models import ProcessingOptions, ProcessingMode, LogLevel
from ..processors.image_processor import ImageProcessor
from ..processors.word_processor import WordProcessor
from ..utils.validators import ParameterValidator
from ..utils.logger import get_logger


logger = get_logger(__name__)


class ImageProcessingThread(QThread):
    """画像処理用スレッド"""
    
    message_ready = pyqtSignal(str)
    finished_processing = pyqtSignal(bool, str)
    
    def __init__(self, target: str, options: ProcessingOptions, is_folder: bool):
        super().__init__()
        self.target = target
        self.options = options
        self.is_folder = is_folder
        self._stop_requested = False
        
    def run(self):
        """処理実行"""
        try:
            processor = ImageProcessor(self.options)
            
            self.message_ready.emit("画像処理を開始します...")
            self.message_ready.emit(f"対象: {self.target}")
            
            # 処理実行
            if self.is_folder:
                result = processor.process_folder(self.target)
            else:
                result = processor.process_image(self.target)
                
            # 結果表示
            for message in result.messages:
                self.message_ready.emit(message)
                
            if result.success:
                summary = f"\n処理完了: {result.processed_count}ファイル処理, {result.error_count}エラー, {result.warning_count}警告"
                self.message_ready.emit(summary)
                self.finished_processing.emit(True, "処理が完了しました")
            else:
                self.message_ready.emit("\n処理中にエラーが発生しました")
                self.finished_processing.emit(False, "処理中にエラーが発生しました")
                
        except Exception as e:
            logger.exception("画像処理エラー")
            self.message_ready.emit(f"エラー: {str(e)}")
            self.finished_processing.emit(False, f"エラー: {str(e)}")
            
    def stop(self):
        """処理停止"""
        self._stop_requested = True
        self.terminate()
        self.wait()


class WordProcessingThread(QThread):
    """Word文書処理用スレッド"""
    
    message_ready = pyqtSignal(str)
    finished_processing = pyqtSignal(bool, str)
    
    def __init__(self, zip_path: str):
        super().__init__()
        self.zip_path = zip_path
        self._stop_requested = False
        
    def run(self):
        """処理実行"""
        try:
            processor = WordProcessor()
            
            self.message_ready.emit("Word文書処理を開始します...")
            self.message_ready.emit(f"対象: {self.zip_path}")
            
            # 処理実行
            result = processor.process_zip_file(self.zip_path)
            
            # 結果表示
            for message in result.messages:
                self.message_ready.emit(message)
                
            if result.success:
                summary = f"\n処理完了: {result.processed_count}ファイル処理"
                self.message_ready.emit(summary)
                if 'output_path' in result.details:
                    self.message_ready.emit(f"出力ファイル: {result.details['output_path']}")
                self.finished_processing.emit(True, "処理が完了しました")
            else:
                self.message_ready.emit("\n処理中にエラーが発生しました")
                self.finished_processing.emit(False, "処理中にエラーが発生しました")
                
        except Exception as e:
            logger.exception("Word文書処理エラー")
            self.message_ready.emit(f"エラー: {str(e)}")
            self.finished_processing.emit(False, f"エラー: {str(e)}")
            
    def stop(self):
        """処理停止"""
        self._stop_requested = True
        self.terminate()
        self.wait()


class TechDisposalAnalyzerWindow(BaseWindow):
    """TechDisposal Analyzerのメインウィンドウ - Qt6ベース"""
    
    def __init__(self):
        """初期化"""
        super().__init__(
            title="TechDisposal Analyzer - 統合画像・文書処理",
            width=1000,
            height=800
        )
        
        # スレッド管理
        self.image_thread: Optional[ImageProcessingThread] = None
        self.word_thread: Optional[WordProcessingThread] = None
        
        # バリデーター
        self.validator = ParameterValidator()
        
        # UI変数
        self.processing_mode = "folder"
        self.image_options = {}
        
    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        # タブウィジェット
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # タブを作成
        self.image_tab = QWidget()
        self.word_tab = QWidget()
        
        self.tab_widget.addTab(self.image_tab, "画像処理")
        self.tab_widget.addTab(self.word_tab, "Word文書処理")
        
        # 各タブをセットアップ
        self._setup_image_tab()
        self._setup_word_tab()
        
    def _setup_image_tab(self) -> None:
        """画像処理タブをセットアップ"""
        # メインレイアウト
        main_layout = QHBoxLayout(self.image_tab)
        
        # 左側コントロールパネル
        left_frame = QFrame()
        left_frame.setFixedWidth(450)
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout(left_frame)
        
        # 右側出力エリア
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        
        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)
        
        # 処理モード選択
        mode_section = FramedSection("処理モード")
        mode_layout = QHBoxLayout()
        
        self.mode_group = QButtonGroup()
        self.folder_radio = QRadioButton("フォルダ処理")
        self.file_radio = QRadioButton("ファイル処理")
        
        self.folder_radio.setChecked(True)
        self.processing_mode = "folder"
        
        self.mode_group.addButton(self.folder_radio, 0)
        self.mode_group.addButton(self.file_radio, 1)
        self.mode_group.buttonClicked.connect(self._update_mode_ui)
        
        mode_layout.addWidget(self.folder_radio)
        mode_layout.addWidget(self.file_radio)
        mode_section.add_layout(mode_layout)
        
        left_layout.addWidget(mode_section)
        
        # ファイル/フォルダ選択
        selection_section = FramedSection("対象選択")
        
        # フォルダ選択
        self.folder_selector = FolderSelector("フォルダ選択:")
        selection_section.add_widget(self.folder_selector)
        
        # ファイル選択（初期は非表示）
        self.file_selector = FileSelector(
            "ファイル選択:",
            "Image Files (*.jpg *.jpeg *.png);;All Files (*)"
        )
        self.file_selector.setVisible(False)
        selection_section.add_widget(self.file_selector)
        
        left_layout.addWidget(selection_section)
        
        # パラメータ設定
        param_section = FramedSection("パラメータ")
        
        # 最大画素数
        pixels_layout = QHBoxLayout()
        pixels_layout.addWidget(QLabel("最大画素数(万画素):"))
        self.max_pixels_edit = QLineEdit("400")
        self.max_pixels_edit.setFixedWidth(100)
        pixels_layout.addWidget(self.max_pixels_edit)
        pixels_layout.addStretch()
        param_section.add_layout(pixels_layout)
        
        # 解像度
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("解像度(DPI):"))
        self.resolution_edit = QLineEdit("100")
        self.resolution_edit.setFixedWidth(100)
        res_layout.addWidget(self.resolution_edit)
        res_layout.addStretch()
        param_section.add_layout(res_layout)
        
        left_layout.addWidget(param_section)
        
        # オプション設定
        option_section = FramedSection("処理オプション")
        
        # チェックボックス作成
        option_labels = {
            'remove_profile': ("カラープロファイル除去", False),
            'grayscale': ("グレースケール変換", False),
            'change_resolution': ("指定解像度への変更", True),
            'resize': ("最大画素数でリサイズ", True),
            'backup': ("処理前の自動バックアップ", True),
            'png_to_jpg': ("PNG→JPG変換", True)
        }
        
        self.image_options = {}
        for key, (label, default) in option_labels.items():
            checkbox = QCheckBox(label)
            checkbox.setChecked(default)
            self.image_options[key] = checkbox
            option_section.add_widget(checkbox)
            
        left_layout.addWidget(option_section)
        
        # スペーサー
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # 実行ボタン
        self.image_start_button = QPushButton("画像処理開始")
        self.image_start_button.setMinimumHeight(40)
        self.image_start_button.clicked.connect(self._start_image_processing)
        left_layout.addWidget(self.image_start_button)
        
        # 出力エリア
        output_section = FramedSection("処理ログ")
        self.image_output = ScrollableTextOutput()
        output_section.add_widget(self.image_output)
        right_layout.addWidget(output_section)
        
    def _setup_word_tab(self) -> None:
        """Word文書処理タブをセットアップ"""
        # メインレイアウト
        main_layout = QHBoxLayout(self.word_tab)
        
        # 左側コントロールパネル
        left_frame = QFrame()
        left_frame.setFixedWidth(450)
        left_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_layout = QVBoxLayout(left_frame)
        
        # 右側出力エリア
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_layout = QVBoxLayout(right_frame)
        
        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)
        
        # ファイル選択
        file_section = FramedSection("ZIPファイル選択")
        self.zip_selector = FileSelector(
            "ZIPファイル:",
            "ZIP Files (*.zip);;All Files (*)"
        )
        file_section.add_widget(self.zip_selector)
        left_layout.addWidget(file_section)
        
        # 処理説明
        info_section = FramedSection("処理内容")
        info_text = """このツールは、ZIPファイル内の全ての
Word文書（.docx）の先頭行を削除します。

処理後、新しいZIPファイルが作成されます。
元のファイルは変更されません。"""
        
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_section.add_widget(info_label)
        left_layout.addWidget(info_section)
        
        # スペーサー
        left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # 実行ボタン
        self.word_start_button = QPushButton("先頭行削除処理開始")
        self.word_start_button.setMinimumHeight(40)
        self.word_start_button.clicked.connect(self._start_word_processing)
        left_layout.addWidget(self.word_start_button)
        
        # 出力エリア
        output_section = FramedSection("処理ログ")
        self.word_output = ScrollableTextOutput()
        output_section.add_widget(self.word_output)
        right_layout.addWidget(output_section)
        
    def _update_mode_ui(self) -> None:
        """処理モードに応じてUIを更新"""
        if self.folder_radio.isChecked():
            self.processing_mode = "folder"
            self.file_selector.setVisible(False)
            self.folder_selector.setVisible(True)
        else:
            self.processing_mode = "file"
            self.folder_selector.setVisible(False)
            self.file_selector.setVisible(True)
            
    def _start_image_processing(self) -> None:
        """画像処理を開始"""
        # 既存の処理を停止
        self._stop_current_processing()
        
        # 出力をクリア
        self.image_output.clear_output()
        
        # パラメータ検証
        resolution = self.validator.validate_resolution(self.resolution_edit.text())
        if resolution is None:
            self.show_error("入力エラー", "解像度は1〜600の数値で入力してください")
            return
            
        max_pixels = self.validator.validate_max_pixels(self.max_pixels_edit.text())
        if max_pixels is None:
            self.show_error("入力エラー", "最大画素数は1〜10000の数値で入力してください")
            return
            
        # 処理オプションを作成
        options = ProcessingOptions(
            remove_profile=self.image_options['remove_profile'].isChecked(),
            grayscale=self.image_options['grayscale'].isChecked(),
            change_resolution=self.image_options['change_resolution'].isChecked(),
            resize=self.image_options['resize'].isChecked(),
            backup=self.image_options['backup'].isChecked(),
            png_to_jpg=self.image_options['png_to_jpg'].isChecked(),
            max_pixels=str(max_pixels),
            resolution=resolution
        )
        
        # 処理対象を取得
        if self.processing_mode == "folder":
            target = self.folder_selector.get_folder_path()
            if not target:
                self.show_error("入力エラー", "フォルダを選択してください")
                return
        else:
            target = self.file_selector.get_file_path()
            if not target:
                self.show_error("入力エラー", "画像ファイルを選択してください")
                return
                
        # 処理スレッドを開始
        self.image_thread = ImageProcessingThread(target, options, self.processing_mode == "folder")
        self.image_thread.message_ready.connect(self.image_output.add_message)
        self.image_thread.finished_processing.connect(self._on_image_processing_finished)
        self.image_thread.start()
        
        # ボタンを無効化
        self.image_start_button.setEnabled(False)
        self.image_start_button.setText("処理中...")
        
    def _on_image_processing_finished(self, success: bool, message: str):
        """画像処理完了時の処理"""
        self.image_start_button.setEnabled(True)
        self.image_start_button.setText("画像処理開始")
        
        if success:
            self.show_info("完了", "画像処理が完了しました")
        else:
            self.show_error("エラー", message)
        
            
    def _start_word_processing(self) -> None:
        """Word文書処理を開始"""
        # 既存の処理を停止
        self._stop_current_processing()
        
        # 出力をクリア
        self.word_output.clear_output()
        
        # ZIPファイルを取得
        zip_path = self.zip_selector.get_file_path()
        if not zip_path:
            self.show_error("入力エラー", "ZIPファイルを選択してください")
            return
            
        # 処理スレッドを開始
        self.word_thread = WordProcessingThread(zip_path)
        self.word_thread.message_ready.connect(self.word_output.add_message)
        self.word_thread.finished_processing.connect(self._on_word_processing_finished)
        self.word_thread.start()
        
        # ボタンを無効化
        self.word_start_button.setEnabled(False)
        self.word_start_button.setText("処理中...")
        
    def _on_word_processing_finished(self, success: bool, message: str):
        """Word文書処理完了時の処理"""
        self.word_start_button.setEnabled(True)
        self.word_start_button.setText("先頭行削除処理開始")
        
        if success:
            self.show_info("完了", "Word文書処理が完了しました")
        else:
            self.show_error("エラー", message)
        
            
    def _stop_current_processing(self) -> None:
        """現在の処理を停止"""
        if self.image_thread and self.image_thread.isRunning():
            self.image_thread.stop()
            
        if self.word_thread and self.word_thread.isRunning():
            self.word_thread.stop()
            
    def confirm_close(self) -> bool:
        """終了確認"""
        is_processing = (
            (self.image_thread and self.image_thread.isRunning()) or
            (self.word_thread and self.word_thread.isRunning())
        )
        
        if is_processing:
            return self.ask_yes_no(
                "確認",
                "処理中のタスクがあります。終了しますか？"
            )
        return True