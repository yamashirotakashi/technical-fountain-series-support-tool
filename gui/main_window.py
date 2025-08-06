"""メインウィンドウモジュール"""
from __future__ import annotations
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QStatusBar, QMessageBox,
                             QInputDialog, QLineEdit, QDialog)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QIcon, QAction

from gui.components.input_panel import InputPanel
from gui.components.log_panel import LogPanel
from gui.components.progress_bar import ProgressPanel
from gui.dialogs import FolderSelectorDialog
from gui.dialogs.simple_file_selector_dialog import SimpleFileSelectorDialog
from gui.dialogs.process_mode_dialog import ProcessModeDialog
from gui.dialogs.warning_dialog import WarningDialog
from core.workflow_processor import WorkflowProcessor
from core.api_processor import ApiProcessor
from utils.logger import get_logger
from pathlib import Path
import os


class ProcessWorker(QThread):
    """バックグラウンド処理用のワーカースレッド"""
    
    progress_updated = pyqtSignal(int)
    log_message = pyqtSignal(str, str)
    status_updated = pyqtSignal(str)
    confirmation_needed = pyqtSignal(str, str)
    folder_selection_needed = pyqtSignal(object, str, object)  # repo_path, repo_name, default_folder
    file_placement_confirmation_needed = pyqtSignal(str, list, object)  # honbun_folder_path, file_list, callback
    warning_dialog_needed = pyqtSignal(list, str)  # messages, result_type
    finished = pyqtSignal()
    
    def __init__(self, n_codes, email_password=None, process_mode="traditional"):
        super().__init__()
        self.n_codes = n_codes
        self.email_password = email_password
        self.process_mode = process_mode
        self.workflow_processor = None
        self.api_processor = None
        self.logger = get_logger(__name__)
    
    def run(self):
        """処理を実行"""
        try:
            # WorkflowProcessorを作成（処理方式を渡す）
            self.workflow_processor = WorkflowProcessor(
                email_password=self.email_password,
                process_mode=self.process_mode
            )
            
            # シグナルを接続
            self.workflow_processor.log_message.connect(self.log_message.emit)
            self.workflow_processor.progress_updated.connect(self.progress_updated.emit)
            self.workflow_processor.status_updated.connect(self.status_updated.emit)
            self.workflow_processor.folder_selection_needed.connect(self.folder_selection_needed.emit)
            self.workflow_processor.file_placement_confirmation_needed.connect(self.file_placement_confirmation_needed.emit)
            self.workflow_processor.warning_dialog_needed.connect(self.warning_dialog_needed.emit)
            
            # 処理を実行
            self.workflow_processor.process_n_codes(self.n_codes)
            
        except Exception as e:
            self.logger.error(f"処理エラー: {e}", exc_info=True)
            self.log_message.emit(f"エラーが発生しました: {str(e)}", "ERROR")
        finally:
            if self.workflow_processor:
                self.workflow_processor.cleanup()
            self.finished.emit()


