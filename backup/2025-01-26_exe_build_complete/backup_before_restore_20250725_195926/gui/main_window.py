"""繝｡繧､繝ｳ繧ｦ繧｣繝ｳ繝峨え繝｢繧ｸ繝･繝ｼ繝ｫ"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QMenuBar, QStatusBar, QMessageBox,
                             QInputDialog, QLineEdit)
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


class ProcessWorker(QThread):
    """繝舌ャ繧ｯ繧ｰ繝ｩ繧ｦ繝ｳ繝会ｿｽE逅・・ｽ・ｽ縺ｮ繝ｯ繝ｼ繧ｫ繝ｼ繧ｹ繝ｬ繝・・ｽ・ｽ"""
    
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
        """蜃ｦ逅・・ｽ・ｽ螳溯｡・""
        try:
            # WorkflowProcessor繧剃ｽ懶ｿｽE・ｽE・ｽ・ｽE逅・・ｽ・ｽ蠑上ｒ貂｡縺呻ｼ・            self.workflow_processor = WorkflowProcessor(
                email_password=self.email_password,
                process_mode=self.process_mode
            )
            
            # 繧ｷ繧ｰ繝翫Ν繧呈磁邯・            self.workflow_processor.log_message.connect(self.log_message.emit)
            self.workflow_processor.progress_updated.connect(self.progress_updated.emit)
            self.workflow_processor.status_updated.connect(self.status_updated.emit)
            self.workflow_processor.folder_selection_needed.connect(self.folder_selection_needed.emit)
            self.workflow_processor.file_placement_confirmation_needed.connect(self.file_placement_confirmation_needed.emit)
            self.workflow_processor.warning_dialog_needed.connect(self.warning_dialog_needed.emit)
            
            # 蜃ｦ逅・・ｽ・ｽ螳溯｡・            self.workflow_processor.process_n_codes(self.n_codes)
            
        except Exception as e:
            self.logger.error(f"蜃ｦ逅・・ｽ・ｽ繝ｩ繝ｼ: {e}", exc_info=True)
            self.log_message.emit(f"繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}", "ERROR")
        finally:
            if self.workflow_processor:
                self.workflow_processor.cleanup()
            self.finished.emit()


