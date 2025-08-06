from __future__ import annotations
"""リポジトリ設定ダイアログ"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

from utils.logger import get_logger
from utils.config import get_config, save_config
from core.git_repository_manager import GitRepositoryManager


class RepositorySettingsDialog(QDialog):
    """リポジトリ設定を管理するダイアログ"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.git_manager = GitRepositoryManager()
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """UIを初期化"""
        self.setWindowTitle("リポジトリ設定")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # GitHub設定グループ
        github_group = QGroupBox("GitHub設定")
        github_layout = QVBoxLayout()
        
        # GitHubユーザー名
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("GitHubユーザー:"))
        self.github_user_edit = QLineEdit()
        user_layout.addWidget(self.github_user_edit)
        github_layout.addLayout(user_layout)
        
        # GitHubトークン
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("GitHubトークン:"))
        self.github_token_edit = QLineEdit()
        self.github_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.github_token_edit.setPlaceholderText("環境変数GITHUB_TOKENまたは直接入力")
        token_layout.addWidget(self.github_token_edit)
        github_layout.addLayout(token_layout)
        
        # リモートリポジトリ使用オプション
        self.use_remote_check = QCheckBox("リモートリポジトリを使用する")
        self.use_remote_check.setChecked(True)
        github_layout.addWidget(self.use_remote_check)
        
        github_group.setLayout(github_layout)
        layout.addWidget(github_group)
        
        # 繝ｭ繝ｼ繧ｫ繝ｫ險ｭ螳壹げ繝ｫ繝ｼ繝・        local_group = QGroupBox("ローカル設定")
        local_layout = QVBoxLayout()
        
        # Google Drive繝代せ
        drive_layout = QHBoxLayout()
        drive_layout.addWidget(QLabel("Google Drive繝代せ:"))
        self.drive_path_edit = QLineEdit()
        drive_layout.addWidget(self.drive_path_edit)
        browse_button = QPushButton("蜿ら・...")
        browse_button.clicked.connect(self.browse_drive_path)
        drive_layout.addWidget(browse_button)
        local_layout.addLayout(drive_layout)
        
        local_group.setLayout(local_layout)
        layout.addWidget(local_group)
        
        # 繧ｭ繝｣繝・す繝･諠・ｱ繧ｰ繝ｫ繝ｼ繝・        cache_group = QGroupBox("キャッシュ情報")
        cache_layout = QVBoxLayout()
        
        self.cache_info_text = QTextEdit()
        self.cache_info_text.setReadOnly(True)
        self.cache_info_text.setMaximumHeight(150)
        cache_layout.addWidget(self.cache_info_text)
        
        cache_button_layout = QHBoxLayout()
        refresh_button = QPushButton("繧ｭ繝｣繝・す繝･諠・ｱ譖ｴ譁ｰ")
        refresh_button.clicked.connect(self.refresh_cache_info)
        cache_button_layout.addWidget(refresh_button)
        
        clear_button = QPushButton("繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繧｢")
        clear_button.clicked.connect(self.clear_cache)
        cache_button_layout.addWidget(clear_button)
        
        cache_layout.addLayout(cache_button_layout)
        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)
        
        # 繝懊ち繝ｳ
        button_layout = QHBoxLayout()
        
        test_button = QPushButton("接続テスト")
        test_button.clicked.connect(self.test_connection)
        button_layout.addWidget(test_button)
        
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 蛻晄悄繧ｭ繝｣繝・す繝･諠・ｱ陦ｨ遉ｺ
        self.refresh_cache_info()
    
    def load_settings(self):
        """險ｭ螳壹ｒ隱ｭ縺ｿ霎ｼ縺ｿ"""
        self.github_user_edit.setText(
            self.config.get('github.default_user', 'irdtechbook')
        )
        
        # 繝医・繧ｯ繝ｳ縺ｯ迺ｰ蠅・､画焚縺九ｉ隱ｭ縺ｿ霎ｼ縺ｿ・医そ繧ｭ繝･繝ｪ繝・ぅ縺ｮ縺溘ａ・・        import os
        token = os.environ.get('GITHUB_TOKEN', '')
        if token:
            self.github_token_edit.setText(token)
        
        self.use_remote_check.setChecked(
            self.config.get('github.use_remote', True)
        )
        
        self.drive_path_edit.setText(
            self.config.get('paths.git_base', '')
        )
    
    def save_settings(self):
        """險ｭ螳壹ｒ菫晏ｭ・""
        try:
            # GitHub險ｭ螳・            self.config.data['github']['default_user'] = self.github_user_edit.text()
            self.config.data['github']['use_remote'] = self.use_remote_check.isChecked()
            
            # 繝ｭ繝ｼ繧ｫ繝ｫ險ｭ螳・            self.config.data['paths']['git_base'] = self.drive_path_edit.text()
            
            # 險ｭ螳壹ｒ菫晏ｭ・            save_config(self.config.data)
            
            # 繝医・繧ｯ繝ｳ縺ｯ迺ｰ蠅・､画焚縺ｨ縺励※險ｭ螳壹ｒ謗ｨ螂ｨ
            token = self.github_token_edit.text()
            if token:
                import os
                os.environ['GITHUB_TOKEN'] = token
                QMessageBox.information(
                    self,
                    "繝医・繧ｯ繝ｳ險ｭ螳・,
                    "GitHub繝医・繧ｯ繝ｳ縺ｯ迺ｰ蠅・､画焚縺ｨ縺励※險ｭ螳壹＆繧後∪縺励◆縲・n"
                    "豌ｸ邯夂噪縺ｫ菴ｿ逕ｨ縺吶ｋ蝣ｴ蜷医・縲√す繧ｹ繝・Β縺ｮ迺ｰ蠅・､画焚縺ｫ險ｭ螳壹＠縺ｦ縺上□縺輔＞縲・
                )
            
            QMessageBox.information(self, "菫晏ｭ伜ｮ御ｺ・, "險ｭ螳壹ｒ菫晏ｭ倥＠縺ｾ縺励◆")
            self.accept()
            
        except Exception as e:
            self.logger.error(f"險ｭ螳壻ｿ晏ｭ倥お繝ｩ繝ｼ: {e}")
            QMessageBox.critical(self, "繧ｨ繝ｩ繝ｼ", f"險ｭ螳壹・菫晏ｭ倥↓螟ｱ謨励＠縺ｾ縺励◆:\n{e}")
    
    def browse_drive_path(self):
        """Google Drive繝代せ繧貞盾辣ｧ"""
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(
            self,
            "Google Drive繝代せ繧帝∈謚・,
            self.drive_path_edit.text()
        )
        if path:
            self.drive_path_edit.setText(path)
    
    def test_connection(self):
        """謗･邯壹ユ繧ｹ繝・""
        try:
            # 繝・せ繝育畑縺ｮ繝ｪ繝昴ず繝医Μ蜷・            test_repo = "test-repository"
            
            QMessageBox.information(
                self,
                "謗･邯壹ユ繧ｹ繝・,
                f"GitHub繝ｦ繝ｼ繧ｶ繝ｼ '{self.github_user_edit.text()}' 縺ｸ縺ｮ謗･邯壹ｒ繝・せ繝医＠縺ｾ縺吶・n"
                f"繝・せ繝医Μ繝昴ず繝医Μ: {test_repo}"
            )
            
            # 螳滄圀縺ｮ繝・せ繝医・螳溯｣・↓蠢懊§縺ｦ隱ｿ謨ｴ
            QMessageBox.information(
                self,
                "繝・せ繝育ｵ先棡",
                "謗･邯壹ユ繧ｹ繝医・螳溯｣・＆繧後※縺・∪縺帙ｓ縲・n"
                "螳滄圀縺ｮ菴ｿ逕ｨ譎ゅ↓謗･邯壹′遒ｺ隱阪＆繧後∪縺吶・
            )
            
        except Exception as e:
            self.logger.error(f"謗･邯壹ユ繧ｹ繝医お繝ｩ繝ｼ: {e}")
            QMessageBox.critical(self, "繧ｨ繝ｩ繝ｼ", f"謗･邯壹ユ繧ｹ繝医↓螟ｱ謨励＠縺ｾ縺励◆:\n{e}")
    
    def refresh_cache_info(self):
        """繧ｭ繝｣繝・す繝･諠・ｱ繧呈峩譁ｰ"""
        try:
            info = self.git_manager.get_cache_info()
            
            text = f"繧ｭ繝｣繝・す繝･繝・ぅ繝ｬ繧ｯ繝医Μ: {info['cache_dir']}\n"
            text += f"繝ｪ繝昴ず繝医Μ謨ｰ: {info['repository_count']}\n"
            text += f"蜷郁ｨ医し繧､繧ｺ: {info['total_size'] / 1024 / 1024:.2f} MB\n\n"
            
            if info['repositories']:
                text += "繧ｭ繝｣繝・す繝･縺輔ｌ縺溘Μ繝昴ず繝医Μ:\n"
                for repo in info['repositories']:
                    text += f"  - {repo['name']} ({repo['size'] / 1024 / 1024:.2f} MB)\n"
            
            self.cache_info_text.setText(text)
            
        except Exception as e:
            self.logger.error(f"繧ｭ繝｣繝・す繝･諠・ｱ蜿門ｾ励お繝ｩ繝ｼ: {e}")
            self.cache_info_text.setText(f"繧ｭ繝｣繝・す繝･諠・ｱ縺ｮ蜿門ｾ励↓螟ｱ謨励＠縺ｾ縺励◆: {e}")
    
    def clear_cache(self):
        """繧ｭ繝｣繝・す繝･繧偵け繝ｪ繧｢"""
        reply = QMessageBox.question(
            self,
            "遒ｺ隱・,
            "縺吶∋縺ｦ縺ｮ繧ｭ繝｣繝・す繝･繧偵け繝ｪ繧｢縺励∪縺吶°・・,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.git_manager.clear_cache()
                QMessageBox.information(self, "螳御ｺ・, "繧ｭ繝｣繝・す繝･繧偵け繝ｪ繧｢縺励∪縺励◆")
                self.refresh_cache_info()
            except Exception as e:
                self.logger.error(f"繧ｭ繝｣繝・す繝･繧ｯ繝ｪ繧｢繧ｨ繝ｩ繝ｼ: {e}")
                QMessageBox.critical(self, "繧ｨ繝ｩ繝ｼ", f"繧ｭ繝｣繝・す繝･縺ｮ繧ｯ繝ｪ繧｢縺ｫ螟ｱ謨励＠縺ｾ縺励◆:\n{e}")