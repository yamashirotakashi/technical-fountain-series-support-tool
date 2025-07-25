"""フォルダ選択ダイアログ"""
import json
import os
from pathlib import Path
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QCheckBox, QSplitter, QTextEdit, QMessageBox,
    QWidget, QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from utils.logger import get_logger


class FolderSelectorDialog(QDialog):
    """作業フォルダ選択ダイアログ"""
    
    folder_confirmed = pyqtSignal(str, bool)  # (選択されたパス, 設定を保存するか)
    
    def __init__(self, repo_path: Path, repo_name: str, default_folder: Optional[Path] = None, parent=None):
        """
        Args:
            repo_path: リポジトリのルートパス
            repo_name: リポジトリ名（設定保存用）
            default_folder: デフォルトで選択するフォルダ
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.repo_path = repo_path
        self.repo_name = repo_name
        self.default_folder = default_folder
        self.selected_folder = default_folder
        
        # 保存された設定を読み込む
        self.settings_file = Path.home() / ".techzip" / "folder_settings.json"
        self.saved_settings = self._load_settings()
        
        self.setup_ui()
        self._populate_tree()
        
        # デフォルトフォルダまたは保存された設定を選択
        if self.repo_name in self.saved_settings:
            saved_path = Path(self.saved_settings[self.repo_name])
            if saved_path.exists() and str(saved_path).startswith(str(repo_path)):
                self._select_folder_in_tree(saved_path)
        elif default_folder:
            self._select_folder_in_tree(default_folder)
    
    def setup_ui(self):
        """UIを設定"""
        self.setWindowTitle("作業フォルダの選択")
        self.setModal(True)
        self.resize(800, 600)
        
        # メインレイアウト
        main_layout = QVBoxLayout(self)
        
        # 説明ラベル
        info_label = QLabel(
            "Re:VIEW関連ファイル（.re, config.yml, catalog.yml）が含まれるフォルダを選択してください。"
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # スプリッター（ツリーとプレビュー）
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ファイルツリー
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("フォルダ構造")
        self.tree_widget.itemClicked.connect(self._on_item_clicked)
        splitter.addWidget(self.tree_widget)
        
        # プレビューエリア
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_label = QLabel("選択されたフォルダ:")
        preview_label.setFont(QFont("", 10, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label)
        
        self.path_label = QLabel("")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; }")
        preview_layout.addWidget(self.path_label)
        
        preview_label2 = QLabel("フォルダ内容:")
        preview_label2.setFont(QFont("", 10, QFont.Weight.Bold))
        preview_layout.addWidget(preview_label2)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([400, 400])
        
        main_layout.addWidget(splitter)
        
        # チェックボックス
        self.save_settings_checkbox = QCheckBox("次回からも同じフォルダで作業")
        if self.repo_name in self.saved_settings:
            self.save_settings_checkbox.setChecked(True)
        main_layout.addWidget(self.save_settings_checkbox)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        self.change_button = QPushButton("変更")
        self.change_button.setEnabled(False)
        self.change_button.clicked.connect(self._on_change_clicked)
        button_layout.addWidget(self.change_button)
        
        self.confirm_button = QPushButton("Zip作成")
        self.confirm_button.setDefault(True)
        self.confirm_button.clicked.connect(self._on_confirm_clicked)
        button_layout.addWidget(self.confirm_button)
        
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
    
    def _populate_tree(self):
        """ファイルツリーを構築"""
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, self.repo_path.name)
        root_item.setData(0, Qt.ItemDataRole.UserRole, str(self.repo_path))
        root_item.setExpanded(True)
        
        # アイコンを設定
        root_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        
        self._add_tree_items(root_item, self.repo_path)
    
    def _add_tree_items(self, parent_item: QTreeWidgetItem, parent_path: Path):
        """ツリーアイテムを再帰的に追加"""
        try:
            # フォルダのみを表示
            for item in sorted(parent_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, item.name)
                    child_item.setData(0, Qt.ItemDataRole.UserRole, str(item))
                    
                    # Re:VIEWフォルダかチェック
                    if self._is_review_folder(item):
                        child_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
                        # 太字で表示
                        font = child_item.font(0)
                        font.setBold(True)
                        child_item.setFont(0, font)
                    else:
                        child_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
                    
                    # 再帰的に子アイテムを追加
                    self._add_tree_items(child_item, item)
        except PermissionError:
            pass
    
    def _is_review_folder(self, path: Path) -> bool:
        """Re:VIEWフォルダかチェック"""
        required_files = {'config.yml', 'catalog.yml'}
        
        try:
            # .reファイルの存在確認
            has_re_file = any(f.suffix == '.re' for f in path.iterdir() if f.is_file())
            
            # 必須ファイルの存在確認
            existing_files = {f.name for f in path.iterdir() if f.is_file()}
            has_required_files = required_files.issubset(existing_files)
            
            return has_re_file and has_required_files
        except:
            return False
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """アイテムクリック時の処理"""
        path = Path(item.data(0, Qt.ItemDataRole.UserRole))
        self.selected_folder = path
        
        # パスを表示
        self.path_label.setText(str(path))
        
        # フォルダ内容をプレビュー
        self._update_preview(path)
        
        # 変更ボタンを有効化
        self.change_button.setEnabled(True)
    
    def _update_preview(self, path: Path):
        """フォルダ内容のプレビューを更新"""
        preview_lines = []
        
        try:
            # Re:VIEWフォルダかチェック
            is_review = self._is_review_folder(path)
            if is_review:
                preview_lines.append("✅ Re:VIEWフォルダとして認識されました\n")
            else:
                preview_lines.append("⚠️ Re:VIEWフォルダの要件を満たしていません\n")
            
            preview_lines.append("【ファイル一覧】")
            
            # ファイル一覧（最大20個）
            files = sorted(path.iterdir())[:20]
            for file in files:
                if file.is_file():
                    # 重要なファイルをハイライト
                    if file.name in ['config.yml', 'catalog.yml']:
                        preview_lines.append(f"  📄 {file.name} ✓")
                    elif file.suffix == '.re':
                        preview_lines.append(f"  📝 {file.name} ✓")
                    else:
                        preview_lines.append(f"  📄 {file.name}")
                else:
                    preview_lines.append(f"  📁 {file.name}/")
            
            if len(list(path.iterdir())) > 20:
                preview_lines.append("  ...")
            
        except Exception as e:
            preview_lines.append(f"エラー: {e}")
        
        self.preview_text.setPlainText("\n".join(preview_lines))
    
    def _select_folder_in_tree(self, folder_path: Path):
        """ツリー内の指定フォルダを選択"""
        # ルートから順にパスを辿る
        relative_path = folder_path.relative_to(self.repo_path)
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
        
        # 最終的なアイテムを選択
        self.tree_widget.setCurrentItem(current_item)
        self._on_item_clicked(current_item, 0)
    
    def _on_change_clicked(self):
        """変更ボタンクリック時"""
        if not self.selected_folder:
            QMessageBox.warning(self, "警告", "フォルダを選択してください。")
            return
        
        # Re:VIEWフォルダでない場合は警告
        if not self._is_review_folder(self.selected_folder):
            reply = QMessageBox.warning(
                self, "確認",
                "選択されたフォルダにはRe:VIEWの必須ファイルが含まれていません。\n"
                "このフォルダを使用しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # 選択を確定（ダイアログは閉じない）
        self.path_label.setText(f"✓ {str(self.selected_folder)}")
        QMessageBox.information(self, "確認", "フォルダが変更されました。")
    
    def _on_confirm_clicked(self):
        """Zip作成ボタンクリック時"""
        if not self.selected_folder:
            QMessageBox.warning(self, "警告", "フォルダを選択してください。")
            return
        
        # 設定を保存するかチェック
        save_settings = self.save_settings_checkbox.isChecked()
        
        if save_settings:
            self._save_settings(self.repo_name, str(self.selected_folder))
        
        # シグナルを発行してダイアログを閉じる
        self.folder_confirmed.emit(str(self.selected_folder), save_settings)
        self.accept()
    
    def _load_settings(self) -> Dict[str, str]:
        """保存された設定を読み込む"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"設定ファイルの読み込みエラー: {e}")
        return {}
    
    def _save_settings(self, repo_name: str, folder_path: str):
        """設定を保存"""
        settings = self._load_settings()
        settings[repo_name] = folder_path
        
        # ディレクトリを作成
        self.settings_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.logger.info(f"フォルダ設定を保存: {repo_name} -> {folder_path}")
        except Exception as e:
            self.logger.error(f"設定ファイルの保存エラー: {e}")