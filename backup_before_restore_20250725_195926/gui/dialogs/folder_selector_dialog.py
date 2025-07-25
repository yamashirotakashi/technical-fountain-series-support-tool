"""繝輔か繝ｫ繝驕ｸ謚槭ム繧､繧｢繝ｭ繧ｰ"""
import json
import os
from pathlib import Path
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QCheckBox, QSplitter, QTextEdit, QMessageBox,
    QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from utils.logger import get_logger


class FolderSelectorDialog(QDialog):
    """菴懈･ｭ繝輔か繝ｫ繝驕ｸ謚槭ム繧､繧｢繝ｭ繧ｰ"""
    
    folder_confirmed = pyqtSignal(str, bool)  # (驕ｸ謚槭＆繧後◆繝代せ, 險ｭ螳壹ｒ菫晏ｭ倥☆繧九°)
    
    def __init__(self, repo_path: Path, repo_name: str, default_folder: Optional[Path] = None, parent=None):
        """
        Args:
            repo_path: 繝ｪ繝昴ず繝医Μ縺ｮ繝ｫ繝ｼ繝医ヱ繧ｹ
            repo_name: 繝ｪ繝昴ず繝医Μ蜷搾ｼ郁ｨｭ螳壻ｿ晏ｭ倡畑・・            default_folder: 繝・ヵ繧ｩ繝ｫ繝医〒驕ｸ謚槭☆繧九ヵ繧ｩ繝ｫ繝
            parent: 隕ｪ繧ｦ繧｣繧ｸ繧ｧ繝・ヨ
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.repo_path = repo_path
        self.repo_name = repo_name
        self.default_folder = default_folder
        self.selected_folder = default_folder
        
        # 菫晏ｭ倥＆繧後◆險ｭ螳壹ｒ隱ｭ縺ｿ霎ｼ繧
        self.settings_file = Path.home() / ".techzip" / "folder_settings.json"
        self.saved_settings = self._load_settings()
        
        self.setup_ui()
        self._populate_tree()
        
        # 繝・ヵ繧ｩ繝ｫ繝医ヵ繧ｩ繝ｫ繝縺ｾ縺溘・菫晏ｭ倥＆繧後◆險ｭ螳壹ｒ驕ｸ謚・        if self.repo_name in self.saved_settings:
            saved_path = Path(self.saved_settings[self.repo_name])
            if saved_path.exists() and str(saved_path).startswith(str(repo_path)):
                self._select_folder_in_tree(saved_path)
        elif default_folder:
            self._select_folder_in_tree(default_folder)
    
    def setup_ui(self):
        """UI繧定ｨｭ螳・""
        self.setWindowTitle("菴懈･ｭ繝輔か繝ｫ繝縺ｮ驕ｸ謚・)
        self.setModal(True)
        self.resize(800, 600)
        
        # 繝｡繧､繝ｳ繝ｬ繧､繧｢繧ｦ繝・        main_layout = QVBoxLayout(self)
        
        # 隱ｬ譏弱Λ繝吶Ν
        info_label = QLabel(
            "Re:VIEW髢｢騾｣繝輔ぃ繧､繝ｫ・・re, config.yml, catalog.yml・峨′蜷ｫ縺ｾ繧後ｋ繝輔か繝ｫ繝繧帝∈謚槭＠縺ｦ縺上□縺輔＞縲・
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # 繧ｹ繝励Μ繝・ち繝ｼ・医ヤ繝ｪ繝ｼ縺ｨ繝励Ξ繝薙Η繝ｼ・・        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 繝輔ぃ繧､繝ｫ繝・Μ繝ｼ
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("繝輔か繝ｫ繝讒矩")
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        splitter.addWidget(self.tree_widget)
        
        # 繝励Ξ繝薙Η繝ｼ繧ｨ繝ｪ繧｢
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_label = QLabel("驕ｸ謚槭＆繧後◆繝輔か繝ｫ繝:")
        preview_label.setFont(QFont("", 10, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)
        
        self.path_label = QLabel("")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; }")
        preview_layout.addWidget(self.path_label)
        
        preview_label2 = QLabel("繝輔か繝ｫ繝蜀・ｮｹ:")
        preview_label2.setFont(QFont("", 10, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label2)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([400, 400])
        
        main_layout.addWidget(splitter)
        
        # 繝√ぉ繝・け繝懊ャ繧ｯ繧ｹ
        self.save_settings_checkbox = QCheckBox("谺｡蝗槭°繧峨ｂ蜷後§繝輔か繝ｫ繝縺ｧ菴懈･ｭ")
        if self.repo_name in self.saved_settings:
            self.save_settings_checkbox.setChecked(True)
        main_layout.addWidget(self.save_settings_checkbox)
        
        # 繝懊ち繝ｳ繧ｨ繝ｪ繧｢
        button_layout = QHBoxLayout()
        
        self.change_button = QPushButton("螟画峩")
        self.change_button.setEnabled(False)
        self.change_button.clicked.connect(self._on_change_clicked)
        button_layout.addWidget(self.change_button)
        
        self.confirm_button = QPushButton("Zip菴懈・")
        self.confirm_button.setDefault(True)
        self.confirm_button.clicked.connect(self._on_confirm_clicked)
        button_layout.addWidget(self.confirm_button)
        
        cancel_button = QPushButton("繧ｭ繝｣繝ｳ繧ｻ繝ｫ")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def _populate_tree(self):
        """繝輔ぃ繧､繝ｫ繝・Μ繝ｼ繧呈ｧ狗ｯ・""
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, self.repo_path.name)
        root_item.setData(0, Qt.UserRole, str(self.repo_path))
        root_item.setExpanded(True)
        
        # 繧｢繧､繧ｳ繝ｳ繧定ｨｭ螳・        root_item.setIcon(0, self.style().standardIcon(self.style().SP_DirIcon))
        
        self._add_tree_items(root_item, self.repo_path)
    
    def _add_tree_items(self, parent_item: QTreeWidgetItem, parent_path: Path):
        """繝・Μ繝ｼ繧｢繧､繝・Β繧貞・蟶ｰ逧・↓霑ｽ蜉"""
        try:
            # 繝輔か繝ｫ繝縺ｮ縺ｿ繧定｡ｨ遉ｺ
            for item in sorted(parent_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, item.name)
                    child_item.setData(0, Qt.UserRole, str(item))
                    
                    # Re:VIEW繝輔か繝ｫ繝縺九メ繧ｧ繝・け
                    if self._is_review_folder(item):
                        child_item.setIcon(0, self.style().standardIcon(self.style().SP_DirOpenIcon))
                        # 螟ｪ蟄励〒陦ｨ遉ｺ
                        font = child_item.font(0)
                        font.setBold(True)
                        child_item.setFont(0, font)
                    else:
                        child_item.setIcon(0, self.style().standardIcon(self.style().SP_DirIcon))
                    
                    # 蜀榊ｸｰ逧・↓蟄舌い繧､繝・Β繧定ｿｽ蜉
                    self._add_tree_items(child_item, item)
        except PermissionError:
            pass
    
    def _is_review_folder(self, path: Path) -> bool:
        """Re:VIEW繝輔か繝ｫ繝縺九メ繧ｧ繝・け"""
        required_files = {'config.yml', 'catalog.yml'}
        
        try:
            # .re繝輔ぃ繧､繝ｫ縺ｮ蟄伜惠遒ｺ隱・            has_re_file = any(f.suffix == '.re' for f in path.iterdir() if f.is_file())
            
            # 蠢・医ヵ繧｡繧､繝ｫ縺ｮ蟄伜惠遒ｺ隱・            existing_files = {f.name for f in path.iterdir() if f.is_file()}
            has_required_files = required_files.issubset(existing_files)
            
            return has_re_file and has_required_files
        except:
            return False
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """繧｢繧､繝・Β繧ｯ繝ｪ繝・け譎ゅ・蜃ｦ逅・""
        path = Path(item.data(0, Qt.UserRole))
        self.selected_folder = path
        
        # 繝代せ繧定｡ｨ遉ｺ
        self.path_label.setText(str(path))
        
        # 繝輔か繝ｫ繝蜀・ｮｹ繧偵・繝ｬ繝薙Η繝ｼ
        self._update_preview(path)
        
        # 螟画峩繝懊ち繝ｳ繧呈怏蜉ｹ蛹・        self.change_button.setEnabled(True)
    
    def _update_preview(self, path: Path):
        """繝輔か繝ｫ繝蜀・ｮｹ縺ｮ繝励Ξ繝薙Η繝ｼ繧呈峩譁ｰ"""
        preview_lines = []
        
        try:
            # Re:VIEW繝輔か繝ｫ繝縺九メ繧ｧ繝・け
            is_review = self._is_review_folder(path)
            if is_review:
                preview_lines.append("笨・Re:VIEW繝輔か繝ｫ繝縺ｨ縺励※隱崎ｭ倥＆繧後∪縺励◆\n")
            else:
                preview_lines.append("笞・・Re:VIEW繝輔か繝ｫ繝縺ｮ隕∽ｻｶ繧呈ｺ縺溘＠縺ｦ縺・∪縺帙ｓ\n")
            
            preview_lines.append("縲舌ヵ繧｡繧､繝ｫ荳隕ｧ縲・)
            
            # 繝輔ぃ繧､繝ｫ荳隕ｧ・域怙螟ｧ20蛟具ｼ・            files = sorted(path.iterdir())[:20]
            for file in files:
                if file.is_file():
                    # 驥崎ｦ√↑繝輔ぃ繧､繝ｫ繧偵ワ繧､繝ｩ繧､繝・                    if file.name in ['config.yml', 'catalog.yml']:
                        preview_lines.append(f"  塘 {file.name} 笨・)
                    elif file.suffix == '.re':
                        preview_lines.append(f"  統 {file.name} 笨・)
                    else:
                        preview_lines.append(f"  塘 {file.name}")
                else:
                    preview_lines.append(f"  刀 {file.name}/")
            
            if len(list(path.iterdir())) > 20:
                preview_lines.append("  ...")
            
        except Exception as e:
            preview_lines.append(f"繧ｨ繝ｩ繝ｼ: {e}")
        
        self.preview_text.setPlainText("\n".join(preview_lines))
    
    def _select_folder_in_tree(self, folder_path: Path):
        """繝・Μ繝ｼ蜀・・謖・ｮ壹ヵ繧ｩ繝ｫ繝繧帝∈謚・""
        # 繝ｫ繝ｼ繝医°繧蛾・↓繝代せ繧定ｾｿ繧・        relative_path = folder_path.relative_to(self.repo_path)
        parts = relative_path.parts if relative_path.parts else []
        
        current_item = self.tree_widget.topLevelItem(0)
        current_item.setExpanded(True)
        
        for part in parts:
            found = False
            for i in range(current_item.childCount()):
                child = current_item.child(i)
                if child.text(0) == part:
                    current_item = child
                    current_item.setExpanded(True)
                    found = True
                    break
            
            if not found:
                break
        
        # 譛邨ら噪縺ｪ繧｢繧､繝・Β繧帝∈謚・        self.tree_widget.setCurrentItem(current_item)
        self._on_item_clicked(current_item, 0)
    
    def _on_change_clicked(self):
        """螟画峩繝懊ち繝ｳ繧ｯ繝ｪ繝・け譎・""
        if not self.selected_folder:
            QMessageBox.warning(self, "隴ｦ蜻・, "繝輔か繝ｫ繝繧帝∈謚槭＠縺ｦ縺上□縺輔＞縲・)
            return
        
        # Re:VIEW繝輔か繝ｫ繝縺ｧ縺ｪ縺・ｴ蜷医・隴ｦ蜻・        if not self._is_review_folder(self.selected_folder):
            reply = QMessageBox.warning(
                self, "遒ｺ隱・,
                "驕ｸ謚槭＆繧後◆繝輔か繝ｫ繝縺ｫ縺ｯRe:VIEW縺ｮ蠢・医ヵ繧｡繧､繝ｫ縺悟性縺ｾ繧後※縺・∪縺帙ｓ縲・n"
                "縺薙・繝輔か繝ｫ繝繧剃ｽｿ逕ｨ縺励∪縺吶°・・,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # 驕ｸ謚槭ｒ遒ｺ螳夲ｼ医ム繧､繧｢繝ｭ繧ｰ縺ｯ髢峨§縺ｪ縺・ｼ・        self.path_label.setText(f"笨・{str(self.selected_folder)}")
        QMessageBox.information(self, "遒ｺ隱・, "繝輔か繝ｫ繝縺悟､画峩縺輔ｌ縺ｾ縺励◆縲・)
    
    def _on_confirm_clicked(self):
        """Zip菴懈・繝懊ち繝ｳ繧ｯ繝ｪ繝・け譎・""
        if not self.selected_folder:
            QMessageBox.warning(self, "隴ｦ蜻・, "繝輔か繝ｫ繝繧帝∈謚槭＠縺ｦ縺上□縺輔＞縲・)
            return
        
        # 險ｭ螳壹ｒ菫晏ｭ倥☆繧九°繝√ぉ繝・け
        save_settings = self.save_settings_checkbox.isChecked()
        
        if save_settings:
            self._save_settings(self.repo_name, str(self.selected_folder))
        
        # 繧ｷ繧ｰ繝翫Ν繧堤匱陦後＠縺ｦ繝繧､繧｢繝ｭ繧ｰ繧帝哩縺倥ｋ
        self.folder_confirmed.emit(str(self.selected_folder), save_settings)
        self.accept()
    
    def _load_settings(self) -> Dict[str, str]:
        """菫晏ｭ倥＆繧後◆險ｭ螳壹ｒ隱ｭ縺ｿ霎ｼ繧"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ隱ｭ縺ｿ霎ｼ縺ｿ繧ｨ繝ｩ繝ｼ: {e}")
        return {}
    
    def _save_settings(self, repo_name: str, folder_path: str):
        """險ｭ螳壹ｒ菫晏ｭ・""
        settings = self._load_settings()
        settings[repo_name] = folder_path
        
        # 繝・ぅ繝ｬ繧ｯ繝医Μ繧剃ｽ懈・
        self.settings_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.logger.info(f"繝輔か繝ｫ繝險ｭ螳壹ｒ菫晏ｭ・ {repo_name} -> {folder_path}")
        except Exception as e:
            self.logger.error(f"險ｭ螳壹ヵ繧｡繧､繝ｫ縺ｮ菫晏ｭ倥お繝ｩ繝ｼ: {e}")