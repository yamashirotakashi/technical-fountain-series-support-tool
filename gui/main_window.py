"""メインウィンドウモジュール"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QStatusBar, QMessageBox,
                             QInputDialog, QLineEdit, QDialog)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QIcon, QAction

from gui.components.input_panel_qt6 import InputPanel
from gui.components.log_panel_qt6 import LogPanel
from gui.components.progress_bar_qt6 import ProgressPanel
from gui.dialogs import FolderSelectorDialog
from gui.dialogs.simple_file_selector_dialog import SimpleFileSelectorDialog
from gui.dialogs.process_mode_dialog import ProcessModeDialog
from gui.dialogs.warning_dialog import WarningDialog
from core.workflow_processor import WorkflowProcessor
from core.api_processor import ApiProcessor
from utils.logger import get_logger
from pathlib import Path


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
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.connect_signals()
    
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
        
        # リポジトリ設定アクション
        repo_settings_action = QAction("リポジトリ設定(&R)", self)
        repo_settings_action.triggered.connect(self.show_repository_settings)
        tools_menu.addAction(repo_settings_action)
        
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
        self.input_panel.processing_requested.connect(self.start_processing)
        self.input_panel.settings_requested.connect(self.show_process_mode_dialog)
        # self.input_panel.preflight_requested.connect(self.show_preflight_check)  # 削除
        self.input_panel.error_check_requested.connect(self.start_error_detection)
    
    @pyqtSlot(list)
    def start_processing(self, n_codes):
        """
        処理を開始
        
        Args:
            n_codes: 処理するNコードのリスト
        """
        # 確認ダイアログ
        message = f"以下のNコードを処理します:\n" + "\n".join(n_codes)
        reply = QMessageBox.question(
            self,
            "処理の確認",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # メールパスワードを取得（従来方式の場合のみ）
        email_password = None
        if self.process_mode == ProcessModeDialog.MODE_TRADITIONAL:
            reply = QMessageBox.question(
                self,
                "メール自動取得",
                "メールを自動で取得しますか？\n（いいえを選択した場合は手動でダウンロードが必要です）",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
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
                    self.log_panel.append_log("環境変数からメールパスワードを取得しました", "INFO")
        
        # UIを無効化
        self.input_panel.set_enabled(False)
        
        # 進捗をリセット
        self.progress_panel.reset()
        self.progress_panel.set_total_items(len(n_codes))
        
        # ログに開始を記録
        mode_text = "API方式" if self.process_mode == ProcessModeDialog.MODE_API else "従来方式"
        self.log_panel.append_log(f"処理を開始します（{mode_text}）", "INFO")
        for n_code in n_codes:
            self.log_panel.append_log(f"キューに追加: {n_code}", "INFO")
        
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
    
    def show_repository_settings(self):
        """リポジトリ設定ダイアログを表示"""
        from gui.repository_settings_dialog import RepositorySettingsDialog
        dialog = RepositorySettingsDialog(self)
        dialog.exec()
    
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
            self.log_panel.append_log(f"作業フォルダを選択: {folder_path}", "INFO")
            if save_settings:
                self.log_panel.append_log("フォルダ設定を保存しました", "INFO")
            
            # ワークフロープロセッサに選択結果を設定
            if self.worker_thread and self.worker_thread.workflow_processor:
                self.worker_thread.workflow_processor.set_selected_work_folder(folder_path)
        
        dialog.folder_confirmed.connect(on_folder_confirmed)
        
        # ダイアログを表示
        result = dialog.exec()
        if result != QDialog.DialogCode.Accepted:
            # キャンセルされた場合
            self.log_panel.append_log("フォルダ選択がキャンセルされました", "WARNING")
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
                self.log_panel.append_log("ファイル配置がキャンセルされました", "INFO")
                if callback:
                    callback([])
                return
            
            if clicked_button == select_files_btn:
                # 一部ファイルのみ選択
                dialog = SimpleFileSelectorDialog(file_list, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_files = dialog.get_selected_files()
                    print(f"[DEBUG] MainWindow: ダイアログから取得したファイル数: {len(selected_files)}")
                    self.log_panel.append_log(f"ファイル選択: {len(selected_files)}個を選択", "INFO")
                    if callback:
                        print(f"[DEBUG] MainWindow: callbackを呼び出します")
                        callback(selected_files)
                else:
                    self.log_panel.append_log("ファイル選択がキャンセルされました", "INFO")
                    if callback:
                        callback([])
            else:
                # 全ファイルを配置
                self.log_panel.append_log(f"ファイル配置確認: 全{len(file_list)}個のファイルを配置", "INFO")
                if callback:
                    callback(file_list)
                
        except Exception as e:
            self.log_panel.append_log(f"確認ダイアログエラー: {e}", "ERROR")
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
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.process_mode = dialog.get_selected_mode()
            mode_text = "API方式" if self.process_mode == ProcessModeDialog.MODE_API else "従来方式"
            self.log_panel.append_log(f"処理方式を変更: {mode_text}", "INFO")
            self.status_bar.showMessage(f"処理方式: {mode_text}")
    
    # Pre-flight Check関数を削除
        
    @pyqtSlot(list, str)
    def on_warning_dialog_needed(self, messages, result_type):
        """API処理の警告ダイアログを表示"""
        self.log_panel.append_log(f"警告ダイアログ表示要求: {len(messages)}件のメッセージ ({result_type})", "INFO")
        
        # シンプルなQMessageBoxアプローチを使用（一時的な回避策）
        USE_SIMPLE_DIALOG = True
        
        if USE_SIMPLE_DIALOG:
            # QMessageBoxベースのシンプルなダイアログ
            from gui.dialogs.simple_warning_dialog import show_warning_dialog
            show_warning_dialog(self, messages, result_type)
            self.log_panel.append_log("警告ダイアログを閉じました", "INFO")
        else:
            # カスタムダイアログ（元の実装）
            # イベントを処理させる
            QCoreApplication.processEvents()
            
            # ダイアログを作成して表示
            dialog = WarningDialog(messages, result_type, self)
            
            # モーダルダイアログとして実行
            result = dialog.exec()
            
            self.log_panel.append_log(f"警告ダイアログを閉じました (結果: {result})", "INFO")
    
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
        self.error_detection_processor = WorkflowProcessorWithErrorDetection(
            email_address=email_address,
            email_password=email_password,
            process_mode=self.process_mode
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
        self.log_panel.append_log("エラーファイル検知フローを開始します", "INFO")
        self.log_panel.append_log(f"対象Nコード: {', '.join(n_codes)}", "INFO")
        
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
        self.log_panel.append_log("エラー検知処理が完了しました", "INFO")
        
        # 画面を初期状態に戻す
        self.input_panel.set_enabled(True)
        self.progress_panel.reset()
        self.status_bar.showMessage("準備完了")
        
        # ログに区切り線を追加
        self.log_panel.append_log("=" * 50, "INFO")
        
        # スレッドのクリーンアップ
        if self.error_detection_thread:
            self.error_detection_thread = None
    
    @pyqtSlot(str, bool, str)
    def on_file_processed(self, filename, success, message):
        """ファイル処理完了時の処理"""
        if success:
            self.log_panel.append_log(f"✓ {filename}: {message}", "INFO")
        else:
            self.log_panel.append_log(f"✗ {filename}: {message}", "ERROR")
    
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
                self.log_panel.append_log("エラー検知がキャンセルされました", "INFO")
                if callback:
                    callback([])
                return
            
            if clicked_button == select_files_btn:
                # 一部ファイルのみ選択
                dialog = SimpleFileSelectorDialog(file_list, self)
                dialog.setWindowTitle("エラー検知ファイル選択")
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_files = dialog.get_selected_files()
                    self.log_panel.append_log(f"エラー検知ファイル選択: {len(selected_files)}個を選択", "INFO")
                    if callback:
                        callback(selected_files)
                else:
                    self.log_panel.append_log("ファイル選択がキャンセルされました", "INFO")
                    if callback:
                        callback([])
            else:
                # 全てのファイルを検査
                self.log_panel.append_log(f"全ファイル（{len(file_list)}個）を検査します", "INFO")
                if callback:
                    callback(file_list)
                    
        except Exception as e:
            self.log_panel.append_log(f"ファイル選択エラー: {e}", "ERROR")
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