class MainWindow(QMainWindow):
    """繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ繝｡繧､繝ｳ繧ｦ繧｣繝ｳ繝峨え"""
    
    def __init__(self):
        """MainWindow繧抵ｿｽE譛溷喧"""
        super().__init__()
        self.worker_thread = None
        self.process_mode = ProcessModeDialog.MODE_TRADITIONAL  # 繝・・ｽ・ｽ繧ｩ繝ｫ繝茨ｿｽE蠕捺擂譁ｹ蠑・        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.connect_signals()
    
    def setup_ui(self):
        """UI繧呈ｧ狗ｯ・""
        self.setWindowTitle("謚陦難ｿｽE豕峨す繝ｪ繝ｼ繧ｺ蛻ｶ菴懈髪謠ｴ繝・・ｽE繝ｫ")
        self.setGeometry(100, 100, 1200, 800)
        
        # 荳ｭ螟ｮ繧ｦ繧｣繧ｸ繧ｧ繝・・ｽ・ｽ
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 繝｡繧､繝ｳ繝ｬ繧､繧｢繧ｦ繝・        main_layout = QVBoxLayout(central_widget)
        
        # 荳企Κ・ｽE・ｽ・ｽE蜉帙ヱ繝阪Ν
        self.input_panel = InputPanel()
        
        # 荳ｭ螟ｮ・ｽE・ｽ繧ｹ繝励Μ繝・・ｽ・ｽ繝ｼ・ｽE・ｽ繝ｭ繧ｰ繝代ロ繝ｫ・ｽE・ｽE        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 繝ｭ繧ｰ繝代ロ繝ｫ
        self.log_panel = LogPanel()
        
        # 騾ｲ謐励ヱ繝阪Ν
        self.progress_panel = ProgressPanel()
        
        # 繧ｹ繝励Μ繝・・ｽ・ｽ繝ｼ縺ｫ霑ｽ蜉
        splitter.addWidget(self.log_panel)
        splitter.setStretchFactor(0, 1)
        
        # 繝ｬ繧､繧｢繧ｦ繝医↓霑ｽ蜉
        main_layout.addWidget(self.input_panel)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.progress_panel)
        
        # 繧ｹ繧ｿ繧､繝ｫ險ｭ螳・        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def setup_menu(self):
        """繝｡繝九Η繝ｼ繝撰ｿｽE繧定ｨｭ螳・""
        menubar = self.menuBar()
        
        # 繝輔ぃ繧､繝ｫ繝｡繝九Η繝ｼ
        file_menu = menubar.addMenu("繝輔ぃ繧､繝ｫ(&F)")
        
        # 邨ゆｺ・・ｽ・ｽ繧ｯ繧ｷ繝ｧ繝ｳ
        exit_action = QAction("邨ゆｺ・&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 繝・・ｽE繝ｫ繝｡繝九Η繝ｼ
        tools_menu = menubar.addMenu("繝・・ｽE繝ｫ(&T)")
        
        # 繝ｭ繧ｰ繧ｯ繝ｪ繧｢繧｢繧ｯ繧ｷ繝ｧ繝ｳ
        clear_log_action = QAction("繝ｭ繧ｰ繧ｯ繝ｪ繧｢(&C)", self)
        clear_log_action.triggered.connect(self.log_panel.clear_logs)
        tools_menu.addAction(clear_log_action)
        
        # 繧ｻ繝代Ξ繝ｼ繧ｿ
        tools_menu.addSeparator()
        
        # 繝ｪ繝昴ず繝医Μ險ｭ螳壹い繧ｯ繧ｷ繝ｧ繝ｳ
        repo_settings_action = QAction("繝ｪ繝昴ず繝医Μ險ｭ螳・&R)", self)
        repo_settings_action.triggered.connect(self.show_repository_settings)
        tools_menu.addAction(repo_settings_action)
        
        # 繝倥Ν繝励Γ繝九Η繝ｼ
        help_menu = menubar.addMenu("繝倥Ν繝・&H)")
        
        # 繝撰ｿｽE繧ｸ繝ｧ繝ｳ諠・・ｽ・ｽ繧｢繧ｯ繧ｷ繝ｧ繝ｳ
        about_action = QAction("繝撰ｿｽE繧ｸ繝ｧ繝ｳ諠・・ｽ・ｽ(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_statusbar(self):
        """繧ｹ繝・・ｽE繧ｿ繧ｹ繝撰ｿｽE繧定ｨｭ螳・""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("貅門ｙ螳御ｺ・)
    
    def connect_signals(self):
        """繧ｷ繧ｰ繝翫Ν繧呈磁邯・""
        # 蜈･蜉帙ヱ繝阪Ν縺九ｉ縺ｮ繧ｷ繧ｰ繝翫Ν
        self.input_panel.process_requested.connect(self.start_processing)
        self.input_panel.settings_requested.connect(self.show_process_mode_dialog)
    
    @pyqtSlot(list)
    def start_processing(self, n_codes):
        """
        蜃ｦ逅・・ｽ・ｽ髢句ｧ・        
        Args:
            n_codes: 蜃ｦ逅・・ｽ・ｽ繧起繧ｳ繝ｼ繝会ｿｽE繝ｪ繧ｹ繝・        """
        # 遒ｺ隱阪ム繧､繧｢繝ｭ繧ｰ
        message = f"莉･荳具ｿｽEN繧ｳ繝ｼ繝峨ｒ蜃ｦ逅・・ｽ・ｽ縺ｾ縺・\n" + "\n".join(n_codes)
        reply = QMessageBox.question(
            self,
            "蜃ｦ逅・・ｽE遒ｺ隱・,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        # 繝｡繝ｼ繝ｫ繝代せ繝ｯ繝ｼ繝峨ｒ蜿門ｾ暦ｼ亥ｾ捺擂譁ｹ蠑擾ｿｽE蝣ｴ蜷茨ｿｽE縺ｿ・ｽE・ｽE        email_password = None
        if self.process_mode == ProcessModeDialog.MODE_TRADITIONAL:
            reply = QMessageBox.question(
                self,
                "繝｡繝ｼ繝ｫ閾ｪ蜍募叙蠕・,
                "繝｡繝ｼ繝ｫ繧抵ｿｽE蜍輔〒蜿門ｾ励＠縺ｾ縺吶°・ｽE・ｽ\n・ｽE・ｽ縺・＝E・ｽ・ｽ繧帝∈謚槭＠縺溷ｴ蜷茨ｿｽE謇句虚縺ｧ繝繧ｦ繝ｳ繝ｭ繝ｼ繝峨′蠢・・ｽ・ｽ縺ｧ縺呻ｼ・,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 迺ｰ蠅・・ｽ・ｽ謨ｰ縺九ｉ蜿門ｾ励ｒ隧ｦ縺ｿ繧・                import os
                email_password = os.getenv('GMAIL_APP_PASSWORD')
                
                # 迺ｰ蠅・・ｽ・ｽ謨ｰ縺ｫ縺ｪ縺・・ｽ・ｽ蜷茨ｿｽE縺ｿ蜈･蜉帙ｒ豎ゅａ繧・                if not email_password:
                    email_password, ok = QInputDialog.getText(
                        self,
                        "繝｡繝ｼ繝ｫ繝代せ繝ｯ繝ｼ繝・,
                        "繝｡繝ｼ繝ｫ縺ｮ繧｢繝励Μ繝代せ繝ｯ繝ｼ繝峨ｒ蜈･蜉帙＠縺ｦ縺上□縺輔＞:",
                        QLineEdit.EchoMode.Password
                    )
                    if not ok or not email_password:
                        email_password = None
                else:
                    self.log_panel.append_log("迺ｰ蠅・・ｽ・ｽ謨ｰ縺九ｉ繝｡繝ｼ繝ｫ繝代せ繝ｯ繝ｼ繝峨ｒ蜿門ｾ励＠縺ｾ縺励◆", "INFO")
        
        # UI繧堤┌蜉ｹ蛹・        self.input_panel.set_enabled(False)
        
        # 騾ｲ謐励ｒ繝ｪ繧ｻ繝・・ｽ・ｽ
        self.progress_panel.reset()
        self.progress_panel.set_total_items(len(n_codes))
        
        # 繝ｭ繧ｰ縺ｫ髢句ｧ九ｒ險倬鹸
        mode_text = "API譁ｹ蠑・ if self.process_mode == ProcessModeDialog.MODE_API else "蠕捺擂譁ｹ蠑・
        self.log_panel.append_log(f"蜃ｦ逅・・ｽ・ｽ髢句ｧ九＠縺ｾ縺呻ｼ・mode_text}・ｽE・ｽE, "INFO")
        for n_code in n_codes:
            self.log_panel.append_log(f"繧ｭ繝･繝ｼ縺ｫ霑ｽ蜉: {n_code}", "INFO")
        
        # 繝ｯ繝ｼ繧ｫ繝ｼ繧ｹ繝ｬ繝・・ｽ・ｽ繧剃ｽ懶ｿｽE縺励※髢句ｧ・        self.worker_thread = ProcessWorker(n_codes, email_password, self.process_mode)
        self.worker_thread.progress_updated.connect(self.progress_panel.update_progress)
        self.worker_thread.log_message.connect(self.log_panel.append_log)
        self.worker_thread.status_updated.connect(self.progress_panel.update_status)
        self.worker_thread.folder_selection_needed.connect(self.on_folder_selection_needed)
        self.worker_thread.file_placement_confirmation_needed.connect(self.on_file_placement_confirmation_needed)
        self.worker_thread.warning_dialog_needed.connect(self.on_warning_dialog_needed)
        self.worker_thread.finished.connect(self.on_processing_finished)
        self.worker_thread.start()
        
        self.status_bar.showMessage("蜃ｦ逅・・ｽ・ｽ...")
    
    @pyqtSlot()
    def on_processing_finished(self):
        """蜃ｦ逅・・ｽ・ｽ螳御ｺ・・ｽ・ｽ縺滓凾縺ｮ蜃ｦ逅・""
        self.input_panel.set_enabled(True)
        self.progress_panel.update_status("蜃ｦ逅・・ｽ・ｽ莠・)
        self.status_bar.showMessage("貅門ｙ螳御ｺ・)
        
        QMessageBox.information(
            self,
            "蜃ｦ逅・・ｽ・ｽ莠・,
            "縺吶∋縺ｦ縺ｮ蜃ｦ逅・・ｽ・ｽ螳御ｺ・・ｽ・ｽ縺ｾ縺励◆縲・
        )
    
    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """
        遒ｺ隱阪ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ
        
        Args:
            title: 繝繧､繧｢繝ｭ繧ｰ縺ｮ繧ｿ繧､繝医Ν
            message: 遒ｺ隱阪Γ繝・・ｽ・ｽ繝ｼ繧ｸ
        
        Returns:
            繝ｦ繝ｼ繧ｶ繝ｼ縺刑es繧帝∈謚槭＠縺溷ｴ蜷・rue
        """
        reply = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def show_about(self):
        """繝撰ｿｽE繧ｸ繝ｧ繝ｳ諠・・ｽ・ｽ繧定｡ｨ遉ｺ"""
        QMessageBox.about(
            self,
            "繝撰ｿｽE繧ｸ繝ｧ繝ｳ諠・・ｽ・ｽ",
            "謚陦難ｿｽE豕峨す繝ｪ繝ｼ繧ｺ蛻ｶ菴懈髪謠ｴ繝・・ｽE繝ｫ\n\n"
            "繝撰ｿｽE繧ｸ繝ｧ繝ｳ: 1.0.0\n"
            "髢狗匱: Technical Fountain Team\n\n"
            "縺難ｿｽE繝・・ｽE繝ｫ縺ｯ謚陦難ｿｽE豕峨す繝ｪ繝ｼ繧ｺ縺ｮ蛻ｶ菴懶ｿｽE繝ｭ繧ｻ繧ｹ繧箪n"
            "閾ｪ蜍募喧繝ｻ蜉ｹ邇・・ｽ・ｽ縺吶ｋ縺溘ａ縺ｫ髢狗匱縺輔ｌ縺ｾ縺励◆縲・
        )
    
    def show_repository_settings(self):
        """繝ｪ繝昴ず繝医Μ險ｭ螳壹ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ"""
        from gui.repository_settings_dialog import RepositorySettingsDialog
        dialog = RepositorySettingsDialog(self)
        dialog.exec()
    
    @pyqtSlot(object, str, object)
    def on_folder_selection_needed(self, repo_path, repo_name, default_folder):
        """繝輔か繝ｫ繝驕ｸ謚槭ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ"""
        from pathlib import Path
        dialog = FolderSelectorDialog(
            Path(repo_path), 
            repo_name, 
            Path(default_folder) if default_folder else None, 
            self
        )
        
        # 繝繧､繧｢繝ｭ繧ｰ縺ｮ繧ｷ繧ｰ繝翫Ν繧呈磁邯・        def on_folder_confirmed(folder_path, save_settings):
            self.log_panel.append_log(f"菴懈･ｭ繝輔か繝ｫ繝繧帝∈謚・ {folder_path}", "INFO")
            if save_settings:
                self.log_panel.append_log("繝輔か繝ｫ繝險ｭ螳壹ｒ菫晏ｭ倥＠縺ｾ縺励◆", "INFO")
            
            # 繝ｯ繝ｼ繧ｯ繝輔Ο繝ｼ繝励Ο繧ｻ繝・・ｽ・ｽ縺ｫ驕ｸ謚樒ｵ先棡繧定ｨｭ螳・            if self.worker_thread and self.worker_thread.workflow_processor:
                self.worker_thread.workflow_processor.set_selected_work_folder(folder_path)
        
        dialog.folder_confirmed.connect(on_folder_confirmed)
        
        # 繝繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ
        result = dialog.exec()
        if result != dialog.Accepted:
            # 繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺輔ｌ縺溷ｴ蜷・            self.log_panel.append_log("繝輔か繝ｫ繝驕ｸ謚槭′繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺輔ｌ縺ｾ縺励◆", "WARNING")
            if self.worker_thread and self.worker_thread.workflow_processor:
                self.worker_thread.workflow_processor.set_selected_work_folder(None)
    
    @pyqtSlot(str, list, object)
    def on_file_placement_confirmation_needed(self, honbun_folder_path, file_list, callback):
        """繝輔ぃ繧､繝ｫ驟咲ｽｮ遒ｺ隱阪ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ"""
        try:
            # 繝輔ぃ繧､繝ｫ蜷搾ｿｽE繝ｪ繧ｹ繝医ｒ菴懶ｿｽE
            file_names = [f.name for f in file_list[:10]]  # 譛螟ｧ10蛟九∪縺ｧ陦ｨ遉ｺ
            if len(file_list) > 10:
                file_names.append(f"... 莉・{len(file_list) - 10} 繝輔ぃ繧､繝ｫ")
            file_list_str = "\n".join([f"窶｢ {name}" for name in file_names])
            
            # 譛蛻晢ｿｽE遒ｺ隱阪ム繧､繧｢繝ｭ繧ｰ
            reply = QMessageBox.question(
                self,
                "繝輔ぃ繧､繝ｫ驟咲ｽｮ遒ｺ隱・,
                f"莉･荳具ｿｽE繝輔か繝ｫ繝縺ｫ{len(file_list)}蛟具ｿｽEWord繝輔ぃ繧､繝ｫ・ｽE・ｽE陦檎岼蜑企勁貂医∩・ｽE・ｽ繧帝・鄂ｮ縺励∪縺吶・n\n"
                f"驟咲ｽｮ蜈・ {honbun_folder_path}\n\n"
                f"繝輔ぃ繧､繝ｫ:\n{file_list_str}\n\n"
                f"蜈ｨ縺ｦ縺ｮ繝輔ぃ繧､繝ｫ繧抵ｿｽE鄂ｮ縺励∪縺吶°・ｽE・ｽE,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                self.log_panel.append_log("繝輔ぃ繧､繝ｫ驟咲ｽｮ縺後く繝｣繝ｳ繧ｻ繝ｫ縺輔ｌ縺ｾ縺励◆", "INFO")
                if callback:
                    callback([])
                return
            
            if reply == QMessageBox.StandardButton.No:
                # 荳驛ｨ繝輔ぃ繧､繝ｫ縺ｮ縺ｿ驕ｸ謚・                dialog = SimpleFileSelectorDialog(file_list, self)
                if dialog.exec() == QMessageBox.Accepted:
                    selected_files = dialog.get_selected_files()
                    self.log_panel.append_log(f"繝輔ぃ繧､繝ｫ驕ｸ謚・ {len(selected_files)}蛟九ｒ驕ｸ謚・, "INFO")
                    if callback:
                        callback(selected_files)
                else:
                    self.log_panel.append_log("繝輔ぃ繧､繝ｫ驕ｸ謚槭′繧ｭ繝｣繝ｳ繧ｻ繝ｫ縺輔ｌ縺ｾ縺励◆", "INFO")
                    if callback:
                        callback([])
            else:
                # 蜈ｨ繝輔ぃ繧､繝ｫ繧抵ｿｽE鄂ｮ
                self.log_panel.append_log(f"繝輔ぃ繧､繝ｫ驟咲ｽｮ遒ｺ隱・ 蜈ｨ{len(file_list)}蛟具ｿｽE繝輔ぃ繧､繝ｫ繧抵ｿｽE鄂ｮ", "INFO")
                if callback:
                    callback(file_list)
                
        except Exception as e:
            self.log_panel.append_log(f"遒ｺ隱阪ム繧､繧｢繝ｭ繧ｰ繧ｨ繝ｩ繝ｼ: {e}", "ERROR")
            if callback:
                callback([])
    
    def closeEvent(self, event):
        """繧ｦ繧｣繝ｳ繝峨え繧帝哩縺倥ｋ譎ゑｿｽE蜃ｦ逅・""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "邨ゆｺ・・ｽE遒ｺ隱・,
                "蜃ｦ逅・・ｽ・ｽ螳溯｡御ｸｭ縺ｧ縺吶らｵゆｺ・・ｽ・ｽ縺ｾ縺吶°・ｽE・ｽE,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            # 繧ｹ繝ｬ繝・・ｽ・ｽ繧貞●豁｢
            self.worker_thread.terminate()
            self.worker_thread.wait()
        
        event.accept()
    
    @pyqtSlot()
    def show_process_mode_dialog(self):
        """蜃ｦ逅・・ｽ・ｽ蠑城∈謚槭ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ"""
        dialog = ProcessModeDialog(self)
        if dialog.exec() == dialog.Accepted:
            self.process_mode = dialog.get_selected_mode()
            mode_text = "API譁ｹ蠑・ if self.process_mode == ProcessModeDialog.MODE_API else "蠕捺擂譁ｹ蠑・
            self.log_panel.append_log(f"蜃ｦ逅・・ｽ・ｽ蠑上ｒ螟画峩: {mode_text}", "INFO")
            self.status_bar.showMessage(f"蜃ｦ逅・・ｽ・ｽ蠑・ {mode_text}")
    
    @pyqtSlot(list, str)
    def on_warning_dialog_needed(self, messages, result_type):
        """API蜃ｦ逅・・ｽE隴ｦ蜻翫ム繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ"""
        self.log_panel.append_log(f"隴ｦ蜻翫ム繧､繧｢繝ｭ繧ｰ陦ｨ遉ｺ隕∵ｱ・ {len(messages)}莉ｶ縺ｮ繝｡繝・・ｽ・ｽ繝ｼ繧ｸ ({result_type})", "INFO")
        
        # 繧ｷ繝ｳ繝励Ν縺ｪQMessageBox繧｢繝励Ο繝ｼ繝√ｒ菴ｿ逕ｨ・ｽE・ｽ荳譎ら噪縺ｪ蝗樣∩遲厄ｼ・        USE_SIMPLE_DIALOG = True
        
        if USE_SIMPLE_DIALOG:
            # QMessageBox繝呻ｿｽE繧ｹ縺ｮ繧ｷ繝ｳ繝励Ν縺ｪ繝繧､繧｢繝ｭ繧ｰ
            from gui.dialogs.simple_warning_dialog import show_warning_dialog
            show_warning_dialog(self, messages, result_type)
            self.log_panel.append_log("隴ｦ蜻翫ム繧､繧｢繝ｭ繧ｰ繧帝哩縺倥∪縺励◆", "INFO")
        else:
            # 繧ｫ繧ｹ繧ｿ繝繝繧､繧｢繝ｭ繧ｰ・ｽE・ｽ・ｽE縺ｮ螳溯｣・・ｽ・ｽE            # 繧､繝吶Φ繝医ｒ蜃ｦ逅・・ｽ・ｽ縺帙ｋ
            QCoreApplication.processEvents()
            
            # 繝繧､繧｢繝ｭ繧ｰ繧剃ｽ懶ｿｽE縺励※陦ｨ遉ｺ
            dialog = WarningDialog(messages, result_type, self)
            
            # 繝｢繝ｼ繝繝ｫ繝繧､繧｢繝ｭ繧ｰ縺ｨ縺励※螳溯｡・            result = dialog.exec()
            
            self.log_panel.append_log(f"隴ｦ蜻翫ム繧､繧｢繝ｭ繧ｰ繧帝哩縺倥∪縺励◆ (邨先棡: {result})", "INFO")