"""
プロジェクト初期化ツール - メインウィンドウ
Qt6ベースのGUI実装
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QGridLayout,
    QCheckBox, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTabWidget, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction

# Unicode安全出力関数
def safe_print(text: str):
    """Unicode文字を安全に出力"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Unicode文字を安全な文字に置き換え
        safe_text = text.replace("✅", "[OK]").replace("✗", "[ERROR]").replace("⚠️", "[WARN]")
        print(safe_text.encode('ascii', 'ignore').decode('ascii'))

# Qt6 + asyncio統合ライブラリ
try:
    from asyncqt import QEventLoop
    safe_print("✅ asyncqt使用")
except ImportError:
    try:
        import qasync
        from qasync import QEventLoop
        safe_print("✅ qasync使用（Qt6対応）")
    except ImportError:
        from asyncqt_fixed import QEventLoop
        safe_print("⚠️ 代替実装使用")


# 自作モジュール
from google_sheets import GoogleSheetsClient
from slack_client import SlackClient
from github_client import GitHubClient
from path_resolver import get_config_path


class WorkerThread(QThread):
    """非同期処理用のワーカースレッド"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, task_type: str, params: Dict[str, Any]):
        super().__init__()
        self.task_type = task_type
        self.params = params
    
    def run(self):
        """タスクを実行"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if self.task_type == "initialize_project":
                result = loop.run_until_complete(self._initialize_project())
            elif self.task_type == "check_project":
                result = loop.run_until_complete(self._check_project_info())
            else:
                raise ValueError(f"Unknown task type: {self.task_type}")
                
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            loop.close()
    
    async def _check_project_info(self):
        """プロジェクト情報を確認"""
        self.progress.emit("Google Sheetsから情報を取得中...")
        
        # Google Sheets クライアント初期化
        service_account_path = get_config_path("service_account.json")
        sheets_client = GoogleSheetsClient(str(service_account_path))
        
        # プロジェクト情報取得
        project_info = await sheets_client.get_project_info(
            self.params["planning_sheet_id"],
            self.params["n_code"]
        )
        
        if not project_info:
            raise ValueError(f"Nコード {self.params['n_code']} が見つかりません")
        
        # 購入リストから書籍URL取得
        self.progress.emit("購入リストから書籍URLを検索中...")
        book_url = await sheets_client.get_book_url_from_purchase_list(
            self.params["purchase_sheet_id"],
            self.params["n_code"]
        )
        
        project_info["book_url_from_purchase"] = book_url
        
        return project_info
    
    async def _initialize_project(self):
        """プロジェクト初期化を実行"""
        result = {
            "slack_channel": None,
            "github_repo": None,
            "manual_tasks": []
        }
        
        # 1. プロジェクト情報取得
        project_info = await self._check_project_info()
        result["project_info"] = project_info
        
        # 2. Slackチャンネル作成
        if self.params.get("create_slack_channel"):
            self.progress.emit("Slackチャンネルを作成中...")
            
            slack_client = SlackClient(
                self.params["slack_token"],
                self.params.get("slack_user_token", os.getenv("SLACK_USER_TOKEN"))
            )
            # チャンネル名はリポジトリ名と同じにする
            channel_name = project_info["repository_name"]
            book_title = project_info.get("book_title")
            
            # チャンネル作成（書籍名をトピックに設定）
            channel_id = await slack_client.create_channel(channel_name, book_title)
            if channel_id:
                result["slack_channel"] = {
                    "id": channel_id,
                    "name": channel_name
                }
                
                # チャンネル作成後の安定化待機（時間を延長）
                await asyncio.sleep(3.0)
                
                # デフォルトメンバー招待（User Token使用）
                self.progress.emit("山城敬を招待中...")
                invite_success = await slack_client.invite_user_to_channel(
                    channel_id,
                    "U7V83BLLB",  # 山城敬
                    use_user_token=True  # プライベートチャンネルのためUser Token使用
                )
                if not invite_success:
                    self.progress.emit("[WARN] 山城敬の招待に失敗しました")
                
                # Bot招待（User Token使用）
                self.progress.emit("TechZip PDF Botを招待中...")
                bot_invite_success = await slack_client.invite_user_to_channel(
                    channel_id,
                    slack_client.TECHZIP_PDF_BOT_ID,
                    use_user_token=True  # プライベートチャンネルのためUser Token使用
                )
                if not bot_invite_success:
                    self.progress.emit("[WARN] TechZip PDF Botの招待に失敗しました")
                
                # GitHub App招待（複数の方法を試行）
                self.progress.emit("GitHub Appを招待中... (Bot Token優先)")
                github_app_invite_success = False
                
                # 方法1: Bot Token（現在のTechZip Bot）での招待を試行（ChatGPT推奨方式）
                try:
                    github_app_invite_success = await slack_client.invite_github_app_with_bot_token(
                        channel_id
                    )
                    if github_app_invite_success:
                        self.progress.emit("✅ GitHub App招待完了 (Bot Token)")
                except Exception as e:
                    self.progress.emit(f"Bot Token招待失敗: {str(e)[:50]}...")
                
                # 方法2: Bot Token失敗時、User Tokenでの招待を試行
                if not github_app_invite_success:
                    self.progress.emit("User Token招待を試行中...")
                    try:
                        github_app_invite_success = await slack_client.invite_user_to_channel(
                            channel_id,
                            slack_client.GITHUB_APP_ID,
                            use_user_token=True
                        )
                        if github_app_invite_success:
                            self.progress.emit("✅ GitHub App招待完了 (User Token)")
                    except Exception as e:
                        self.progress.emit(f"User Token招待失敗: {str(e)[:50]}...")
                
                # 方法3: 両方失敗時、別Botでの招待を試行
                if not github_app_invite_success:
                    self.progress.emit("代替Bot招待を試行中...")
                    try:
                        github_app_invite_success = await slack_client.invite_github_app_with_alternative_bot(
                            channel_id
                        )
                        if github_app_invite_success:
                            self.progress.emit("✅ GitHub App招待完了 (代替Bot)")
                        else:
                            self.progress.emit("[WARN] 全ての招待方法が失敗")
                    except Exception as e:
                        self.progress.emit(f"代替Bot招待エラー: {str(e)[:30]}...")
                
                # 最終結果とGitHub App手動タスクの追加
                if not github_app_invite_success:
                    self.progress.emit("[WARN] GitHub App招待失敗 - 手動設定が必要です")
                    # 手動タスクに追加
                    result["manual_tasks"].append({
                        "type": "github_app_invitation",
                        "repository_name": project_info["repository_name"],
                        "channel_name": channel_name,
                        "description": f"GitHub Appを#{channel_name}に設定してください"
                    })
                
                # 著者の招待処理（エラーハンドリング付き）
                if project_info.get("slack_user_id"):
                    # 既存ユーザー
                    self.progress.emit("著者を招待中...")
                    author_invite_success = await slack_client.invite_user_to_channel(
                        channel_id,
                        project_info["slack_user_id"],
                        use_user_token=True  # プライベートチャンネルのためUser Token使用
                    )
                    if not author_invite_success:
                        self.progress.emit("[WARN] 著者の招待に失敗しました")
                        # 手動タスクとして記録
                        result["manual_tasks"].append({
                            "type": "slack_invitation",
                            "user_id": project_info["slack_user_id"],
                            "email": project_info.get("author_email", "不明"),
                            "description": f"著者 {project_info.get('author_email', project_info['slack_user_id'])} をSlackチャンネルに招待してください"
                        })
                elif project_info.get("author_email"):
                    # メールで検索
                    self.progress.emit("著者をメールで検索中...")
                    user_id = await slack_client.find_user_by_email(
                        project_info["author_email"]
                    )
                    if user_id:
                        self.progress.emit("著者を招待中...")
                        author_invite_success = await slack_client.invite_user_to_channel(
                            channel_id, 
                            user_id,
                            use_user_token=True  # プライベートチャンネルのためUser Token使用
                        )
                        if not author_invite_success:
                            self.progress.emit("[WARN] 著者の招待に失敗しました")
                            # 手動タスクとして記録
                            result["manual_tasks"].append({
                                "type": "slack_invitation",
                                "user_id": user_id,
                                "email": project_info["author_email"],
                                "description": f"著者 {project_info['author_email']} をSlackチャンネルに招待してください"
                            })
                    else:
                        # 手動タスク作成
                        self.progress.emit("著者が見つからないため手動タスクを作成...")
                        result["manual_tasks"].append({
                            "type": "slack_invitation",
                            "email": project_info["author_email"],
                            "description": f"著者 {project_info['author_email']} をSlackワークスペースに招待してください"
                        })
        
        # 3. GitHubリポジトリ作成
        if self.params.get("create_github_repo"):
            self.progress.emit("GitHubリポジトリを作成中...")
            self.progress.emit("yamashirotakashi（編集者）とコラボレーター設定も実行...")
            
            github_client = GitHubClient(self.params["github_token"])
            
            # 書籍名をdescriptionに設定（書籍名がある場合は書籍名のみ）
            book_title = project_info.get("book_title")
            if book_title and book_title != "技術の泉シリーズ":
                description = book_title  # 書籍名のみ
            else:
                description = f"{self.params['n_code']} - 技術の泉シリーズ"
            
            repo_info = await github_client.setup_repository(
                n_code=self.params["n_code"],
                repo_name=project_info["repository_name"],
                github_username=project_info.get("github_account"),
                description=description,
                book_title=book_title
            )
            
            if repo_info:
                result["github_repo"] = repo_info
                
                # GitHubリポジトリ招待失敗の場合は手動タスクに追加
                if repo_info.get("invitation_failed"):
                    result["manual_tasks"].append({
                        "type": "github_invitation",
                        "github_username": repo_info.get("failed_github_username", "不明"),
                        "repository_url": repo_info.get("html_url", "不明"),
                        "description": f"GitHub {repo_info.get('failed_github_username', '不明')} をリポジトリに招待してください"
                    })
        
        # 4. Google Sheets更新
        if self.params.get("update_sheets"):
            self.progress.emit("Google Sheetsを更新中...")
            
            # 書籍URLの転記
            if project_info.get("book_url_from_purchase"):
                service_account_path = get_config_path("service_account.json")
                sheets_client = GoogleSheetsClient(str(service_account_path))
                await sheets_client.update_book_url(
                    self.params["planning_sheet_id"],
                    self.params["n_code"],
                    project_info["book_url_from_purchase"]
                )
        
        # 5. ワークフロー管理統合（全実行結果を投稿）
        self.progress.emit("ワークフロー管理システムを統合中...")
        
        slack_client = SlackClient(
            self.params["slack_token"],
            self.params.get("slack_user_token", os.getenv("SLACK_USER_TOKEN"))
        )
        
        # ワークフロー管理チャンネルを検索（常に管理チャンネルIDが返される）
        workflow_channel_id = await slack_client.find_workflow_channel()
        
        # ワークフローガイダンスを投稿（全ての実行結果）
        await slack_client.post_workflow_guidance(
            workflow_channel_id,
            project_info,
            result.get("manual_tasks", []),
            execution_summary=result,  # 全実行結果を含める
            sheet_id=self.params["planning_sheet_id"]  # 発行計画シートID
        )
        
        # 手動タスク管理シートに記録を追加
        if self.params.get("update_sheets"):
            service_account_path = get_config_path("service_account.json")
            sheets_client = GoogleSheetsClient(str(service_account_path))
            
            status = "手動タスクあり" if result.get("manual_tasks") else "初期化完了"
            additional_info = {
                "slack_channel": result.get("slack_channel", {}).get("name", "未作成"),
                "github_repo": result.get("github_repo", {}).get("html_url", "未作成"),
                "manual_tasks_count": len(result.get("manual_tasks", []))
            }
            
            # 手動タスク管理シートに記録を追加
            try:
                await sheets_client.add_manual_task_record(
                    self.params["planning_sheet_id"],
                    self.params["n_code"],
                    status,
                    additional_info
                )
                self.progress.emit("手動タスク管理シートに記録を追加しました")
                result["workflow_posted"] = True
            except Exception as e:
                self.progress.emit(f"[WARN] 手動タスク管理シート更新に失敗: {str(e)}")
                result["workflow_posted"] = False
        else:
            # Google Sheets更新が無効でも管理チャンネルには投稿済み
            result["workflow_posted"] = True
        
        self.progress.emit("完了！")
        return result


class ProjectInitializerWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """UIを初期化"""
        self.setWindowTitle("技術の泉シリーズプロジェクト初期化ツール")
        self.setGeometry(100, 100, 1000, 700)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # レイアウト
        layout = QVBoxLayout(main_widget)
        
        # タブウィジェット
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 初期化タブ
        init_tab = self._create_init_tab()
        tabs.addTab(init_tab, "プロジェクト初期化")
        
        # 設定タブ
        settings_tab = self._create_settings_tab()
        tabs.addTab(settings_tab, "設定")
        
        # ステータスバー
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # メニューバー
        self._create_menu_bar()
    
    def _create_init_tab(self):
        """初期化タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Nコード入力
        input_group = QGroupBox("プロジェクト情報")
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("Nコード:"), 0, 0)
        self.n_code_input = QLineEdit()
        self.n_code_input.setPlaceholderText("例: N09999")
        input_layout.addWidget(self.n_code_input, 0, 1)
        
        self.check_button = QPushButton("情報確認")
        self.check_button.clicked.connect(self.check_project_info)
        input_layout.addWidget(self.check_button, 0, 2)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # プロジェクト情報表示
        info_group = QGroupBox("確認結果")
        info_layout = QGridLayout()
        
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMinimumHeight(200)
        self.info_display.setMaximumHeight(300)
        info_layout.addWidget(self.info_display, 0, 0, 1, 2)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 実行オプション
        options_group = QGroupBox("実行オプション")
        options_layout = QVBoxLayout()
        
        self.create_slack_cb = QCheckBox("Slackチャンネルを作成")
        self.create_slack_cb.setChecked(True)
        options_layout.addWidget(self.create_slack_cb)
        
        self.create_github_cb = QCheckBox("GitHubリポジトリを作成")
        self.create_github_cb.setChecked(True)
        options_layout.addWidget(self.create_github_cb)
        
        self.update_sheets_cb = QCheckBox("Google Sheetsを更新")
        self.update_sheets_cb.setChecked(True)
        options_layout.addWidget(self.update_sheets_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 実行ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.execute_button = QPushButton("プロジェクト初期化実行")
        self.execute_button.clicked.connect(self.execute_initialization)
        self.execute_button.setEnabled(False)
        button_layout.addWidget(self.execute_button)
        
        layout.addLayout(button_layout)
        
        # ログ表示
        log_group = QGroupBox("実行ログ")
        log_layout = QVBoxLayout()
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        log_layout.addWidget(self.log_display)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        return widget
    
    def _create_settings_tab(self):
        """設定タブを作成"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API設定
        api_group = QGroupBox("API設定")
        api_layout = QGridLayout()
        
        # Slack Token
        api_layout.addWidget(QLabel("Slack Bot Token:"), 0, 0)
        self.slack_token_input = QLineEdit()
        self.slack_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(self.slack_token_input, 0, 1)
        
        # GitHub Token
        api_layout.addWidget(QLabel("GitHub Token:"), 1, 0)
        self.github_token_input = QLineEdit()
        self.github_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addWidget(self.github_token_input, 1, 1)
        
        # Google Sheets ID
        api_layout.addWidget(QLabel("発行計画シートID:"), 2, 0)
        self.planning_sheet_input = QLineEdit()
        api_layout.addWidget(self.planning_sheet_input, 2, 1)
        
        api_layout.addWidget(QLabel("購入リストシートID:"), 3, 0)
        self.purchase_sheet_input = QLineEdit()
        api_layout.addWidget(self.purchase_sheet_input, 3, 1)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 保存ボタン
        save_button = QPushButton("設定を保存")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        layout.addStretch()
        
        return widget
    
    def _create_menu_bar(self):
        """メニューバーを作成"""
        menubar = self.menuBar()
        
        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル")
        
        exit_action = QAction("終了", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ")
        
        about_action = QAction("このツールについて", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_settings(self):
        """設定を読み込み"""
        # 環境変数から読み込み
        self.slack_token_input.setText(os.getenv("SLACK_BOT_TOKEN", ""))
        self.github_token_input.setText(os.getenv("GITHUB_ORG_TOKEN", ""))
        self.planning_sheet_input.setText("17DKsMGQ6krbhY7GIcX0iaeN-y8HcGGVkXt3d4oOckyQ")
        self.purchase_sheet_input.setText("1JJ_C3z0txlJWiyEDl0c6OoVD5Ym_IoZJMMf5o76oV4c")
    
    def save_settings(self):
        """設定を保存"""
        QMessageBox.information(self, "設定保存", "設定を保存しました")
    
    def check_project_info(self):
        """プロジェクト情報を確認"""
        n_code = self.n_code_input.text().strip()
        if not n_code:
            QMessageBox.warning(self, "エラー", "Nコードを入力してください")
            return
        
        # ワーカースレッドで実行
        params = {
            "n_code": n_code,
            "planning_sheet_id": self.planning_sheet_input.text(),
            "purchase_sheet_id": self.purchase_sheet_input.text()
        }
        
        self.worker = WorkerThread("check_project", params)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_check_finished)
        self.worker.error.connect(self.on_error)
        
        self.check_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.worker.start()
    
    def on_check_finished(self, result):
        """情報確認完了"""
        self.check_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 情報を表示（書籍名を最初に表示）
        book_title = result.get('book_title', 'なし')
        info_text = f"""
【書籍名】: {book_title}
Nコード: {result['n_code']}
リポジトリ名: {result['repository_name']}

【著者情報】
著者メール: {result.get('author_email', 'なし')}
GitHub: {result.get('github_account', 'なし')}
Slack ID: {result.get('slack_user_id', 'なし')}

【その他】
書籍URL（購入リスト）: {result.get('book_url_from_purchase', 'なし')}
"""
        self.info_display.setText(info_text)
        self.execute_button.setEnabled(True)
        
        # 結果を保存
        self.current_project_info = result
    
    def execute_initialization(self):
        """プロジェクト初期化を実行"""
        reply = QMessageBox.question(
            self, 
            "確認", 
            "プロジェクト初期化を実行しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # パラメータ準備
        params = {
            "n_code": self.n_code_input.text(),
            "planning_sheet_id": self.planning_sheet_input.text(),
            "purchase_sheet_id": self.purchase_sheet_input.text(),
            "slack_token": self.slack_token_input.text(),
            "github_token": self.github_token_input.text(),
            "create_slack_channel": self.create_slack_cb.isChecked(),
            "create_github_repo": self.create_github_cb.isChecked(),
            "update_sheets": self.update_sheets_cb.isChecked()
        }
        
        self.worker = WorkerThread("initialize_project", params)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_init_finished)
        self.worker.error.connect(self.on_error)
        
        self.execute_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.log_display.clear()
        self.worker.start()
    
    def on_init_finished(self, result):
        """初期化完了"""
        self.execute_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 結果をログに表示
        log_text = "=== プロジェクト初期化完了 ===\n\n"
        
        if result.get("slack_channel"):
            book_title = result.get('book_title', 'なし')
            log_text += f"✓ Slackチャンネル作成: #{result['slack_channel']['name']}\n"
            if book_title != 'なし':
                log_text += f"  - トピック: {book_title}\n"
            log_text += f"  - 説明: 入稿メモURL設定済み\n"
            log_text += f"  - 招待メンバー: 山城敬、TechZip PDF Bot、GitHub App、著者\n"
        
        if result.get("github_repo"):
            log_text += f"✓ GitHubリポジトリ作成: {result['github_repo']['html_url']}\n"
            log_text += f"  - yamashirotakashi（編集者）をadmin権限でコラボレーター追加\n"
            if result['github_repo'].get('invitation_failed'):
                log_text += f"  - 著者のコラボレーター追加は手動タスクに登録\n"
            else:
                log_text += f"  - 著者もコラボレーターとして追加済み\n"
        
        if result.get("manual_tasks"):
            log_text += "\n🔴 手動タスク:\n"
            for task in result["manual_tasks"]:
                if task["type"] == "slack_invitation":
                    if "user_id" in task:
                        log_text += f"- 【重要】{task['email']} (ID: {task['user_id']}) をSlackチャンネルに招待してください\n"
                    else:
                        log_text += f"- 【重要】{task['email']} をSlackワークスペースに招待してください（新規ユーザー）\n"
                elif task["type"] == "github_invitation":
                    log_text += f"- 【重要】GitHub {task['github_username']} をリポジトリに招待してください\n"
                elif task["type"] == "github_app_invitation":
                    channel_name = task.get("channel_name", "チャンネル")
                    repo_name = task.get("repository_name", "リポジトリ")
                    log_text += f"- 【重要】GitHub App設定:\n"
                    log_text += f"  1. 著者のGitHub招待メールを確認・承認\n"
                    log_text += f"  2. #{channel_name} で `/invite @GitHub` を実行\n"
                    log_text += f"  3. #{channel_name} で `/github subscribe {repo_name}` を実行\n"
        
        # ワークフロー管理システム統合結果
        if result.get("workflow_posted"):
            log_text += "\n✓ ワークフロー管理システム統合完了\n"
            log_text += "  - 全実行結果を管理チャンネル（-管理channel）に投稿\n"
            if self.update_sheets_cb.isChecked():
                log_text += "  - 手動タスク管理シートに記録を追加\n"
        elif result.get("workflow_posted") is False:
            log_text += "\n[WARN] 手動タスク管理シート更新に失敗\n"
            log_text += "  - 管理チャンネルへの実行結果投稿は完了済み\n"
        
        self.log_display.append(log_text)
        
        QMessageBox.information(self, "完了", "プロジェクト初期化が完了しました")
    
    def update_progress(self, message):
        """進捗を更新"""
        self.status_bar.showMessage(message)
        self.log_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def on_error(self, error_message):
        """エラー処理"""
        self.check_button.setEnabled(True)
        self.execute_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.log_display.append(f"\n[ERROR] エラー: {error_message}")
        QMessageBox.critical(self, "エラー", error_message)
    
    def show_about(self):
        """アプリケーション情報を表示"""
        QMessageBox.about(
            self,
            "プロジェクト初期化ツールについて",
            "技術の泉シリーズ プロジェクト初期化ツール\n\n"
            "Version 1.0.0\n"
            "© 2025 TechBridge Project"
        )


def main():
    """メインエントリーポイント"""
    # 環境変数を読み込み（ローカル優先）
    from pathlib import Path
    from dotenv import load_dotenv
    
    local_env = Path(__file__).parent / ".env"
    parent_env = Path(__file__).parent.parent.parent / ".env"
    
    if local_env.exists():
        load_dotenv(local_env)
        safe_print(f"✅ ローカル.envファイルを読み込み: {local_env}")
    elif parent_env.exists():
        load_dotenv(parent_env)
        safe_print(f"✅ 親ディレクトリ.envファイルを読み込み: {parent_env}")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # asyncqtイベントループを設定
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # メインウィンドウ表示
    window = ProjectInitializerWindow()
    window.show()
    
    # イベントループ実行
    with loop:
        sys.exit(loop.run_forever())


if __name__ == "__main__":
    main()