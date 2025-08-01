"""
TechBook27 Analyzer メインウィンドウ
単一責任: アプリケーションのメインUI管理
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional
from threading import Thread, Event
import logging

from .base_window import BaseWindow, FramedSection
from .widgets import ScrollableTextOutput, FileSelector, FolderSelector, ProgressDialog
from ..core.models import ProcessingOptions, ProcessingMode, LogLevel
from ..processors.image_processor import ImageProcessor
from ..processors.word_processor import WordProcessor
from ..utils.validators import ParameterValidator
from ..utils.logger import get_logger


logger = get_logger(__name__)


class TechBook27AnalyzerWindow(BaseWindow):
    """TechBook27 Analyzerのメインウィンドウ"""
    
    def __init__(self):
        """初期化"""
        super().__init__(
            title="TechBook27 Analyzer - 統合画像・文書処理",
            width=1000,
            height=800
        )
        
        # スレッド管理
        self.current_thread: Optional[Thread] = None
        self.stop_event: Optional[Event] = None
        
        # バリデーター
        self.validator = ParameterValidator()
        
    def setup_ui(self) -> None:
        """UIをセットアップ"""
        # メインフレーム
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タブビュー
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill=tk.BOTH, expand=True)
        
        # タブを追加
        self.image_tab = self.tabview.add("画像処理")
        self.word_tab = self.tabview.add("Word文書処理")
        
        # 各タブをセットアップ
        self._setup_image_tab()
        self._setup_word_tab()
        
        # 終了ボタン
        self.exit_button = ctk.CTkButton(
            self.main_frame, 
            text="終了", 
            command=self.destroy,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.exit_button.pack(pady=10)
        
    def _setup_image_tab(self) -> None:
        """画像処理タブをセットアップ"""
        # 左右分割
        left_frame = ctk.CTkFrame(self.image_tab, width=450)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        right_frame = ctk.CTkFrame(self.image_tab)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 処理モード選択
        mode_section = FramedSection(left_frame, "処理モード")
        mode_frame = mode_section.get_content_frame()
        
        self.processing_mode = ctk.StringVar(value="folder")
        ctk.CTkRadioButton(
            mode_frame, 
            text="フォルダ処理", 
            variable=self.processing_mode, 
            value="folder",
            command=self._update_mode_ui
        ).pack(side=tk.LEFT, padx=10)
        
        ctk.CTkRadioButton(
            mode_frame, 
            text="ファイル処理", 
            variable=self.processing_mode, 
            value="file",
            command=self._update_mode_ui
        ).pack(side=tk.LEFT, padx=10)
        
        mode_section.pack(fill=tk.X, pady=5)
        
        # ファイル/フォルダ選択
        selection_section = FramedSection(left_frame, "対象選択")
        selection_frame = selection_section.get_content_frame()
        
        # フォルダ選択
        self.folder_selector = FolderSelector(selection_frame)
        self.folder_selector.pack(fill=tk.X, pady=5)
        
        # ファイル選択（初期は非表示）
        self.file_selector = FileSelector(
            selection_frame,
            file_types=[("画像ファイル", "*.jpg *.jpeg *.png")]
        )
        self.file_selector.pack(fill=tk.X, pady=5)
        self.file_selector.pack_forget()
        
        selection_section.pack(fill=tk.X, pady=5)
        
        # パラメータ設定
        param_section = FramedSection(left_frame, "パラメータ")
        param_frame = param_section.get_content_frame()
        
        # 最大画素数
        pixels_frame = ctk.CTkFrame(param_frame)
        pixels_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(pixels_frame, text="最大画素数(万画素):").pack(side=tk.LEFT, padx=5)
        self.max_pixels_var = ctk.StringVar(value="400")
        ctk.CTkEntry(pixels_frame, textvariable=self.max_pixels_var, width=100).pack(side=tk.LEFT, padx=5)
        
        # 解像度
        res_frame = ctk.CTkFrame(param_frame)
        res_frame.pack(fill=tk.X, pady=5)
        
        ctk.CTkLabel(res_frame, text="解像度(DPI):").pack(side=tk.LEFT, padx=5)
        self.resolution_var = ctk.StringVar(value="100")
        ctk.CTkEntry(res_frame, textvariable=self.resolution_var, width=100).pack(side=tk.LEFT, padx=5)
        
        param_section.pack(fill=tk.X, pady=5)
        
        # オプション設定
        option_section = FramedSection(left_frame, "処理オプション")
        option_frame = option_section.get_content_frame()
        
        # チェックボックス変数
        self.image_options = {
            'remove_profile': ctk.BooleanVar(value=False),
            'grayscale': ctk.BooleanVar(value=False),
            'change_resolution': ctk.BooleanVar(value=True),
            'resize': ctk.BooleanVar(value=True),
            'backup': ctk.BooleanVar(value=True),
            'png_to_jpg': ctk.BooleanVar(value=True)
        }
        
        # チェックボックス作成
        option_labels = {
            'remove_profile': "カラープロファイル除去",
            'grayscale': "グレースケール変換",
            'change_resolution': "指定解像度への変更",
            'resize': "最大画素数でリサイズ",
            'backup': "処理前の自動バックアップ",
            'png_to_jpg': "PNG→JPG変換"
        }
        
        for key, label in option_labels.items():
            ctk.CTkCheckBox(
                option_frame,
                text=label,
                variable=self.image_options[key]
            ).pack(anchor="w", pady=2)
            
        option_section.pack(fill=tk.X, pady=5)
        
        # 実行ボタン
        self.image_start_button = ctk.CTkButton(
            left_frame,
            text="画像処理開始",
            command=self._start_image_processing,
            height=40
        )
        self.image_start_button.pack(pady=10)
        
        # 出力エリア
        output_section = FramedSection(right_frame, "処理ログ")
        self.image_output = ScrollableTextOutput(
            output_section.get_content_frame(),
            height=600
        )
        self.image_output.pack(fill=tk.BOTH, expand=True)
        output_section.pack(fill=tk.BOTH, expand=True)
        
    def _setup_word_tab(self) -> None:
        """Word文書処理タブをセットアップ"""
        # 左右分割
        left_frame = ctk.CTkFrame(self.word_tab, width=450)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        right_frame = ctk.CTkFrame(self.word_tab)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ファイル選択
        file_section = FramedSection(left_frame, "ZIPファイル選択")
        self.zip_selector = FileSelector(
            file_section.get_content_frame(),
            label="ZIPファイル:",
            file_types=[("ZIP files", "*.zip")]
        )
        self.zip_selector.pack(fill=tk.X, pady=5)
        file_section.pack(fill=tk.X, pady=5)
        
        # 処理説明
        info_section = FramedSection(left_frame, "処理内容")
        info_frame = info_section.get_content_frame()
        
        info_text = """このツールは、ZIPファイル内の全ての
