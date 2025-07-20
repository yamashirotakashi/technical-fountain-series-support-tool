"""リポジトリ設定ダイアログモジュール"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt

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
        self.github_token_edit.setEchoMode(QLineEdit.Password)
        self.github_token_edit.setPlaceholderText("オプション（プライベートリポジトリ用）")
        token_layout.addWidget(self.github_token_edit)
        github_layout.addLayout(token_layout)
        
        # リモート優先チェックボックス
        self.use_remote_check = QCheckBox("リモートリポジトリを優先的に使用")
        self.use_remote_check.setChecked(True)
        github_layout.addWidget(self.use_remote_check)
        
        github_group.setLayout(github_layout)
        layout.addWidget(github_group)
        
        # ローカル設定グループ
        local_group = QGroupBox("ローカル設定")
        local_layout = QVBoxLayout()
        
        # Google Driveパス
        drive_layout = QHBoxLayout()
        drive_layout.addWidget(QLabel("Google Driveパス:"))
        self.drive_path_edit = QLineEdit()
        drive_layout.addWidget(self.drive_path_edit)
        browse_button = QPushButton("参照...")
        browse_button.clicked.connect(self.browse_drive_path)
        drive_layout.addWidget(browse_button)
        local_layout.addLayout(drive_layout)
        
        local_group.setLayout(local_layout)
        layout.addWidget(local_group)
        
        # キャッシュ情報グループ
        cache_group = QGroupBox("キャッシュ情報")
        cache_layout = QVBoxLayout()
        
        self.cache_info_text = QTextEdit()
        self.cache_info_text.setReadOnly(True)
        self.cache_info_text.setMaximumHeight(150)
        cache_layout.addWidget(self.cache_info_text)
        
        cache_button_layout = QHBoxLayout()
        refresh_button = QPushButton("キャッシュ情報更新")
        refresh_button.clicked.connect(self.refresh_cache_info)
        cache_button_layout.addWidget(refresh_button)
        
        clear_button = QPushButton("キャッシュクリア")
        clear_button.clicked.connect(self.clear_cache)
        cache_button_layout.addWidget(clear_button)
        
        cache_layout.addLayout(cache_button_layout)
        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)
        
        # ボタン
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
        
        # 初期キャッシュ情報表示
        self.refresh_cache_info()
    
    def load_settings(self):
        """設定を読み込み"""
        self.github_user_edit.setText(
            self.config.get('github.default_user', 'irdtechbook')
        )
        
        # トークンは環境変数から読み込み（セキュリティのため）
        import os
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
        """設定を保存"""
        try:
            # GitHub設定
            self.config.data['github']['default_user'] = self.github_user_edit.text()
            self.config.data['github']['use_remote'] = self.use_remote_check.isChecked()
            
            # ローカル設定
            self.config.data['paths']['git_base'] = self.drive_path_edit.text()
            
            # 設定を保存
            save_config(self.config.data)
            
            # トークンは環境変数として設定を推奨
            token = self.github_token_edit.text()
            if token:
                import os
                os.environ['GITHUB_TOKEN'] = token
                QMessageBox.information(
                    self,
                    "トークン設定",
                    "GitHubトークンは環境変数として設定されました。\n"
                    "永続的に使用する場合は、システムの環境変数に設定してください。"
                )
            
            QMessageBox.information(self, "保存完了", "設定を保存しました")
            self.accept()
            
        except Exception as e:
            self.logger.error(f"設定保存エラー: {e}")
            QMessageBox.critical(self, "エラー", f"設定の保存に失敗しました:\n{e}")
    
    def browse_drive_path(self):
        """Google Driveパスを参照"""
        from PyQt5.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(
            self,
            "Google Driveパスを選択",
            self.drive_path_edit.text()
        )
        if path:
            self.drive_path_edit.setText(path)
    
    def test_connection(self):
        """接続テスト"""
        try:
            # テスト用のリポジトリ名
            test_repo = "test-repository"
            
            QMessageBox.information(
                self,
                "接続テスト",
                f"GitHubユーザー '{self.github_user_edit.text()}' への接続をテストします。\n"
                f"テストリポジトリ: {test_repo}"
            )
            
            # 実際のテストは実装に応じて調整
            QMessageBox.information(
                self,
                "テスト結果",
                "接続テストは実装されていません。\n"
                "実際の使用時に接続が確認されます。"
            )
            
        except Exception as e:
            self.logger.error(f"接続テストエラー: {e}")
            QMessageBox.critical(self, "エラー", f"接続テストに失敗しました:\n{e}")
    
    def refresh_cache_info(self):
        """キャッシュ情報を更新"""
        try:
            info = self.git_manager.get_cache_info()
            
            text = f"キャッシュディレクトリ: {info['cache_dir']}\n"
            text += f"リポジトリ数: {info['repository_count']}\n"
            text += f"合計サイズ: {info['total_size'] / 1024 / 1024:.2f} MB\n\n"
            
            if info['repositories']:
                text += "キャッシュされたリポジトリ:\n"
                for repo in info['repositories']:
                    text += f"  - {repo['name']} ({repo['size'] / 1024 / 1024:.2f} MB)\n"
            
            self.cache_info_text.setText(text)
            
        except Exception as e:
            self.logger.error(f"キャッシュ情報取得エラー: {e}")
            self.cache_info_text.setText(f"キャッシュ情報の取得に失敗しました: {e}")
    
    def clear_cache(self):
        """キャッシュをクリア"""
        reply = QMessageBox.question(
            self,
            "確認",
            "すべてのキャッシュをクリアしますか？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.git_manager.clear_cache()
                QMessageBox.information(self, "完了", "キャッシュをクリアしました")
                self.refresh_cache_info()
            except Exception as e:
                self.logger.error(f"キャッシュクリアエラー: {e}")
                QMessageBox.critical(self, "エラー", f"キャッシュのクリアに失敗しました:\n{e}")