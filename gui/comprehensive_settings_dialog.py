"""包括的な設定ダイアログ - 認証情報と設定の統合管理"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QTextEdit,
    QGroupBox, QFormLayout, QFileDialog, QCheckBox,
    QMessageBox, QDialogButtonBox, QScrollArea,
    QWidget, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from utils.path_resolver import PathResolver
from utils.env_manager import EnvManager
from utils.config import get_config
from utils.logger import get_logger


class ComprehensiveSettingsDialog(QDialog):
    """包括的な設定ダイアログ"""
    
    settings_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.setWindowTitle("TechZip 設定")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        # 設定値を保持する辞書
        self.settings = {}
        
        # 既存の設定を読み込む
        self.load_current_settings()
        
        # UIを初期化
        self.init_ui()
        
    def load_current_settings(self):
        """現在の設定をすべて読み込む"""
        # 環境変数から
        self.settings['gmail_address'] = EnvManager.get('GMAIL_ADDRESS', '')
        self.settings['gmail_app_password'] = EnvManager.get('GMAIL_APP_PASSWORD', '')
        self.settings['slack_bot_token'] = EnvManager.get('SLACK_BOT_TOKEN', '')
        self.settings['github_token'] = EnvManager.get('GITHUB_TOKEN', '')
        
        # NextPublishing API（Word2XHTML5と同じ）
        # settings.jsonから読み込み（存在する場合）
        web_config = self.config.get('web', {})
        self.settings['nextpublishing_username'] = web_config.get('username', '') or EnvManager.get('WORD2XHTML5_USERNAME', '')
        self.settings['nextpublishing_password'] = web_config.get('password', '') or EnvManager.get('WORD2XHTML5_PASSWORD', '')
        
        # Word2XHTML5 設定（settings.jsonのweb設定を優先）
        self.settings['word2xhtml5_username'] = web_config.get('username', '') or EnvManager.get('WORD2XHTML5_USERNAME', '')
        self.settings['word2xhtml5_password'] = web_config.get('password', '') or EnvManager.get('WORD2XHTML5_PASSWORD', '')
        
        # 設定ファイルから
        self.settings['google_sheets_id'] = self.config.get('google_sheet.sheet_id', '') or EnvManager.get('GOOGLE_SHEETS_ID', '')
        self.settings['google_sheets_credentials_path'] = self.config.get('google_sheet.credentials_path', '') or EnvManager.get('GOOGLE_SHEETS_CREDENTIALS_PATH', '')
        self.settings['git_base_path'] = self.config.get('paths.git_base', '')
        self.settings['output_base_path'] = self.config.get('paths.output_base', '')
        
        # Gmail OAuth認証ファイルの存在確認
        gmail_oauth_path = PathResolver.resolve_config_file('gmail_oauth_credentials.json')
        self.settings['gmail_oauth_exists'] = gmail_oauth_path is not None
        self.settings['gmail_oauth_path'] = str(gmail_oauth_path) if gmail_oauth_path else ''
        
    def init_ui(self):
        """UIを初期化"""
        layout = QVBoxLayout(self)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 各タブを追加
        self.tab_widget.addTab(self.create_basic_tab(), "基本設定")
        self.tab_widget.addTab(self.create_google_tab(), "Google API")
        self.tab_widget.addTab(self.create_slack_tab(), "Slack連携")
        self.tab_widget.addTab(self.create_advanced_tab(), "詳細設定")
        self.tab_widget.addTab(self.create_environment_tab(), "環境情報")
        
        # ボタン
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def create_basic_tab(self):
        """基本設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Gmail設定
        gmail_group = QGroupBox("Gmail設定（IMAP/SMTP）")
        gmail_layout = QFormLayout()
        
        self.gmail_address_edit = QLineEdit(self.settings.get('gmail_address', ''))
        gmail_layout.addRow("メールアドレス:", self.gmail_address_edit)
        
        self.gmail_password_edit = QLineEdit(self.settings.get('gmail_app_password', ''))
        self.gmail_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        gmail_layout.addRow("アプリパスワード:", self.gmail_password_edit)
        
        gmail_help = QLabel(
            "<small>※2段階認証を有効にしてアプリパスワードを生成してください<br>"
            "<a href='https://support.google.com/accounts/answer/185833'>アプリパスワードの作成方法</a></small>"
        )
        gmail_help.setOpenExternalLinks(True)
        gmail_layout.addRow("", gmail_help)
        
        gmail_group.setLayout(gmail_layout)
        layout.addWidget(gmail_group)
        
        # パス設定
        path_group = QGroupBox("ディレクトリ設定")
        path_layout = QFormLayout()
        
        # Git基本ディレクトリ
        git_base_layout = QHBoxLayout()
        self.git_base_edit = QLineEdit(self.settings.get('git_base_path', ''))
        git_base_browse_btn = QPushButton("参照...")
        git_base_browse_btn.clicked.connect(lambda: self.browse_directory(self.git_base_edit))
        git_base_layout.addWidget(self.git_base_edit)
        git_base_layout.addWidget(git_base_browse_btn)
        path_layout.addRow("Gitベースディレクトリ:", git_base_layout)
        
        # 出力ディレクトリ
        output_base_layout = QHBoxLayout()
        self.output_base_edit = QLineEdit(self.settings.get('output_base_path', ''))
        output_base_browse_btn = QPushButton("参照...")
        output_base_browse_btn.clicked.connect(lambda: self.browse_directory(self.output_base_edit))
        output_base_layout.addWidget(self.output_base_edit)
        output_base_layout.addWidget(output_base_browse_btn)
        path_layout.addRow("出力ベースディレクトリ:", output_base_layout)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        layout.addStretch()
        return widget
        
    def create_google_tab(self):
        """Google APIタブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Google Sheets設定
        sheets_group = QGroupBox("Google Sheets API")
        sheets_layout = QFormLayout()
        
        self.sheets_id_edit = QLineEdit(self.settings.get('google_sheets_id', ''))
        sheets_layout.addRow("スプレッドシートID:", self.sheets_id_edit)
        
        # サービスアカウント認証ファイル
        sa_layout = QHBoxLayout()
        self.sheets_creds_edit = QLineEdit(self.settings.get('google_sheets_credentials_path', ''))
        sa_browse_btn = QPushButton("参照...")
        sa_browse_btn.clicked.connect(lambda: self.browse_json_file(self.sheets_creds_edit))
        sa_import_btn = QPushButton("インポート...")
        sa_import_btn.clicked.connect(self.import_google_sheets_credentials)
        sa_layout.addWidget(self.sheets_creds_edit)
        sa_layout.addWidget(sa_browse_btn)
        sa_layout.addWidget(sa_import_btn)
        sheets_layout.addRow("サービスアカウント認証:", sa_layout)
        
        sheets_help = QLabel(
            "<small>※Google Cloud ConsoleでサービスアカウントのJSONキーを生成してください</small>"
        )
        sheets_layout.addRow("", sheets_help)
        
        sheets_group.setLayout(sheets_layout)
        layout.addWidget(sheets_group)
        
        # Gmail OAuth設定
        oauth_group = QGroupBox("Gmail OAuth 2.0")
        oauth_layout = QFormLayout()
        
        # OAuth認証ファイル
        oauth_file_layout = QHBoxLayout()
        self.oauth_status_label = QLabel()
        self.update_oauth_status()
        oauth_file_layout.addWidget(self.oauth_status_label)
        
        oauth_browse_btn = QPushButton("認証ファイルを選択...")
        oauth_browse_btn.clicked.connect(self.import_oauth_credentials)
        oauth_file_layout.addWidget(oauth_browse_btn)
        
        oauth_layout.addRow("OAuth認証ファイル:", oauth_file_layout)
        
        # OAuth設定手順
        oauth_help = QLabel(
            "<small>Gmail APIを使用する場合の設定手順:<br>"
            "1. <a href='https://console.cloud.google.com/'>Google Cloud Console</a>にアクセス<br>"
            "2. APIs & Services > Credentials<br>"
            "3. 「+ CREATE CREDENTIALS」> OAuth client ID<br>"
            "4. Application type: Desktop application<br>"
            "5. ダウンロードしたJSONファイルを上記ボタンで選択</small>"
        )
        oauth_help.setOpenExternalLinks(True)
        oauth_help.setWordWrap(True)
        oauth_layout.addRow("", oauth_help)
        
        oauth_group.setLayout(oauth_layout)
        layout.addWidget(oauth_group)
        
        layout.addStretch()
        return widget
        
    def create_slack_tab(self):
        """Slack連携タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        slack_group = QGroupBox("Slack Bot設定")
        slack_layout = QFormLayout()
        
        self.slack_token_edit = QLineEdit(self.settings.get('slack_bot_token', ''))
        self.slack_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        slack_layout.addRow("Bot Token:", self.slack_token_edit)
        
        # トークン表示/非表示トグル
        show_token_cb = QCheckBox("トークンを表示")
        show_token_cb.toggled.connect(
            lambda checked: self.slack_token_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        slack_layout.addRow("", show_token_cb)
        
        slack_help = QLabel(
            "<small>Slack Botの作成手順:<br>"
            "1. <a href='https://api.slack.com/apps'>Slack API</a>でアプリを作成<br>"
            "2. OAuth & Permissions > Bot Token Scopesを設定<br>"
            "　　- channels:read (チャネル一覧取得)<br>"
            "　　- files:write (ファイルアップロード)<br>"
            "3. Install to Workspaceでインストール<br>"
            "4. Bot User OAuth Tokenをコピー (xoxb-で始まる)</small>"
        )
        slack_help.setOpenExternalLinks(True)
        slack_help.setWordWrap(True)
        slack_layout.addRow("", slack_help)
        
        slack_group.setLayout(slack_layout)
        layout.addWidget(slack_group)
        
        # GitHub設定
        github_group = QGroupBox("GitHub設定")
        github_layout = QFormLayout()
        
        self.github_token_edit = QLineEdit(self.settings.get('github_token', ''))
        self.github_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        github_layout.addRow("Personal Access Token:", self.github_token_edit)
        
        github_help = QLabel(
            "<small>※プライベートリポジトリにアクセスする場合に必要</small>"
        )
        github_layout.addRow("", github_help)
        
        github_group.setLayout(github_layout)
        layout.addWidget(github_group)
        
        layout.addStretch()
        return widget
        
    def create_advanced_tab(self):
        """詳細設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # NextPublishing設定（削除 - Word2XHTML5と統合）
        # NextPublishingはWord2XHTML5と同じサービスのため、統合します
        
        # Word2XHTML5設定
        w2x_group = QGroupBox("Word2XHTML5 変換サービス")
        w2x_layout = QFormLayout()
        
        self.w2x_username_edit = QLineEdit(self.settings.get('word2xhtml5_username', ''))
        w2x_layout.addRow("ユーザー名:", self.w2x_username_edit)
        
        self.w2x_password_edit = QLineEdit(self.settings.get('word2xhtml5_password', ''))
        self.w2x_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        w2x_layout.addRow("パスワード:", self.w2x_password_edit)
        
        w2x_help = QLabel(
            "<small>※NextPublishing Word2XHTML5変換サービスのアカウント情報<br>"
            "　デフォルト: ep_user / Nn7eUTX5<br>"
            "　URL: http://trial.nextpublishing.jp/</small>"
        )
        w2x_layout.addRow("", w2x_help)
        
        w2x_group.setLayout(w2x_layout)
        layout.addWidget(w2x_group)
        
        # デバッグ設定
        debug_group = QGroupBox("デバッグ設定")
        debug_layout = QFormLayout()
        
        self.debug_mode_cb = QCheckBox("デバッグモードを有効にする")
        self.debug_mode_cb.setChecked(EnvManager.get_bool('DEBUG_MODE', False))
        debug_layout.addRow("", self.debug_mode_cb)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        current_level = EnvManager.get('LOG_LEVEL', 'INFO')
        self.log_level_combo.setCurrentText(current_level)
        debug_layout.addRow("ログレベル:", self.log_level_combo)
        
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)
        
        layout.addStretch()
        return widget
        
    def create_environment_tab(self):
        """環境情報タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setFont(QFont("Consolas", 9))
        
        # 環境情報を収集
        info_lines = []
        info_lines.append("=== 実行環境情報 ===")
        info_lines.append(f"実行モード: {'EXE' if PathResolver.is_exe_environment() else '開発環境'}")
        info_lines.append(f"ベースパス: {PathResolver.get_base_path()}")
        info_lines.append(f"設定パス: {PathResolver.get_config_path()}")
        info_lines.append(f"ユーザーディレクトリ: {PathResolver.get_user_dir()}")
        info_lines.append("")
        
        info_lines.append("=== 認証情報の設定状況 ===")
        creds_info = EnvManager.get_credentials_info()
        for key, value in creds_info.items():
            status = "✓ 設定済み" if value else "✗ 未設定"
            info_lines.append(f"{key}: {status}")
        info_lines.append("")
        
        info_lines.append("=== 設定ファイルの場所 ===")
        info_lines.append(f"settings.json: {self.config.config_path}")
        env_file = PathResolver.get_user_dir() / '.env' if PathResolver.is_exe_environment() else Path('.env')
        info_lines.append(f".env: {env_file}")
        
        info_text.setPlainText("\n".join(info_lines))
        layout.addWidget(info_text)
        
        # エクスポート/インポートボタン
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("設定をエクスポート")
        export_btn.clicked.connect(self.export_settings)
        button_layout.addWidget(export_btn)
        
        import_btn = QPushButton("設定をインポート")
        import_btn.clicked.connect(self.import_settings)
        button_layout.addWidget(import_btn)
        
        open_folder_btn = QPushButton("設定フォルダを開く")
        open_folder_btn.clicked.connect(self.open_settings_folder)
        button_layout.addWidget(open_folder_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return widget
        
    def browse_directory(self, line_edit: QLineEdit):
        """ディレクトリ選択ダイアログ"""
        current_path = line_edit.text()
        if not current_path:
            current_path = str(Path.home())
            
        directory = QFileDialog.getExistingDirectory(
            self,
            "ディレクトリを選択",
            current_path
        )
        
        if directory:
            line_edit.setText(directory)
            
    def browse_json_file(self, line_edit: QLineEdit):
        """JSONファイル選択ダイアログ"""
        current_path = line_edit.text()
        if not current_path or not Path(current_path).parent.exists():
            current_path = str(Path.home())
        else:
            current_path = str(Path(current_path).parent)
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "JSONファイルを選択",
            current_path,
            "JSON Files (*.json)"
        )
        
        if file_path:
            line_edit.setText(file_path)
            
    def import_oauth_credentials(self):
        """Gmail OAuth認証ファイルをインポート"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Gmail OAuth認証ファイルを選択",
            str(Path.home()),
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                # ファイルの妥当性を確認
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'installed' not in data and 'web' not in data:
                        raise ValueError("OAuth 2.0クライアントIDファイルではありません")
                
                # 設定ディレクトリにコピー
                target_path = PathResolver.get_config_path() / 'gmail_oauth_credentials.json'
                
                import shutil
                shutil.copy2(file_path, target_path)
                
                self.settings['gmail_oauth_exists'] = True
                self.settings['gmail_oauth_path'] = str(target_path)
                self.update_oauth_status()
                
                QMessageBox.information(
                    self,
                    "インポート成功",
                    "Gmail OAuth認証ファイルをインポートしました。"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "インポートエラー",
                    f"認証ファイルのインポートに失敗しました:\n{str(e)}"
                )
                
    def update_oauth_status(self):
        """OAuth認証ファイルの状態を更新"""
        if self.settings.get('gmail_oauth_exists'):
            self.oauth_status_label.setText(
                f"<span style='color: green'>✓ 設定済み</span><br>"
                f"<small>{self.settings.get('gmail_oauth_path', '')}</small>"
            )
        else:
            self.oauth_status_label.setText(
                "<span style='color: red'>✗ 未設定</span>"
            )
            
    def save_settings(self):
        """設定を保存"""
        try:
            # .envファイルに保存する内容
            env_content = []
            
            # Gmail設定
            if self.gmail_address_edit.text():
                env_content.append(f"GMAIL_ADDRESS={self.gmail_address_edit.text()}")
            if self.gmail_password_edit.text():
                env_content.append(f"GMAIL_APP_PASSWORD={self.gmail_password_edit.text()}")
                
            # Slack設定
            if self.slack_token_edit.text():
                env_content.append(f"SLACK_BOT_TOKEN={self.slack_token_edit.text()}")
                
            # GitHub設定
            if self.github_token_edit.text():
                env_content.append(f"GITHUB_TOKEN={self.github_token_edit.text()}")
                
                
            # Word2XHTML5設定
            if self.w2x_username_edit.text():
                env_content.append(f"WORD2XHTML5_USERNAME={self.w2x_username_edit.text()}")
            if self.w2x_password_edit.text():
                env_content.append(f"WORD2XHTML5_PASSWORD={self.w2x_password_edit.text()}")
                
            # デバッグ設定
            env_content.append(f"DEBUG_MODE={'true' if self.debug_mode_cb.isChecked() else 'false'}")
            env_content.append(f"LOG_LEVEL={self.log_level_combo.currentText()}")
            
            # Google Sheets設定
            if self.sheets_id_edit.text():
                env_content.append(f"GOOGLE_SHEETS_ID={self.sheets_id_edit.text()}")
            if self.sheets_creds_edit.text():
                env_content.append(f"GOOGLE_SHEETS_CREDENTIALS_PATH={self.sheets_creds_edit.text()}")
            
            # .envファイルに保存
            env_path = PathResolver.get_user_dir() / '.env' if PathResolver.is_exe_environment() else Path('.env')
            env_path.write_text('\n'.join(env_content), encoding='utf-8')
            
            # settings.jsonを更新
            config_data = self.config.data.copy()
            
            # Google Sheets設定
            if 'google_sheet' not in config_data:
                config_data['google_sheet'] = {}
            config_data['google_sheet']['sheet_id'] = self.sheets_id_edit.text()
            config_data['google_sheet']['credentials_path'] = self.sheets_creds_edit.text()
            
            # パス設定
            if 'paths' not in config_data:
                config_data['paths'] = {}
            config_data['paths']['git_base'] = self.git_base_edit.text()
            config_data['paths']['output_base'] = self.output_base_edit.text()
            
            # Word2XHTML5/NextPublishing設定をwebセクションに保存
            if 'web' not in config_data:
                config_data['web'] = {}
            if self.w2x_username_edit.text():
                config_data['web']['username'] = self.w2x_username_edit.text()
            if self.w2x_password_edit.text():
                config_data['web']['password'] = self.w2x_password_edit.text()
            
            # 設定を保存
            self.config.save(config_data)
            
            # 環境変数を再読み込み
            EnvManager.initialize(force=True)
            
            self.settings_updated.emit()
            
            QMessageBox.information(
                self,
                "保存完了",
                "設定を保存しました。\n一部の設定は再起動後に有効になります。"
            )
            
            self.accept()
            
        except Exception as e:
            self.logger.error(f"設定保存エラー: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "保存エラー",
                f"設定の保存に失敗しました:\n{str(e)}"
            )
            
    def export_settings(self):
        """設定をエクスポート"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "設定をエクスポート",
            str(Path.home() / "techzip_settings.json"),
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                export_data = {
                    "gmail_address": self.gmail_address_edit.text(),
                    "google_sheets_id": self.sheets_id_edit.text(),
                    "google_sheets_credentials_path": self.sheets_creds_edit.text(),
                    "git_base_path": self.git_base_edit.text(),
                    "output_base_path": self.output_base_edit.text(),
                    "word2xhtml5_username": self.w2x_username_edit.text(),
                    "word2xhtml5_password": self.w2x_password_edit.text(),
                    "debug_mode": self.debug_mode_cb.isChecked(),
                    "log_level": self.log_level_combo.currentText()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(
                    self,
                    "エクスポート完了",
                    f"設定をエクスポートしました:\n{file_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "エクスポートエラー",
                    f"設定のエクスポートに失敗しました:\n{str(e)}"
                )
                
    def import_settings(self):
        """設定をインポート"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "設定をインポート",
            str(Path.home()),
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                    
                # 設定を適用
                if 'gmail_address' in import_data:
                    self.gmail_address_edit.setText(import_data['gmail_address'])
                if 'google_sheets_id' in import_data:
                    self.sheets_id_edit.setText(import_data['google_sheets_id'])
                if 'google_sheets_credentials_path' in import_data:
                    self.sheets_creds_edit.setText(import_data['google_sheets_credentials_path'])
                if 'git_base_path' in import_data:
                    self.git_base_edit.setText(import_data['git_base_path'])
                if 'output_base_path' in import_data:
                    self.output_base_edit.setText(import_data['output_base_path'])
                if 'word2xhtml5_username' in import_data:
                    self.w2x_username_edit.setText(import_data['word2xhtml5_username'])
                if 'word2xhtml5_password' in import_data:
                    self.w2x_password_edit.setText(import_data['word2xhtml5_password'])
                if 'debug_mode' in import_data:
                    self.debug_mode_cb.setChecked(import_data['debug_mode'])
                if 'log_level' in import_data:
                    self.log_level_combo.setCurrentText(import_data['log_level'])
                    
                QMessageBox.information(
                    self,
                    "インポート完了",
                    "設定をインポートしました。\n保存ボタンを押して適用してください。"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "インポートエラー",
                    f"設定のインポートに失敗しました:\n{str(e)}"
                )
                
    def open_settings_folder(self):
        """設定フォルダを開く"""
        import subprocess
        import platform
        
        folder_path = PathResolver.get_config_path()
        
        if platform.system() == 'Windows':
            subprocess.Popen(['explorer', str(folder_path)])
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', str(folder_path)])
        else:  # Linux
            subprocess.Popen(['xdg-open', str(folder_path)])