Word文書（.docx）の先頭行を削除します。

処理後、新しいZIPファイルが作成されます。
元のファイルは変更されません。"""
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            justify="left"
        ).pack(pady=10, padx=10)
        
        info_section.pack(fill=tk.X, pady=5)
        
        # 実行ボタン
        self.word_start_button = ctk.CTkButton(
            left_frame,
            text="先頭行削除処理開始",
            command=self._start_word_processing,
            height=40
        )
        self.word_start_button.pack(pady=10)
        
        # 出力エリア
        output_section = FramedSection(right_frame, "処理ログ")
        self.word_output = ScrollableTextOutput(
            output_section.get_content_frame(),
            height=600
        )
        self.word_output.pack(fill=tk.BOTH, expand=True)
        output_section.pack(fill=tk.BOTH, expand=True)
        
    def _update_mode_ui(self) -> None:
        """処理モードに応じてUIを更新"""
        if self.processing_mode.get() == "folder":
            self.file_selector.pack_forget()
            self.folder_selector.pack(fill=tk.X, pady=5)
        else:
            self.folder_selector.pack_forget()
            self.file_selector.pack(fill=tk.X, pady=5)
            
    def _start_image_processing(self) -> None:
        """画像処理を開始"""
        # 既存の処理を停止
        self._stop_current_processing()
        
        # 出力をクリア
        self.image_output.clear()
        
        # パラメータ検証
        resolution = self.validator.validate_resolution(self.resolution_var.get())
        if resolution is None:
            self.show_error("入力エラー", "解像度は1〜600の数値で入力してください")
            return
            
        max_pixels = self.validator.validate_max_pixels(self.max_pixels_var.get())
        if max_pixels is None:
            self.show_error("入力エラー", "最大画素数は1〜10000の数値で入力してください")
            return
            
        # 処理オプションを作成
        options = ProcessingOptions(
            remove_profile=self.image_options['remove_profile'].get(),
            grayscale=self.image_options['grayscale'].get(),
            change_resolution=self.image_options['change_resolution'].get(),
            resize=self.image_options['resize'].get(),
            backup=self.image_options['backup'].get(),
            png_to_jpg=self.image_options['png_to_jpg'].get(),
            max_pixels=str(max_pixels),
            resolution=resolution
        )
        
        # 処理対象を取得
        if self.processing_mode.get() == "folder":
            target = self.folder_selector.get_path()
            if not target:
                self.show_error("入力エラー", "フォルダを選択してください")
                return
        else:
            target = self.file_selector.get_path()
            if not target:
                self.show_error("入力エラー", "画像ファイルを選択してください")
                return
                
        # 処理スレッドを開始
        self.stop_event = Event()
        self.current_thread = Thread(
            target=self._run_image_processing,
            args=(target, options, self.processing_mode.get() == "folder")
        )
        self.current_thread.start()
        
    def _run_image_processing(self, target: str, options: ProcessingOptions, is_folder: bool) -> None:
        """画像処理を実行（別スレッド）"""
        try:
            processor = ImageProcessor(options)
            
            self.image_output.append("画像処理を開始します...")
            self.image_output.append(f"対象: {target}")
            self.image_output.append("有効なオプション:")
            
            # オプション表示
            option_names = {
                'remove_profile': "カラープロファイル除去",
                'grayscale': "グレースケール変換",
                'change_resolution': "指定解像度への変更",
                'resize': "最大画素数でリサイズ",
                'backup': "処理前の自動バックアップ",
                'png_to_jpg': "PNG→JPG変換"
            }
            
            for key, value in options.to_dict().items():
                if value and key in option_names:
                    self.image_output.append(f"  - {option_names[key]}")
                    
            self.image_output.append("")
            
            # 処理実行
            if is_folder:
                result = processor.process_folder(target)
            else:
                result = processor.process_image(target)
                
            # 結果表示
            for message in result.messages:
                self.image_output.append(message, timestamp=False)
                
            if result.success:
                self.image_output.append(
                    f"\n処理完了: {result.processed_count}ファイル処理, "
                    f"{result.error_count}エラー, {result.warning_count}警告"
                )
            else:
                self.image_output.append("\n処理中にエラーが発生しました")
                
        except Exception as e:
            logger.exception("画像処理エラー")
            self.image_output.append(f"エラー: {str(e)}")
            
    def _start_word_processing(self) -> None:
        """Word文書処理を開始"""
        # 既存の処理を停止
        self._stop_current_processing()
        
        # 出力をクリア
        self.word_output.clear()
        
        # ZIPファイルを取得
        zip_path = self.zip_selector.get_path()
        if not zip_path:
            self.show_error("入力エラー", "ZIPファイルを選択してください")
            return
            
        # 処理スレッドを開始
        self.stop_event = Event()
        self.current_thread = Thread(
            target=self._run_word_processing,
            args=(zip_path,)
        )
        self.current_thread.start()
        
    def _run_word_processing(self, zip_path: str) -> None:
        """Word文書処理を実行（別スレッド）"""
        try:
            processor = WordProcessor()
            
            self.word_output.append("Word文書処理を開始します...")
            self.word_output.append(f"対象: {zip_path}")
            self.word_output.append("")
            
            # 処理実行
            result = processor.process_zip_file(zip_path)
            
            # 結果表示
            for message in result.messages:
                self.word_output.append(message, timestamp=False)
                
            if result.success:
                self.word_output.append(
                    f"\n処理完了: {result.processed_count}ファイル処理"
                )
                if 'output_path' in result.details:
                    self.word_output.append(
                        f"出力ファイル: {result.details['output_path']}"
                    )
            else:
                self.word_output.append("\n処理中にエラーが発生しました")
                
        except Exception as e:
            logger.exception("Word文書処理エラー")
            self.word_output.append(f"エラー: {str(e)}")
            
    def _stop_current_processing(self) -> None:
        """現在の処理を停止"""
        if self.current_thread and self.current_thread.is_alive():
            if self.stop_event:
                self.stop_event.set()
            self.current_thread.join(timeout=1.0)
            
    def confirm_close(self) -> bool:
        """終了確認"""
        if self.current_thread and self.current_thread.is_alive():
            return self.ask_yes_no(
                "確認",
                "処理中のタスクがあります。終了しますか？"
            )
        return True