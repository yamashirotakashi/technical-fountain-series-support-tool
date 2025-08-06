from __future__ import annotations
#!/usr/bin/env python3
"""
TECHZIP設定ダイアログ - ConfigManagerとGUI統合
UI/UXによる設定変更をリアルタイム反映
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QTextEdit,
    QFileDialog, QMessageBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# ConfigManagerをインポート
sys.path.append(str(Path(__file__).parent.parent))
from src.slack_pdf_poster import ConfigManager


class ConfigDialog(QDialog):
    """
    TECHZIP統合設定ダイアログ
    
    機能:
    - ConfigManagerとの双方向連携
    - カテゴリ別タブ表示
    - リアルタイム設定検証
    - 即座適用とプレビュー
    """
    
    # 設定変更シグナル
    config_changed = pyqtSignal(str, object)  # key_path, new_value
    
    def __init__(self, config_manager: Optional[ConfigManager] = None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager or ConfigManager()
        self.widgets = {}  # 設定ウィジェット保存用
        self.setup_ui()
        self.load_current_config()
        
    def setup_ui(self):
        """UIセットアップ"""
        self.setWindowTitle("TECHZIP 設定")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        # メインレイアウト
        layout = QVBoxLayout(self)
        
        # タブウィジェット
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # タブを作成
        self.create_paths_tab()
        self.create_api_tab()
        self.create_processing_tab()
        self.create_security_tab()
        self.create_advanced_tab()
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        # 検証ボタン
        self.validate_button = QPushButton("設定検証")
        self.validate_button.clicked.connect(self.validate_config)
        button_layout.addWidget(self.validate_button)
        
        # リセットボタン
        self.reset_button = QPushButton("デフォルトに戻す")
        self.reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        # 適用・キャンセルボタン
        self.apply_button = QPushButton("適用")
        self.apply_button.clicked.connect(self.apply_changes)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept_changes)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # ステータスエリア
        self.status_label = QLabel("設定準備完了")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)
    
    def create_paths_tab(self):
        """パス設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "パス設定")
        
        scroll = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # ベースパス設定
        base_group = QGroupBox("ベースパス設定")
        base_layout = QFormLayout(base_group)
        
        # リポジトリベースパス
        repo_layout = QHBoxLayout()
        self.widgets['paths.base_repository_path'] = QLineEdit()
        repo_browse_btn = QPushButton("参照...")
        repo_browse_btn.clicked.connect(
            lambda: self.browse_directory('paths.base_repository_path')
        )
        repo_layout.addWidget(self.widgets['paths.base_repository_path'])
        repo_layout.addWidget(repo_browse_btn)
        base_layout.addRow("リポジトリパス:", repo_layout)
        
        # Git ベースパス
        git_layout = QHBoxLayout()
        self.widgets['paths.git_base_path'] = QLineEdit()
        git_browse_btn = QPushButton("参照...")
        git_browse_btn.clicked.connect(
            lambda: self.browse_directory('paths.git_base_path')
        )
        git_layout.addWidget(self.widgets['paths.git_base_path'])
        git_layout.addWidget(git_browse_btn)
        base_layout.addRow("Gitベースパス:", git_layout)
        
        layout.addWidget(base_group)
        
        # 作業ディレクトリ設定
        work_group = QGroupBox("作業ディレクトリ")
        work_layout = QFormLayout(work_group)
        
        # 各作業ディレクトリ
        work_dirs = [
            ('paths.temp_directory', '一時ディレクトリ'),
            ('paths.output_directory', '出力ディレクトリ'),
            ('paths.log_directory', 'ログディレクトリ')
        ]
        
        for key, label in work_dirs:
            dir_layout = QHBoxLayout()
            self.widgets[key] = QLineEdit()
            browse_btn = QPushButton("参照...")
            browse_btn.clicked.connect(lambda checked, k=key: self.browse_directory(k))
            dir_layout.addWidget(self.widgets[key])
            dir_layout.addWidget(browse_btn)
            work_layout.addRow(f"{label}:", dir_layout)
        
        layout.addWidget(work_group)
        
        scroll.setWidget(scroll_widget)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
    
    def create_api_tab(self):
        """API設定タブ - 2列レイアウトで縦の長さを改善"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "API設定")
        
        scroll = QScrollArea()
        scroll_widget = QWidget()
        
        # メインレイアウト - 2列構成
        main_layout = QHBoxLayout(scroll_widget)
        
        # 左列
        left_column = QVBoxLayout()
        
        # NextPublishing API設定 (左列)
        np_group = QGroupBox("NextPublishing API")
        np_layout = QFormLayout(np_group)
        
        # API URL (デフォルト値設定)
        self.widgets['api.nextpublishing.base_url'] = QLineEdit()
        self.widgets['api.nextpublishing.base_url'].setPlaceholderText("http://sd001.nextpublishing.jp/rapture")
        np_layout.addRow("ベースURL:", self.widgets['api.nextpublishing.base_url'])
        
        # 認証情報
        self.widgets['api.nextpublishing.username'] = QLineEdit()
        self.widgets['api.nextpublishing.username'].setPlaceholderText("ユーザー名を入力")
        np_layout.addRow("ユーザー名:", self.widgets['api.nextpublishing.username'])
        
        self.widgets['api.nextpublishing.password'] = QLineEdit()
        self.widgets['api.nextpublishing.password'].setPlaceholderText("パスワードを入力")
        np_layout.addRow("パスワード:", self.widgets['api.nextpublishing.password'])
        
        # タイムアウト設定
        self.widgets['api.nextpublishing.timeout'] = QSpinBox()
        self.widgets['api.nextpublishing.timeout'].setRange(5, 300)
        self.widgets['api.nextpublishing.timeout'].setValue(60)  # デフォルト値
        self.widgets['api.nextpublishing.timeout'].setSuffix(" 秒")
        np_layout.addRow("タイムアウト:", self.widgets['api.nextpublishing.timeout'])
        
        left_column.addWidget(np_group)
        
        # ReVIEW変換API設定 (左列)
        review_group = QGroupBox("ReVIEW変換API")
        review_layout = QFormLayout(review_group)
        
        # Review endpoint
        self.widgets['api.nextpublishing.review_endpoint'] = QLineEdit()
        self.widgets['api.nextpublishing.review_endpoint'].setPlaceholderText("/api/review/convert")
        review_layout.addRow("ReVIEWエンドポイント:", self.widgets['api.nextpublishing.review_endpoint'])
        
        # EPUB endpoint
        self.widgets['api.nextpublishing.epub_endpoint'] = QLineEdit()
        self.widgets['api.nextpublishing.epub_endpoint'].setPlaceholderText("/api/epub/generate")
        review_layout.addRow("EPUBエンドポイント:", self.widgets['api.nextpublishing.epub_endpoint'])
        
        # GCF endpoint
        self.widgets['api.nextpublishing.gcf_endpoint'] = QLineEdit()
        self.widgets['api.nextpublishing.gcf_endpoint'].setPlaceholderText("/api/gcf/process")
        review_layout.addRow("GCFエンドポイント:", self.widgets['api.nextpublishing.gcf_endpoint'])
        
        left_column.addWidget(review_group)
        
        # GitHub API設定 (左列)
        github_group = QGroupBox("GitHub API")
        github_layout = QFormLayout(github_group)
        
        # GitHub Token
        self.widgets['api.github.token'] = QLineEdit()
        self.widgets['api.github.token'].setPlaceholderText("環境変数 GITHUB_TOKEN から取得")
        github_layout.addRow("GitHub Token:", self.widgets['api.github.token'])
        
        # API Base URL
        self.widgets['api.github.api_base_url'] = QLineEdit()
        self.widgets['api.github.api_base_url'].setPlaceholderText("https://api.github.com")
        github_layout.addRow("GitHub API URL:", self.widgets['api.github.api_base_url'])
        
        # Default User
        self.widgets['api.github.default_user'] = QLineEdit()
        self.widgets['api.github.default_user'].setPlaceholderText("GitHubユーザー名")
        github_layout.addRow("デフォルトユーザー:", self.widgets['api.github.default_user'])
        
        left_column.addWidget(github_group)
        
        # 右列
        right_column = QVBoxLayout()
        
        # Gmail API設定 (右列)
        gmail_group = QGroupBox("Gmail API")
        gmail_layout = QFormLayout(gmail_group)
        
        # デフォルトアドレス
        self.widgets['api.gmail.default_address'] = QLineEdit()
        self.widgets['api.gmail.default_address'].setPlaceholderText("yamashiro.takashi@gmail.com")
        gmail_layout.addRow("デフォルトアドレス:", self.widgets['api.gmail.default_address'])
        
        # アプリパスワード
        self.widgets['email.app_password'] = QLineEdit()
        self.widgets['email.app_password'].setPlaceholderText("環境変数 GMAIL_APP_PASSWORD から取得")
        gmail_layout.addRow("Gmailアプリパスワード:", self.widgets['email.app_password'])
        
        # Gmail認証アドレス
        self.widgets['email.address'] = QLineEdit()
        self.widgets['email.address'].setPlaceholderText("Gmail認証用アドレス")
        gmail_layout.addRow("Gmail認証アドレス:", self.widgets['email.address'])
        
        right_column.addWidget(gmail_group)
        
        # Slack API設定 (右列)
        slack_group = QGroupBox("Slack API")
        slack_layout = QFormLayout(slack_group)
        
        # Bot Token
        self.widgets['api.slack.bot_token'] = QLineEdit()
        self.widgets['api.slack.bot_token'].setPlaceholderText("環境変数 SLACK_BOT_TOKEN から取得")
        slack_layout.addRow("Bot Token:", self.widgets['api.slack.bot_token'])
        
        # API URL
        self.widgets['api.slack.api_base_url'] = QLineEdit()
        self.widgets['api.slack.api_base_url'].setPlaceholderText("https://slack.com/api/")
        slack_layout.addRow("API URL:", self.widgets['api.slack.api_base_url'])
        
        # Rate Limit
        self.widgets['api.slack.rate_limit_delay'] = QDoubleSpinBox()
        self.widgets['api.slack.rate_limit_delay'].setRange(0.1, 10.0)
        self.widgets['api.slack.rate_limit_delay'].setValue(1.0)  # デフォルト値
        self.widgets['api.slack.rate_limit_delay'].setSingleStep(0.1)
        self.widgets['api.slack.rate_limit_delay'].setSuffix(" 秒")
        slack_layout.addRow("Rate制限間隔:", self.widgets['api.slack.rate_limit_delay'])
        
        right_column.addWidget(slack_group)
        
        # Google Cloud API設定 (右列)
        gcloud_group = QGroupBox("Google Cloud API")
        gcloud_layout = QFormLayout(gcloud_group)
        
        # Console URL
        self.widgets['api.google_cloud.console_url'] = QLineEdit()
        self.widgets['api.google_cloud.console_url'].setPlaceholderText("https://console.cloud.google.com/")
        gcloud_layout.addRow("コンソールURL:", self.widgets['api.google_cloud.console_url'])
        
        # Sheets Scope
        self.widgets['api.google_cloud.sheets_scope'] = QLineEdit()
        self.widgets['api.google_cloud.sheets_scope'].setPlaceholderText("https://www.googleapis.com/auth/spreadsheets.readonly")
        gcloud_layout.addRow("Sheetsスコープ:", self.widgets['api.google_cloud.sheets_scope'])
        
        right_column.addWidget(gcloud_group)
        
        # 列に追加
        main_layout.addLayout(left_column)
        main_layout.addLayout(right_column)
        
        # 等幅に設定
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)
        
        scroll.setWidget(scroll_widget)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
    
    def create_processing_tab(self):
        """処理設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "処理設定")
        
        scroll = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # バッチ処理設定
        batch_group = QGroupBox("バッチ処理")
        batch_layout = QFormLayout(batch_group)
        
        # バッチサイズ
        self.widgets['processing.batch_size'] = QSpinBox()
        self.widgets['processing.batch_size'].setRange(1, 100)
        batch_layout.addRow("バッチサイズ:", self.widgets['processing.batch_size'])
        
        # 同時実行数
        self.widgets['processing.max_concurrent'] = QSpinBox()
        self.widgets['processing.max_concurrent'].setRange(1, 10)
        batch_layout.addRow("最大同時実行:", self.widgets['processing.max_concurrent'])
        
        # 間隔設定
        self.widgets['processing.delay_between_batches'] = QDoubleSpinBox()
        self.widgets['processing.delay_between_batches'].setRange(0.1, 60.0)
        self.widgets['processing.delay_between_batches'].setSuffix(" 秒")
        batch_layout.addRow("バッチ間隔:", self.widgets['processing.delay_between_batches'])
        
        # 自動クリーンアップ
        self.widgets['processing.auto_cleanup'] = QCheckBox("有効")
        batch_layout.addRow("自動クリーンアップ:", self.widgets['processing.auto_cleanup'])
        
        layout.addWidget(batch_group)
        
        # メール監視設定
        email_group = QGroupBox("メール監視")
        email_layout = QFormLayout(email_group)
        
        # チェック間隔
        self.widgets['processing.email_check_interval'] = QSpinBox()
        self.widgets['processing.email_check_interval'].setRange(10, 600)
        self.widgets['processing.email_check_interval'].setSuffix(" 秒")
        email_layout.addRow("チェック間隔:", self.widgets['processing.email_check_interval'])
        
        # タイムアウト
        self.widgets['processing.email_check_timeout'] = QSpinBox()
        self.widgets['processing.email_check_timeout'].setRange(60, 3600)
        self.widgets['processing.email_check_timeout'].setSuffix(" 秒")
        email_layout.addRow("監視タイムアウト:", self.widgets['processing.email_check_timeout'])
        
        layout.addWidget(email_group)
        
        scroll.setWidget(scroll_widget)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
    
    def create_security_tab(self):
        """セキュリティ設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "セキュリティ")
        
        layout = QVBoxLayout(tab)
        
        # ハードコーディング検知設定
        hc_group = QGroupBox("ハードコーディング検知")
        hc_layout = QFormLayout(hc_group)
        
        # 検知有効化
        self.widgets['security.enable_hardcoding_detection'] = QCheckBox("有効")
        hc_layout.addRow("ハードコーディング検知:", self.widgets['security.enable_hardcoding_detection'])
        
        # 起動時スキャン
        self.widgets['security.hardcoding_scan_on_startup'] = QCheckBox("有効")
        hc_layout.addRow("起動時スキャン:", self.widgets['security.hardcoding_scan_on_startup'])
        
        layout.addWidget(hc_group)
        
        # 設定検証
        validation_group = QGroupBox("設定検証")
        validation_layout = QFormLayout(validation_group)
        
        # 起動時検証
        self.widgets['security.validate_config_on_startup'] = QCheckBox("有効")
        validation_layout.addRow("起動時検証:", self.widgets['security.validate_config_on_startup'])
        
        # 環境変数必須チェック
        self.widgets['security.require_env_vars'] = QCheckBox("有効")
        validation_layout.addRow("環境変数必須:", self.widgets['security.require_env_vars'])
        
        layout.addWidget(validation_group)
    
    def create_advanced_tab(self):
        """高度設定タブ"""
        tab = QWidget()
        self.tab_widget.addTab(tab, "高度設定")
        
        scroll = QScrollArea()
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        
        # ログ設定
        log_group = QGroupBox("ログ設定")
        log_layout = QFormLayout(log_group)
        
        # ログレベル
        self.widgets['logging.level'] = QComboBox()
        self.widgets['logging.level'].addItems(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        log_layout.addRow("ログレベル:", self.widgets['logging.level'])
        
        # ローテーション
        self.widgets['logging.file_rotation'] = QComboBox()
        self.widgets['logging.file_rotation'].addItems(['daily', 'weekly', 'monthly'])
        log_layout.addRow("ファイルローテーション:", self.widgets['logging.file_rotation'])
        
        # 保持期間
        self.widgets['logging.retention_days'] = QSpinBox()
        self.widgets['logging.retention_days'].setRange(1, 365)
        self.widgets['logging.retention_days'].setSuffix(" 日")
        log_layout.addRow("保持期間:", self.widgets['logging.retention_days'])
        
        layout.addWidget(log_group)
        
        # 機能フラグ
        features_group = QGroupBox("機能フラグ")
        features_layout = QFormLayout(features_group)
        
        feature_flags = [
            ('features.enable_slack_integration', 'Slack統合'),
            ('features.enable_github_integration', 'GitHub統合'),
            ('features.enable_email_monitoring', 'メール監視'),
            ('features.enable_batch_processing', 'バッチ処理'),
            ('features.debug_mode', 'デバッグモード')
        ]
        
        for key, label in feature_flags:
            self.widgets[key] = QCheckBox("有効")
            features_layout.addRow(f"{label}:", self.widgets[key])
        
        layout.addWidget(features_group)
        
        scroll.setWidget(scroll_widget)
        tab_layout = QVBoxLayout(tab)
        tab_layout.addWidget(scroll)
    
    def browse_directory(self, config_key: str):
        """ディレクトリ参照ダイアログ"""
        current_path = self.widgets[config_key].text()
        directory = QFileDialog.getExistingDirectory(
            self, f"ディレクトリを選択 - {config_key}", current_path
        )
        if directory:
            self.widgets[config_key].setText(directory)
            self.config_changed.emit(config_key, directory)
    
    def load_current_config(self):
        """現在の設定を読み込み - デフォルト値の適用を改善"""
        # API設定のデフォルト値マッピング
        api_defaults = {
            'api.nextpublishing.base_url': 'http://sd001.nextpublishing.jp/rapture',
            'api.nextpublishing.timeout': 60,
            'api.nextpublishing.review_endpoint': '/api/review/convert',
            'api.nextpublishing.epub_endpoint': '/api/epub/generate', 
            'api.nextpublishing.gcf_endpoint': '/api/gcf/process',
            'api.github.api_base_url': 'https://api.github.com',
            'api.gmail.default_address': 'yamashiro.takashi@gmail.com',
            'api.slack.api_base_url': 'https://slack.com/api/',
            'api.slack.rate_limit_delay': 1.0,
            'api.google_cloud.console_url': 'https://console.cloud.google.com/',
            'api.google_cloud.sheets_scope': 'https://www.googleapis.com/auth/spreadsheets.readonly'
        }
        
        for key, widget in self.widgets.items():
            value = self.config_manager.get(key)
            
            # 値がNoneまたは空の場合、デフォルト値を使用
            if value is None or (isinstance(value, str) and value.strip() == ""):
                value = api_defaults.get(key)
            
            if isinstance(widget, QLineEdit):
                widget.setText(str(value) if value is not None else "")
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value) if value is not None else 0)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(value) if value is not None else 0.0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value) if value is not None else False)
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(value) if value is not None else "")
                if index >= 0:
                    widget.setCurrentIndex(index)
    
    def validate_config(self):
        """設定検証"""
        # 現在のウィジェット値でConfigManagerを更新
        temp_config = {}
        for key, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                temp_config[key] = widget.text()
            elif isinstance(widget, QSpinBox):
                temp_config[key] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                temp_config[key] = widget.value()
            elif isinstance(widget, QCheckBox):
                temp_config[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                temp_config[key] = widget.currentText()
        
        # 検証実行
        validation_result = self.config_manager.validate_config()
        
        # 結果表示
        errors = validation_result.get('errors', [])
        warnings = validation_result.get('warnings', [])
        missing_vars = validation_result.get('missing_env_vars', [])
        
        if not errors and not warnings and not missing_vars:
            self.status_label.setText("✅ 設定検証完了 - 問題なし")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            QMessageBox.information(self, "検証完了", "設定に問題はありません。")
        else:
            message_parts = []
            if errors:
                message_parts.append(f"❌ エラー: {len(errors)}件")
                message_parts.extend([f"  • {error}" for error in errors])
            if warnings:
                message_parts.append(f"⚠️ 警告: {len(warnings)}件")
                message_parts.extend([f"  • {warning}" for warning in warnings])
            if missing_vars:
                message_parts.append(f"🔍 不足環境変数: {len(missing_vars)}件")
                message_parts.extend([f"  • {var}" for var in missing_vars])
            
            message = "\\n".join(message_parts)
            self.status_label.setText(f"❌ 設定に問題があります ({len(errors)}エラー)")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.warning(self, "検証結果", message)
    
    def reset_to_defaults(self):
        """デフォルト設定に戻す"""
        reply = QMessageBox.question(
            self, "確認", 
            "すべての設定をデフォルト値に戻しますか？\\n(変更は適用後に確定されます)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # デフォルト設定で初期化
            self.config_manager._config_cache = self.config_manager._create_default_config()
            self.load_current_config()
            self.status_label.setText("🔄 デフォルト設定に戻しました")
            self.status_label.setStyleSheet("color: blue; font-weight: bold;")
    
    def apply_changes(self):
        """変更を適用"""
        try:
            # 各ウィジェットの値をConfigManagerに設定
            for key, widget in self.widgets.items():
                if isinstance(widget, QLineEdit):
                    value = widget.text()
                elif isinstance(widget, QSpinBox):
                    value = widget.value()
                elif isinstance(widget, QDoubleSpinBox):
                    value = widget.value()
                elif isinstance(widget, QCheckBox):
                    value = widget.isChecked()
                elif isinstance(widget, QComboBox):
                    value = widget.currentText()
                else:
                    continue
                
                self.config_manager.set(key, value)
                self.config_changed.emit(key, value)
            
            self.status_label.setText("✅ 設定を適用しました")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            QMessageBox.information(self, "適用完了", "設定が正常に適用されました。")
            
        except Exception as e:
            self.status_label.setText(f"❌ 適用エラー: {str(e)}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "エラー", f"設定の適用に失敗しました:\\n{str(e)}")
    
    def accept_changes(self):
        """変更を適用して閉じる"""
        self.apply_changes()
        self.accept()


def main():
    """デモ用メイン関数"""
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # ConfigManagerを初期化
    config_manager = ConfigManager()
    
    # 設定ダイアログを表示
    dialog = ConfigDialog(config_manager)
    
    # 設定変更シグナルをテスト
    def on_config_changed(key, value):
        print(f"設定変更: {key} = {value}")
    
    dialog.config_changed.connect(on_config_changed)
    
    result = dialog.exec()
    print(f"ダイアログ結果: {'OK' if result == QDialog.DialogCode.Accepted else 'Cancel'}")


if __name__ == "__main__":
    main()