class MainWindow(QMainWindow):
    """アプリケーションのメインウィンドウ"""
    
    def __init__(self):
        """MainWindowを初期化"""
        super().__init__()
        self.worker_thread = None
        self.error_detector_worker = None
        self.preflight_dialog = None
        self.process_mode = ProcessModeDialog.MODE_API  # デフォルトはAPI方式
        # Gmail API方式をデフォルトにする場合は以下をコメントアウト解除
        # self.process_mode = ProcessModeDialog.MODE_GMAIL_API
        
        # ConfigManagerを初期化
        self.init_config_manager()
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.connect_signals()
        
        # 起動時チェック実行
        self.perform_startup_checks()
    
    def init_config_manager(self):
        """ConfigManagerを初期化"""
        try:
            from src.slack_pdf_poster import ConfigManager
            self.config_manager = ConfigManager()
            
            # 設定検証を実行
            validation_result = self.config_manager.validate_config()
            errors = validation_result.get('errors', [])
            missing_vars = validation_result.get('missing_env_vars', [])
            
            if errors or missing_vars:
                print(f"[WARNING] 設定に問題があります: {len(errors)}エラー, {len(missing_vars)}不足環境変数")
            else:
                print("[SUCCESS] ConfigManager初期化完了")
                
        except Exception as e:
            print(f"[ERROR] ConfigManager初期化エラー: {e}")
            # フォールバック: None設定でも動作するように
            self.config_manager = None
    
    def perform_startup_checks(self):
        """起動時チェックを実行"""
        try:
            # ハードコーディング検知チェック（設定で有効な場合）
            if (self.config_manager and 
                self.config_manager.get('security.hardcoding_scan_on_startup', False)):
                self.run_hardcoding_scan()
            
            # 設定検証チェック
            if (self.config_manager and 
                self.config_manager.get('security.validate_config_on_startup', True)):
                self.validate_startup_config()
                
        except Exception as e:
            print(f"❌ 起動時チェックエラー: {e}")
    
    def run_hardcoding_scan(self):
        """ハードコーディングスキャンを実行"""
        try:
            from src.slack_pdf_poster import HardcodingDetector
            from pathlib import Path
            
            detector = HardcodingDetector()
            
            # プロジェクトルートのPythonファイルをスキャン
            project_root = Path(__file__).parent.parent
            python_files = list(project_root.rglob("*.py"))
            
            # main GUI実行時はクイックスキャン（主要ファイルのみ）
            key_files = [f for f in python_files if any(
                keyword in f.name for keyword in ['main', 'config', 'api', 'slack', 'error']
            )][:5]  # 最大5ファイル
            
            if key_files:
                results = detector.scan_multiple_files(key_files)
                total_detections = sum(len(detections) for file_results in results.values() 
                                     for detections in file_results.values())
                
                if total_detections > 0:
                    print(f"🔍 ハードコーディング検知: {total_detections}個検出")
                else:
                    print("✅ ハードコーディング検知: 問題なし")
                    
        except Exception as e:
            print(f"❌ ハードコーディングスキャンエラー: {e}")
    
    def validate_startup_config(self):
        """起動時設定検証を実行"""
        try:
            if self.config_manager:
                validation_result = self.config_manager.validate_config()
                errors = validation_result.get('errors', [])
                warnings = validation_result.get('warnings', [])
                missing_vars = validation_result.get('missing_env_vars', [])
                
                if errors:
                    print(f"❌ 設定エラー: {len(errors)}件")
                elif warnings or missing_vars:
                    print(f"⚠️ 設定警告: {len(warnings)}警告, {len(missing_vars)}不足環境変数")
                else:
                    print("✅ 設定検証: 問題なし")
        except Exception as e:
            print(f"❌ 設定検証エラー: {e}")
    
    def setup_ui(self):
        """UIを構築"""
        self.setWindowTitle("技術の泉シリーズ制作支援ツール")
        self.setGeometry(100, 100, 1200, 800)
        
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)
        
        # 上部：入力パネル
        self.input_panel = InputPanel()
        
        # 中央：スプリッター（ログパネル）
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # ログパネル
        self.log_panel = LogPanel()
        
        # 進捗パネル
        self.progress_panel = ProgressPanel()
        
        # スプリッターに追加
        splitter.addWidget(self.log_panel)
        splitter.setStretchFactor(0, 1)
        
        # レイアウトに追加
        main_layout.addWidget(self.input_panel)
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
        
        # セパレータ
        tools_menu.addSeparator()
        
        # 設定アクション
        settings_action = QAction("設定(&S)", self)
        settings_action.triggered.connect(self.show_comprehensive_settings)
        tools_menu.addAction(settings_action)
        
        # リポジトリ設定アクション
        repo_settings_action = QAction("リポジトリ設定(&R)", self)
        repo_settings_action.triggered.connect(self.show_repository_settings)
        tools_menu.addAction(repo_settings_action)
        
        # セパレータ
        tools_menu.addSeparator()
        
        # ハードコーディングスキャンアクション
        hardcoding_scan_action = QAction("ハードコーディングスキャン(&H)", self)
        hardcoding_scan_action.triggered.connect(self.show_hardcoding_scan_dialog)
        tools_menu.addAction(hardcoding_scan_action)
        
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
        self.status_bar.showMessage("準備完了")
    
    def connect_signals(self):
        """シグナルを接続"""
        # 入力パネルからのシグナル
        self.input_panel.process_requested.connect(self.start_processing)
        self.input_panel.settings_requested.connect(self.show_process_mode_dialog)
        self.input_panel.pdf_post_requested.connect(self.start_pdf_post)
        # self.input_panel.preflight_requested.connect(self.show_preflight_check)  # 削除
        self.input_panel.error_check_requested.connect(self.start_error_detection)
    
    @pyqtSlot(list)
    def start_processing(self, n_codes):
        """
        処理を開始
        
        Args:
            n_codes: 処理するNコードのリスト
        """
        # まず処理方式を選択
        dialog = ProcessModeDialog(self)
        # 現在の処理方式を反映
        if self.process_mode == ProcessModeDialog.MODE_TRADITIONAL:
            dialog.traditional_radio.setChecked(True)
        elif self.process_mode == ProcessModeDialog.MODE_API:
            dialog.api_radio.setChecked(True)
        elif self.process_mode == ProcessModeDialog.MODE_GMAIL_API:
            dialog.gmail_api_radio.setChecked(True)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # 選択された処理方式を取得
        self.process_mode = dialog.get_selected_mode()
        
        # モードテキストマッピング
        mode_text_map = {
            ProcessModeDialog.MODE_API: "API方式",
            ProcessModeDialog.MODE_TRADITIONAL: "従来方式",
            ProcessModeDialog.MODE_GMAIL_API: "Gmail API方式"
        }
        mode_text = mode_text_map.get(self.process_mode, "不明")
        self.log_panel.append_log(f"処理方式: {mode_text}")
        
        # 確認ダイアログ
        message = f"処理方式: {mode_text}\n\n以下のNコードを処理します:\n" + "\n".join(n_codes)
        reply = QMessageBox.question(
            self,
            "処理の確認",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # メールパスワードを取得（従来方式・Gmail API方式の場合のみメール監視が必要）
        email_password = None
        if self.process_mode == ProcessModeDialog.MODE_TRADITIONAL or self.process_mode == ProcessModeDialog.MODE_GMAIL_API:
            reply = QMessageBox.question(
                self,
                "メール自動取得",
                "メールを自動で取得しますか？\n（いいえを選択した場合は手動でダウンロードが必要です）",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.process_mode == ProcessModeDialog.MODE_GMAIL_API:
                    # Gmail API方式の場合
                    self.log_panel.append_log("Gmail APIを使用してメール監視を行います")
                    email_password = "GMAIL_API"  # ダミー値（WorkflowProcessorで判定）
                else:
                    # 従来方式の場合
                    # 環境変数から取得を試みる
                    import os
                    email_password = os.getenv('GMAIL_APP_PASSWORD')
                    
                    # 環境変数にない場合のみ入力を求める
                    if not email_password:
                        email_password, ok = QInputDialog.getText(
                            self,
                            "メールパスワード",
                            "メールのアプリパスワードを入力してください:",
                            QLineEdit.EchoMode.Password
                        )
                        if not ok or not email_password:
                            email_password = None
                    else:
                        self.log_panel.append_log("環境変数からメールパスワードを取得しました")
        
        # UIを無効化
        self.input_panel.set_enabled(False)
        
        # 進捗をリセット
        self.progress_panel.reset()
        self.progress_panel.set_total_items(len(n_codes))
        
        # ログに開始を記録
        mode_text_map = {
            ProcessModeDialog.MODE_API: "API方式",
            ProcessModeDialog.MODE_TRADITIONAL: "従来方式",
            ProcessModeDialog.MODE_GMAIL_API: "Gmail API方式"
        }
        mode_text = mode_text_map.get(self.process_mode, "不明")
        self.log_panel.append_log(f"処理を開始します（{mode_text}）")
        for n_code in n_codes:
            self.log_panel.append_log(f"キューに追加: {n_code}")
        
        # デバッグ：現在の処理モードを確認
        self.log_panel.append_log(f"[DEBUG] 処理開始時のprocess_mode = {repr(self.process_mode)}")
        
        # ワーカースレッドを作成して開始
        self.worker_thread = ProcessWorker(n_codes, email_password, self.process_mode)
        self.worker_thread.progress_updated.connect(self.progress_panel.update_progress)
        self.worker_thread.log_message.connect(self.log_panel.append_log)
        self.worker_thread.status_updated.connect(self.progress_panel.update_status)
        self.worker_thread.folder_selection_needed.connect(self.on_folder_selection_needed)
        self.worker_thread.file_placement_confirmation_needed.connect(self.on_file_placement_confirmation_needed)
        self.worker_thread.warning_dialog_needed.connect(self.on_warning_dialog_needed)
        self.worker_thread.finished.connect(self.on_processing_finished)
        self.worker_thread.start()
        
        self.status_bar.showMessage("処理中...")
    
    @pyqtSlot()
    def on_processing_finished(self):
        """処理が完了した時の処理"""
        self.input_panel.set_enabled(True)
        self.progress_panel.update_status("処理完了")
        self.status_bar.showMessage("準備完了")
        
        QMessageBox.information(
            self,
            "処理完了",
            "すべての処理が完了しました。"
        )
    
    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """
        確認ダイアログを表示
        
        Args:
            title: ダイアログのタイトル
            message: 確認メッセージ
        
        Returns:
            ユーザーがYesを選択した場合True
        """
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def show_about(self):
        """バージョン情報を表示"""
        QMessageBox.about(
            self,
            "バージョン情報",
            "技術の泉シリーズ制作支援ツール\n\n"
            "バージョン: 1.0.0\n"
            "開発: Technical Fountain Team\n\n"
            "このツールは技術の泉シリーズの制作プロセスを\n"
            "自動化・効率化するために開発されました。"
        )
    
    def show_comprehensive_settings(self):
        """包括的な設定ダイアログを表示"""
        from gui.config_dialog import ConfigDialog
        from src.slack_pdf_poster import ConfigManager
        
        # ConfigManagerを初期化
        config_manager = ConfigManager()
        
        # 設定ダイアログを作成
        dialog = ConfigDialog(config_manager, self)
        
        # 設定変更シグナルを接続
        dialog.config_changed.connect(self.on_config_changed)
        
        # ダイアログを表示
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            self.log_panel.append_log("✅ 設定が正常に更新されました。")
            self.status_bar.showMessage("設定更新完了", 3000)
        else:
            self.log_panel.append_log("❌ 設定の更新がキャンセルされました。")
            self.status_bar.showMessage("設定更新キャンセル", 3000)
        
    def show_repository_settings(self):
        """リポジトリ設定ダイアログを表示"""
        from gui.repository_settings_dialog import RepositorySettingsDialog
        dialog = RepositorySettingsDialog(self)
        dialog.exec()
    
    def show_hardcoding_scan_dialog(self):
        """ハードコーディングスキャンダイアログを表示"""
        try:
            from src.slack_pdf_poster import HardcodingDetector
            from pathlib import Path
            
            # プロジェクトルートのPythonファイルを取得
            project_root = Path(__file__).parent.parent
            python_files = list(project_root.rglob("*.py"))
            
            # 主要ファイルのみスキャン（高速化）
            key_files = [f for f in python_files if any(
                keyword in f.name for keyword in [
                    'main', 'config', 'api', 'slack', 'error', 'workflow', 'processor'
                ]
            )][:10]  # 最大10ファイル
            
            if not key_files:
                QMessageBox.information(self, "スキャン結果", "スキャン対象のファイルが見つかりませんでした。")
                return
            
            # スキャン実行
            detector = HardcodingDetector()
            results = detector.scan_multiple_files(key_files)
            
            # 結果を整理
            total_detections = 0
            categories = {}
            for file_path, file_results in results.items():
                for category, detections in file_results.items():
                    if detections:
                        total_detections += len(detections)
                        if category not in categories:
                            categories[category] = []
                        categories[category].extend([f"{file_path}: {d}" for d in detections])
            
            # 結果表示
            if total_detections == 0:
                QMessageBox.information(self, "スキャン結果", "✅ ハードコーディングは検出されませんでした。")
            else:
                # カテゴリ別の詳細レポート
                report_lines = [f"🔍 ハードコーディング検知結果: {total_detections}個検出\n"]
                for category, items in categories.items():
                    report_lines.append(f"【{category}】 {len(items)}個")
                    for item in items[:3]:  # 各カテゴリ最大3個表示
                        report_lines.append(f"  • {item}")
                    if len(items) > 3:
                        report_lines.append(f"  ... 他{len(items)-3}個")
                    report_lines.append("")
                
                report_lines.append("詳細なスキャンは scripts/hardcoding_scan_demo.py を実行してください。")
                
                # メッセージボックスで表示
                QMessageBox.warning(self, "ハードコーディング検知", "\n".join(report_lines))
                
                # ログにも出力
                self.log_panel.append_log(f"🔍 ハードコーディングスキャン: {total_detections}個検出")
                for category, items in categories.items():
                    self.log_panel.append_log(f"  【{category}】: {len(items)}個")
            
        except Exception as e:
            error_msg = f"ハードコーディングスキャン中にエラーが発生しました: {str(e)}"
            QMessageBox.critical(self, "エラー", error_msg)
            self.log_panel.append_log(f"❌ {error_msg}")
        
    @pyqtSlot(str, object)
    def on_config_changed(self, key_path: str, value):
        """リアルタイム設定変更時の処理"""
        self.log_panel.append_log(f"🔧 設定変更: {key_path} = {value}")
        self.status_bar.showMessage(f"設定変更: {key_path}", 2000)
    
    @pyqtSlot()
    def on_settings_updated(self):
        """設定が更新された時の処理（下位互換性維持）"""
        self.log_panel.append_log("設定が更新されました。")
    
    @pyqtSlot(object, str, object)
    def on_folder_selection_needed(self, repo_path, repo_name, default_folder):
        """フォルダ選択ダイアログを表示"""
        from pathlib import Path
        dialog = FolderSelectorDialog(
            Path(repo_path), 
            repo_name, 
            Path(default_folder) if default_folder else None, 
            self
        )
        
        # ダイアログのシグナルを接続
        def on_folder_confirmed(folder_path, save_settings):
            self.log_panel.append_log(f"作業フォルダを選択: {folder_path}")
            if save_settings:
                self.log_panel.append_log("フォルダ設定を保存しました")
            
            # ワークフロープロセッサに選択結果を設定
            if self.worker_thread and self.worker_thread.workflow_processor:
                self.worker_thread.workflow_processor.set_selected_work_folder(folder_path)
        
        dialog.folder_confirmed.connect(on_folder_confirmed)
        
        # ダイアログを表示
        result = dialog.exec()
        if result != QDialog.DialogCode.Accepted:
            # キャンセルされた場合
            self.log_panel.append_log("フォルダ選択がキャンセルされました")
            if self.worker_thread and self.worker_thread.workflow_processor:
                self.worker_thread.workflow_processor.set_selected_work_folder(None)
    
    @pyqtSlot(str, list, object)
    def on_file_placement_confirmation_needed(self, honbun_folder_path, file_list, callback):
        """ファイル配置確認ダイアログを表示"""
        try:
            # ファイル名のリストを作成
            file_names = [f.name for f in file_list[:10]]  # 最大10個まで表示
            if len(file_list) > 10:
                file_names.append(f"... 他 {len(file_list) - 10} ファイル")
            file_list_str = "\n".join([f"• {name}" for name in file_names])
            
            # 最初の確認ダイアログ
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("ファイル配置確認")
            msg_box.setText(
                f"以下のフォルダに{len(file_list)}個のWordファイル（1行目削除済み）を配置します。\n\n"
                f"配置先: {honbun_folder_path}\n\n"
                f"ファイル:\n{file_list_str}\n\n"
                f"全てのファイルを配置しますか？"
            )
            
            # カスタムボタンを追加
            place_all_btn = msg_box.addButton("配置", QMessageBox.ButtonRole.YesRole)
            select_files_btn = msg_box.addButton("一部ファイルを選択", QMessageBox.ButtonRole.NoRole)
            cancel_btn = msg_box.addButton("キャンセル", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.setDefaultButton(place_all_btn)
            msg_box.exec()
            
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == cancel_btn:
                self.log_panel.append_log("ファイル配置がキャンセルされました")
                if callback:
                    callback([])
                return
            
            if clicked_button == select_files_btn:
                # 一部ファイルのみ選択
                dialog = SimpleFileSelectorDialog(file_list, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_files = dialog.get_selected_files()
                    print(f"[DEBUG] MainWindow: ダイアログから取得したファイル数: {len(selected_files)}")
                    self.log_panel.append_log(f"ファイル選択: {len(selected_files)}個を選択")
                    if callback:
                        print(f"[DEBUG] MainWindow: callbackを呼び出します")
                        callback(selected_files)
                else:
                    self.log_panel.append_log("ファイル選択がキャンセルされました")
                    if callback:
                        callback([])
            else:
                # 全ファイルを配置
                self.log_panel.append_log(f"ファイル配置確認: 全{len(file_list)}個のファイルを配置")
                if callback:
                    callback(file_list)
                
        except Exception as e:
            self.log_panel.append_log(f"確認ダイアログエラー: {e}")
            if callback:
                callback([])
    
    def closeEvent(self, event):
        """ウィンドウを閉じる時の処理"""
        # 実行中のワーカースレッドをチェック
        running_workers = []
        
        if self.worker_thread and self.worker_thread.isRunning():
            running_workers.append("処理")
            
        if hasattr(self, 'error_detector_worker') and self.error_detector_worker and self.error_detector_worker.isRunning():
            running_workers.append("エラー検知")
        
        if running_workers:
            reply = QMessageBox.question(
                self,
                "終了の確認",
                f"{', '.join(running_workers)}が実行中です。終了しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            # スレッドを停止
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.terminate()
                self.worker_thread.wait()
                
            if hasattr(self, 'error_detector_worker') and self.error_detector_worker and self.error_detector_worker.isRunning():
                self.error_detector_worker.terminate()
                self.error_detector_worker.wait()
        
        event.accept()
    
    @pyqtSlot()
    def show_process_mode_dialog(self):
        """処理方式選択ダイアログを表示"""
        dialog = ProcessModeDialog(self)
        # 現在の処理方式を反映
        if self.process_mode == ProcessModeDialog.MODE_TRADITIONAL:
            dialog.traditional_radio.setChecked(True)
        elif self.process_mode == ProcessModeDialog.MODE_API:
            dialog.api_radio.setChecked(True)
        elif self.process_mode == ProcessModeDialog.MODE_GMAIL_API:
            dialog.gmail_api_radio.setChecked(True)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.process_mode = dialog.get_selected_mode()
            
            # モードテキストマッピング
            mode_text_map = {
                ProcessModeDialog.MODE_API: "API方式",
                ProcessModeDialog.MODE_TRADITIONAL: "従来方式",
                ProcessModeDialog.MODE_GMAIL_API: "Gmail API方式"
            }
            mode_text = mode_text_map.get(self.process_mode, "不明")
            
            self.log_panel.append_log(f"処理方式を変更: {mode_text}")
            self.status_bar.showMessage(f"処理方式: {mode_text}")
    
    # Pre-flight Check関数を削除
        
    @pyqtSlot(list, str)
    def on_warning_dialog_needed(self, messages, result_type):
        """API処理の警告ダイアログを表示"""
        self.log_panel.append_log(f"警告ダイアログ表示要求: {len(messages)}件のメッセージ ({result_type})")
        
        # シンプルなQMessageBoxアプローチを使用（一時的な回避策）
        USE_SIMPLE_DIALOG = True
        
        if USE_SIMPLE_DIALOG:
            # QMessageBoxベースのシンプルなダイアログ
            from gui.dialogs.simple_warning_dialog import show_warning_dialog
            show_warning_dialog(self, messages, result_type)
            self.log_panel.append_log("警告ダイアログを閉じました")
        else:
            # カスタムダイアログ（元の実装）
            # イベントを処理させる
            QCoreApplication.processEvents()
            
            # ダイアログを作成して表示
            dialog = WarningDialog(messages, result_type, self)
            
            # モーダルダイアログとして実行
            result = dialog.exec()
            
            self.log_panel.append_log(f"警告ダイアログを閉じました (結果: {result})")
    
    @pyqtSlot(list)
    def start_error_detection(self, n_codes):
        """エラーファイル検知を開始"""
        # 確認ダイアログ
        message = (
            f"組版エラー後の原因ファイル検出を開始します。\n\n"
            f"対象Nコード:\n" + "\n".join(n_codes) + "\n\n"
            f"この処理には20-40分程度かかる場合があります。\n"
            f"続行しますか？"
        )
        reply = QMessageBox.question(
            self,
            "エラーファイル検知",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # メールパスワードを取得（オプション）
        email_password = None
        reply = QMessageBox.question(
            self,
            "メール監視設定",
            "変換完了メールを自動で監視しますか？\n"
            "（いいえを選択した場合は手動確認が必要です）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            import os
            email_password = os.getenv('GMAIL_APP_PASSWORD')
            
            if not email_password:
                email_password, ok = QInputDialog.getText(
                    self,
                    "メールパスワード",
                    "メールのアプリパスワードを入力してください:",
                    QLineEdit.EchoMode.Password
                )
                if not ok or not email_password:
                    email_password = None
        
        # UIを無効化
        self.input_panel.set_enabled(False)
        
        # エラー検知用の拡張WorkflowProcessorを作成
        from core.workflow_processor_with_error_detection import WorkflowProcessorWithErrorDetection
        
        email_address = os.getenv('GMAIL_ADDRESS', 'yamashiro.takashi@gmail.com')
        # エラー検知フローは常にAPI方式を使用
        self.error_detection_processor = WorkflowProcessorWithErrorDetection(
            email_address=email_address,
            email_password=email_password,
            process_mode='api'  # エラー検知は常にAPI方式
        )
        
        # シグナルを接続
        self.error_detection_processor.log_message.connect(self.log_panel.append_log)
        self.error_detection_processor.progress_updated.connect(self.progress_panel.update_progress)
        self.error_detection_processor.status_updated.connect(self.progress_panel.update_status)
        self.error_detection_processor.confirmation_needed.connect(self.show_confirmation_dialog)
        self.error_detection_processor.folder_selection_needed.connect(self.on_folder_selection_needed)
        self.error_detection_processor.file_placement_confirmation_needed.connect(self.on_file_placement_confirmation_needed)
        self.error_detection_processor.warning_dialog_needed.connect(self.on_warning_dialog_needed)
        self.error_detection_processor.error_files_detected.connect(self.on_error_detection_completed)
        self.error_detection_processor.error_file_selection_needed.connect(self.on_error_file_selection_needed)
        
        # 進捗をリセット
        self.progress_panel.reset()
        self.progress_panel.update_status("エラーファイル検知フロー実行中...")
        
        # ログに開始を記録
        self.log_panel.append_log("エラーファイル検知フローを開始します")
        self.log_panel.append_log(f"対象Nコード: {', '.join(n_codes)}")
        
        # 処理を別スレッドで実行（QThreadを使用）
        class ErrorDetectionWorker(QThread):
            def __init__(self, processor, n_codes):
                super().__init__()
                self.processor = processor
                self.n_codes = n_codes
                
            def run(self):
                self.processor.process_n_codes_with_error_detection(self.n_codes)
        
        self.error_detection_thread = ErrorDetectionWorker(self.error_detection_processor, n_codes)
        self.error_detection_thread.finished.connect(self.on_error_detection_finished)
        self.error_detection_thread.start()
        
        self.status_bar.showMessage("エラーファイル検知中...")
    
    @pyqtSlot()
    def on_error_detection_finished(self):
        """エラー検知処理完了時の処理"""
        self.log_panel.append_log("エラー検知処理が完了しました")
        
        # 画面を初期状態に戻す
        self.input_panel.set_enabled(True)
        self.progress_panel.reset()
        self.status_bar.showMessage("準備完了")
        
        # ログに区切り線を追加
        self.log_panel.append_log("=" * 50)
        
        # スレッドのクリーンアップ
        if self.error_detection_thread:
            self.error_detection_thread = None
    
    @pyqtSlot(str, bool, str)
    def on_file_processed(self, filename, success, message):
        """ファイル処理完了時の処理"""
        if success:
            self.log_panel.append_log(f"✓ {filename}: {message}")
        else:
            self.log_panel.append_log(f"✗ {filename}: {message}")
    
    @pyqtSlot(list, object)
    def on_error_file_selection_needed(self, file_list, callback):
        """エラー検知用ファイル選択ダイアログを表示"""
        try:
            # ファイル名のリストを作成
            file_names = [f.name for f in file_list[:10]]  # 最大10個まで表示
            if len(file_list) > 10:
                file_names.append(f"... 他 {len(file_list) - 10} ファイル")
            file_list_str = "\n".join([f"• {name}" for name in file_names])
            
            # 確認ダイアログ
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("エラー検知ファイル選択")
            msg_box.setText(
                f"Word2XHTML5でエラー検知を行うファイルを選択してください。\n\n"
                f"対象ファイル: {len(file_list)}個\n\n"
                f"ファイル:\n{file_list_str}\n\n"
                f"どのファイルを検査しますか？"
            )
            
            # カスタムボタンを追加
            check_all_btn = msg_box.addButton("全てのファイルを検査", QMessageBox.ButtonRole.YesRole)
            select_files_btn = msg_box.addButton("一部ファイルを選択", QMessageBox.ButtonRole.NoRole)
            cancel_btn = msg_box.addButton("キャンセル", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.setDefaultButton(check_all_btn)
            msg_box.exec()
            
            clicked_button = msg_box.clickedButton()
            
            if clicked_button == cancel_btn:
                self.log_panel.append_log("エラー検知がキャンセルされました")
                if callback:
                    callback([])
                return
            
            if clicked_button == select_files_btn:
                # 一部ファイルのみ選択
                dialog = SimpleFileSelectorDialog(file_list, self)
                dialog.setWindowTitle("エラー検知ファイル選択")
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_files = dialog.get_selected_files()
                    self.log_panel.append_log(f"エラー検知ファイル選択: {len(selected_files)}個を選択")
                    if callback:
                        callback(selected_files)
                else:
                    self.log_panel.append_log("ファイル選択がキャンセルされました")
                    if callback:
                        callback([])
            else:
                # 全てのファイルを検査
                self.log_panel.append_log(f"全ファイル（{len(file_list)}個）を検査します")
                if callback:
                    callback(file_list)
                    
        except Exception as e:
            self.log_panel.append_log(f"ファイル選択エラー: {e}")
            if callback:
                callback([])
    
    @pyqtSlot(list)
    def on_error_detection_completed(self, error_files):
        """エラー検知完了時の処理"""
        if error_files:
            # エラーファイルリストを表示
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("エラーファイル検出結果")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # 結果表示
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(
                f"エラーファイルが {len(error_files)} 個検出されました:\n\n" +
                "\n".join([f"- {f.name}" for f in error_files]) +
                "\n\nこれらのファイルは組版でPDF生成エラーが発生します。\n"
                "修正が必要です。"
            )
            layout.addWidget(text_edit)
            
            # ボタン
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(dialog.accept)
            layout.addWidget(buttons)
            
            dialog.exec()
        else:
            QMessageBox.information(
                self,
                "検出結果",
                "エラーファイルは検出されませんでした。\n"
                "すべてのファイルが正常に処理可能です。"
            )
    
    @pyqtSlot()
    def on_error_detection_finished(self):
        """エラー検知処理終了時の処理"""
        self.input_panel.set_enabled(True)
        self.progress_panel.update_status("エラー検知完了")
        self.status_bar.showMessage("準備完了")
        
        if hasattr(self, 'error_detection_processor'):
            delattr(self, 'error_detection_processor')
        if hasattr(self, 'error_detection_thread'):
            delattr(self, 'error_detection_thread')
    
    @pyqtSlot(str)
    def start_pdf_post(self, n_code):
        """
        PDF投稿を開始
        
        Args:
            n_code: 投稿するN番号
        """
        try:
            # SlackPDFPosterとPDFPostDialogをインポート
            from src.slack_pdf_poster import SlackPDFPoster
            from gui.pdf_post_dialog import PDFPostDialog
            
            # PDF投稿インスタンスを作成
            poster = SlackPDFPoster()
            
            # 入力検証
            is_valid, error_msg = poster.validate_inputs(n_code)
            if not is_valid:
                QMessageBox.warning(self, "入力エラー", error_msg)
                return
            
            # チャネル番号を抽出
            try:
                channel_number = poster.extract_channel_number(n_code)
            except ValueError as e:
                QMessageBox.warning(self, "入力エラー", str(e))
                return
            
            # Slackチャネルを検索
            channel_name = poster.find_slack_channel(channel_number)
            if not channel_name:
                QMessageBox.warning(
                    self, 
                    "チャネルが見つかりません",
                    f"N番号 {n_code} に対応するSlackチャネルが見つかりませんでした。\n\n"
                    f"検索パターン: n{channel_number}-*\n\n"
                    f"以下を確認してください:\n"
                    f"・チャネルが存在するか\n"
                    f"・Botがチャネルに招待されているか"
                )
                return
            
            # PDFファイルを検索（仮のパス - 実際の設定から取得する必要がある）
            import os
            from pathlib import Path
            
            # NコードからPDFファイルを検索（NP-IRD配下）
            pdf_path = poster.find_pdf_file(n_code)
            if not pdf_path:
                QMessageBox.warning(
                    self, 
                    "PDFファイルが見つかりません",
                    f"N番号 {n_code} のPDFファイルが見つかりませんでした。\n\n"
                    f"検索場所: G:\\.shortcut-targets-by-id\\...\\NP-IRD\\{n_code}\\out\\\n\n"
                    f"以下を確認してください:\n"
                    f"・Nフォルダが存在するか\n"
                    f"・outフォルダが存在するか\n"
                    f"・PDFファイルが生成されているか"
                )
                return
            
            # GoogleシートからNコード情報を取得（著者SlackID含む）
            author_slack_id = None
            try:
                from core.google_sheet import GoogleSheetClient
                sheet_client = GoogleSheetClient()
                sheet_data = sheet_client.search_n_code(n_code)
                if sheet_data and 'author_slack_id' in sheet_data:
                    author_slack_id = sheet_data['author_slack_id']
                    self.log_panel.append_log(f"著者SlackID: {author_slack_id or '未設定'}")
            except Exception as e:
                self.log_panel.append_log(f"著者SlackID取得エラー: {str(e)}")
            
            # 確認ダイアログを表示
            default_message = poster.get_default_message()
            dialog = PDFPostDialog(pdf_path, channel_name, default_message, author_slack_id, self)
            
            approved, message = dialog.get_confirmation()
            if not approved:
                self.log_panel.append_log("PDF投稿がキャンセルされました")
                return
            
            # Slack投稿を実行
            self.log_panel.append_log(f"PDF投稿を開始: {n_code} -> #{channel_name}")
            success, result = poster.post_to_slack(pdf_path, channel_name, message)
            
            if success:
                QMessageBox.information(
                    self,
                    "投稿完了", 
                    f"#{channel_name} への投稿が完了しました。\n\n"
                    f"ファイル: {Path(pdf_path).name}"
                )
                self.log_panel.append_log(f"PDF投稿成功: {result}")
            else:
                QMessageBox.critical(
                    self,
                    "投稿エラー",
                    f"PDF投稿に失敗しました:\n\n{result}"
                )
                self.log_panel.append_log(f"PDF投稿失敗: {result}")
                
        except Exception as e:
            error_msg = f"PDF投稿処理中にエラーが発生しました: {str(e)}"
            QMessageBox.critical(self, "エラー", error_msg)
            self.log_panel.append_log(error_msg)