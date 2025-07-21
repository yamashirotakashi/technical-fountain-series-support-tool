"""メインウィンドウモジュール - Google Sheets機能無効版"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QStatusBar, QMessageBox,
                             QInputDialog, QLineEdit, QAction, QPushButton, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from gui.components.input_panel import InputPanel
from gui.components.log_panel import LogPanel
from gui.components.progress_bar import ProgressPanel
from utils.logger import get_logger


class MainWindowNoGoogle(QMainWindow):
    """アプリケーションのメインウィンドウ - Google Sheets機能無効版"""
    
    def __init__(self):
        """MainWindowを初期化"""
        super().__init__()
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
    
    def setup_ui(self):
        """UIを構築"""
        self.setWindowTitle("技術の泉シリーズ制作支援ツール (Google Sheets無効版)")
        self.setGeometry(100, 100, 1200, 800)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)
        
        # 注意メッセージ
        warning_label = QLabel(
            "⚠️ 注意: Google Sheets機能が無効化されています。\n"
            "依存関係の問題を解決後、通常版(main.py)をご利用ください。"
        )
        warning_label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(warning_label)
        
        # 上部：入力パネル（無効化）
        self.input_panel = InputPanel()
        self.input_panel.setEnabled(False)
        
        # 中央：スプリッター（ログパネル）
        splitter = QSplitter(Qt.Vertical)
        
        # ログパネル
        self.log_panel = LogPanel()
        
        # 進捗パネル
        self.progress_panel = ProgressPanel()
        
        # スプリッターに追加
        splitter.addWidget(self.log_panel)
        splitter.setStretchFactor(0, 1)
        
        # テスト機能ボタン
        test_layout = QHBoxLayout()
        test_dialog_btn = QPushButton("FilePasteDialog テスト")
        test_dialog_btn.clicked.connect(self.test_file_paste_dialog)
        test_layout.addWidget(test_dialog_btn)
        test_layout.addStretch()
        
        # レイアウトに追加
        main_layout.addWidget(self.input_panel)
        main_layout.addLayout(test_layout)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.progress_panel)
        
        # スタイル設定
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def setup_menu(self):
        """メニューバーを設定"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル(&F)")
        
        # 終了アクション
        exit_action = QAction("終了(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ツールメニュー
        tools_menu = menubar.addMenu("ツール(&T)")
        
        # ログクリアアクション
        clear_log_action = QAction("ログクリア(&C)", self)
        clear_log_action.triggered.connect(self.log_panel.clear_logs)
        tools_menu.addAction(clear_log_action)
        
        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ(&H)")
        
        # バージョン情報アクション
        about_action = QAction("バージョン情報(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_statusbar(self):
        """ステータスバーを設定"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("準備完了 (Google Sheets機能無効)")
    
    def test_file_paste_dialog(self):
        """FilePasteDialogのテスト"""
        try:
            from pathlib import Path
            from gui.dialogs.file_paste_dialog import FilePasteDialog
            
            # テスト用のダミーファイルリスト
            test_files = [
                Path("test_file1.docx"),
                Path("test_file2.docx"),
                Path("test_file3.docx")
            ]
            
            # ダイアログを表示
            dialog = FilePasteDialog(test_files, "N02279", self)
            result = dialog.exec_()
            
            if result == dialog.Accepted:
                self.log_panel.append_log("FilePasteDialog テスト: 正常完了", "INFO")
            else:
                self.log_panel.append_log("FilePasteDialog テスト: キャンセル", "WARNING")
                
        except Exception as e:
            self.log_panel.append_log(f"FilePasteDialog テストエラー: {e}", "ERROR")
            QMessageBox.critical(self, "エラー", f"テスト実行エラー:\n{e}")
    
    def show_about(self):
        """バージョン情報を表示"""
        QMessageBox.about(
            self,
            "バージョン情報",
            "技術の泉シリーズ制作支援ツール\\n\\n"
            "バージョン: 1.0.0 (Google Sheets無効版)\\n"
            "開発: Technical Fountain Team\\n\\n"
            "このツールは技術の泉シリーズの制作プロセスを\\n"
            "自動化・効率化するために開発されました。"
        )