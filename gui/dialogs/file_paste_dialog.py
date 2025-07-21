"""ファイルペーストダイアログ - ZIPファイル処理後のファイル選択・ペースト機能"""
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QCheckBox, QSplitter, QTextEdit, QMessageBox,
    QWidget, QGroupBox, QProgressBar, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QIcon, QFont

from utils.logger import get_logger


class FilePasteWorker(QThread):
    """ファイルペースト処理を行うワーカースレッド"""
    progress_updated = pyqtSignal(int, str)  # (progress, message)
    finished = pyqtSignal(bool, str)  # (success, message)
    
    def __init__(self, source_files: List[Path], target_folder: Path):
        super().__init__()
        self.source_files = source_files
        self.target_folder = target_folder
        self.logger = get_logger(__name__)
    
    def run(self):
        """ファイルペースト処理を実行"""
        try:
            total_files = len(self.source_files)
            success_count = 0
            
            for i, source_file in enumerate(self.source_files):
                # 進捗を更新
                progress = int((i / total_files) * 100)
                self.progress_updated.emit(progress, f"コピー中: {source_file.name}")
                
                # ターゲットファイルパス
                target_file = self.target_folder / source_file.name
                
                try:
                    # ファイルコピー
                    shutil.copy2(source_file, target_file)
                    success_count += 1
                    self.logger.info(f"ファイルコピー成功: {source_file} -> {target_file}")
                    
                except Exception as e:
                    self.logger.error(f"ファイルコピーエラー {source_file}: {e}")
            
            # 完了
            self.progress_updated.emit(100, "完了")
            success_message = f"{success_count}/{total_files} ファイルのコピーが完了しました"
            self.finished.emit(success_count == total_files, success_message)
            
        except Exception as e:
            self.logger.error(f"ファイルペースト処理エラー: {e}")
            self.finished.emit(False, f"エラーが発生しました: {e}")


class FilePasteDialog(QDialog):
    """ファイルペーストダイアログ - Windowsファイルマネージャー風UI"""
    
    def __init__(self, file_info_list: List[Dict], ncode: str, parent=None):
        """
        Args:
            file_info_list: ファイル情報の辞書リスト（name, path, sizeを含む）
            ncode: 対象のNコード
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.file_info_list = file_info_list
        self.ncode = ncode
        self.selected_files = set()  # 選択されたファイルのセット（インデックス）
        self.selection_mode = "all"  # "all" または "partial"
        
        # 本文フォルダのパスを構築
        base_path = Path("G:/.shortcut-targets-by-id/0B6euJ_grVeOeMnJLU1IyUWgxeWM/NP-IRD")
        self.ncode_folder = base_path / ncode
        self.target_folder = self.ncode_folder / "本文"
        
        self.setup_ui()
        self._populate_file_lists()
        
        # 進捗表示用
        self.worker = None
    
    def setup_ui(self):
        """UIを設定"""
        self.setWindowTitle(f"ファイルペースト - {self.ncode}")
        self.setModal(True)
        self.resize(1000, 700)
        
        # メインレイアウト
        main_layout = QVBoxLayout(self)
        
        # 説明ラベル
        info_label = QLabel(
            f"ZIPファイルから抽出されたWordファイル（1行目削除済み）を本文フォルダにペーストします。\n"
            f"対象フォルダ: {self.target_folder}"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("QLabel { background-color: #e6f3ff; padding: 10px; border: 1px solid #0066cc; }")
        main_layout.addWidget(info_label)
        
        # ファイルマネージャー風の分割ビュー
        splitter = QSplitter(Qt.Horizontal)
        
        # 左パネル: ペースト用ファイル一覧
        left_panel = self._create_source_panel()
        splitter.addWidget(left_panel)
        
        # 右パネル: 本文フォルダの内容
        right_panel = self._create_target_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter)
        
        # 進捗バー
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 進捗メッセージ
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        main_layout.addWidget(self.progress_label)
        
        # ボタンエリア
        button_layout = QHBoxLayout()
        
        # 全選択/全解除ボタン（部分選択モード時のみ表示）
        self.select_all_button = QPushButton("全選択")
        self.select_all_button.clicked.connect(self._select_all_files)
        self.select_all_button.setVisible(False)  # 初期は非表示
        button_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton("全解除")
        self.deselect_all_button.clicked.connect(self._deselect_all_files)
        self.deselect_all_button.setVisible(False)  # 初期は非表示
        button_layout.addWidget(self.deselect_all_button)
        
        button_layout.addStretch()
        
        # 一部選択ボタン
        self.partial_select_button = QPushButton("一部ファイルのみ選択")
        self.partial_select_button.clicked.connect(self._toggle_selection_mode)
        button_layout.addWidget(self.partial_select_button)
        
        # ファイルペーストボタン
        self.paste_button = QPushButton("ファイルをペースト")
        self.paste_button.setStyleSheet("QPushButton { background-color: #0066cc; color: white; font-weight: bold; }")
        self.paste_button.clicked.connect(self._paste_files)
        button_layout.addWidget(self.paste_button)
        
        # キャンセルボタン
        cancel_button = QPushButton("キャンセル")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # 初期状態は全ファイル選択モード（チェックボックス非表示）
        self._set_initial_state()
    
    def _create_source_panel(self) -> QWidget:
        """ペースト用ファイル一覧パネルを作成"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # タイトル
        title_label = QLabel("ペースト用ファイル")
        title_label.setFont(QFont("", 12, QFont.Bold))
        title_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 5px; }")
        layout.addWidget(title_label)
        
        # スクロールエリア
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.source_layout = QVBoxLayout(scroll_widget)
        
        # ファイルチェックボックスを動的に追加
        self.file_checkboxes = {}
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        return panel
    
    def _create_target_panel(self) -> QWidget:
        """本文フォルダ内容パネルを作成"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # タイトル
        title_label = QLabel("本文フォルダの内容")
        title_label.setFont(QFont("", 12, QFont.Bold))
        title_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 5px; }")
        layout.addWidget(title_label)
        
        # フォルダパス表示
        self.target_path_label = QLabel(str(self.target_folder))
        self.target_path_label.setWordWrap(True)
        self.target_path_label.setStyleSheet("QLabel { background-color: #ffffcc; padding: 10px; }")
        layout.addWidget(self.target_path_label)
        
        # ファイル一覧
        self.target_file_list = QTextEdit()
        self.target_file_list.setReadOnly(True)
        layout.addWidget(self.target_file_list)
        
        return panel
    
    def _populate_file_lists(self):
        """ファイル一覧を表示"""
        # ペースト用ファイル一覧
        for index, file_info in enumerate(self.file_info_list):
            # ファイル名ラベル（常に表示）
            file_label = QLabel(file_info['name'])
            file_label.setFont(QFont("", 10, QFont.Bold))
            
            # チェックボックス（初期は非表示）
            checkbox = QCheckBox(file_info['name'])
            checkbox.setFont(QFont("", 10))
            checkbox.setVisible(False)  # 初期は非表示
            checkbox.stateChanged.connect(self._on_checkbox_changed)
            
            # ファイル情報を表示（事前に収集済みの安全なデータ）
            if file_info['size'] > 0:
                info_text = f"  サイズ: {file_info['size']:,} bytes"
            else:
                info_text = f"  パス: {file_info['path']}"
            info_label = QLabel(info_text)
            info_label.setStyleSheet("QLabel { color: #666; margin-left: 20px; }")
            
            self.source_layout.addWidget(file_label)
            self.source_layout.addWidget(checkbox)
            self.source_layout.addWidget(info_label)
            
            self.file_checkboxes[index] = checkbox
            # ファイルラベルも保存（表示制御用）
            if not hasattr(self, 'file_labels'):
                self.file_labels = {}
            self.file_labels[index] = file_label
        
        self.source_layout.addStretch()
        
        # 本文フォルダの内容表示
        self._update_target_folder_display()
    
    def _set_initial_state(self):
        """初期状態を設定"""
        # 全ファイル選択モード
        self.selection_mode = "all"
        self.selected_files = set(range(len(self.file_info_list)))
        
        # チェックボックスは非表示、ラベルは表示
        for index in range(len(self.file_info_list)):
            self.file_checkboxes[index].setVisible(False)
            self.file_labels[index].setVisible(True)
        
        # ペーストボタンの状態を更新
        self._update_paste_button()
    
    def _on_checkbox_changed(self):
        """チェックボックス状態変更時の処理"""
        if self.selection_mode == "partial":
            self._update_paste_button()
    
    def _update_target_folder_display(self):
        """本文フォルダの内容を更新"""
        lines = []
        
        try:
            if not self.target_folder.exists():
                lines.append("⚠️ 本文フォルダが存在しません")
                lines.append(f"フォルダパス: {self.target_folder}")
                lines.append("\n※ ペースト時に自動作成されます")
            else:
                lines.append("📁 本文フォルダの現在の内容:")
                lines.append("")
                
                try:
                    files = sorted(self.target_folder.iterdir())
                    if not files:
                        lines.append("  (ファイルなし)")
                    else:
                        for file in files:
                            try:
                                if file.is_file():
                                    size = file.stat().st_size
                                    lines.append(f"  📄 {file.name} ({size:,} bytes)")
                                else:
                                    lines.append(f"  📁 {file.name}/")
                            except Exception:
                                lines.append(f"  📄 {file.name} (サイズ不明)")
                except Exception as e:
                    lines.append(f"  エラー: {e}")
        except Exception as e:
            lines.append(f"フォルダアクセスエラー: {e}")
        
        self.target_file_list.setPlainText("\n".join(lines))
    
    def _toggle_selection_mode(self):
        """選択モードを切り替え"""
        if self.selection_mode == "all":
            # 部分選択モードに切り替え
            self.selection_mode = "partial"
            self.partial_select_button.setText("全ファイル選択に戻る")
            
            # チェックボックスを表示、ラベルを非表示
            for index in range(len(self.file_info_list)):
                self.file_checkboxes[index].setVisible(True)
                self.file_labels[index].setVisible(False)
            
            # 全選択/全解除ボタンを表示
            self.select_all_button.setVisible(True)
            self.deselect_all_button.setVisible(True)
            
            # すべてのファイルを選択状態にする
            self._select_all_files()
            
        else:
            # 全ファイル選択モードに戻る
            self.selection_mode = "all"
            self.partial_select_button.setText("一部ファイルのみ選択")
            
            # チェックボックスを非表示、ラベルを表示
            for index in range(len(self.file_info_list)):
                self.file_checkboxes[index].setVisible(False)
                self.file_labels[index].setVisible(True)
            
            # 全選択/全解除ボタンを非表示
            self.select_all_button.setVisible(False)
            self.deselect_all_button.setVisible(False)
            
            # 全ファイル選択状態にする
            self.selected_files = set(range(len(self.file_info_list)))
            self._update_paste_button()
    
    def _select_all_files(self):
        """全ファイルを選択"""
        self.selected_files = set(range(len(self.file_info_list)))
        # シグナルをブロックして無限再帰を防ぐ
        for checkbox in self.file_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(True)
            checkbox.blockSignals(False)
        self._update_paste_button()
    
    def _deselect_all_files(self):
        """全ファイルの選択を解除"""
        self.selected_files.clear()
        # シグナルをブロックして無限再帰を防ぐ
        for checkbox in self.file_checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
        self._update_paste_button()
    
    def _update_paste_button(self):
        """ペーストボタンの状態を更新"""
        if self.selection_mode == "all":
            # 全ファイル選択モード
            self.selected_files = set(range(len(self.file_info_list)))
            self.paste_button.setText(f"ファイルをペースト (全{len(self.file_info_list)}個)")
            self.paste_button.setEnabled(True)
        else:
            # 部分選択モード - チェックされたファイルを取得
            self.selected_files.clear()
            for index, checkbox in self.file_checkboxes.items():
                if checkbox.isChecked():
                    self.selected_files.add(index)
            
            # ボタンのテキストと状態を更新
            if self.selected_files:
                self.paste_button.setText(f"ファイルをペースト ({len(self.selected_files)}個)")
                self.paste_button.setEnabled(True)
            else:
                self.paste_button.setText("ファイルをペースト")
                self.paste_button.setEnabled(False)
    
    def _paste_files(self):
        """選択されたファイルをペースト"""
        if not self.selected_files:
            QMessageBox.warning(self, "警告", "ペーストするファイルを選択してください。")
            return
        
        # 確認ダイアログ
        if self.selection_mode == "all":
            message = f"全{len(self.selected_files)}個のファイルを本文フォルダにペーストします。\n"
        else:
            message = f"選択された{len(self.selected_files)}個のファイルを本文フォルダにペーストします。\n"
        
        message += f"既存のファイルは上書きされます。\n\n"
        message += f"ターゲットフォルダ: {self.target_folder}\n\n"
        message += f"実行しますか？"
        
        reply = QMessageBox.question(
            self, "確認",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 本文フォルダが存在しない場合は作成
        try:
            self.target_folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"本文フォルダの作成に失敗しました:\n{e}")
            return
        
        # 選択されたファイルのパス情報を構築
        selected_file_paths = []
        for index in self.selected_files:
            file_info = self.file_info_list[index]
            selected_file_paths.append(Path(file_info['path']))
        
        # ワーカースレッドでファイルペーストを実行
        self.worker = FilePasteWorker(selected_file_paths, self.target_folder)
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.finished.connect(self._on_paste_finished)
        
        # UIを更新
        self.paste_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        
        self.worker.start()
    
    @pyqtSlot(int, str)
    def _on_progress_updated(self, progress: int, message: str):
        """進捗更新"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
    
    @pyqtSlot(bool, str)
    def _on_paste_finished(self, success: bool, message: str):
        """ペースト完了"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.paste_button.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "完了", message)
            # 本文フォルダの表示を更新
            self._update_target_folder_display()
            # ダイアログを閉じる
            self.accept()
        else:
            QMessageBox.critical(self, "エラー", message)
        
        self.worker = None

    def closeEvent(self, event):
        """ダイアログ閉じる時の処理"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "確認",
                "ファイルペースト処理が実行中です。\n"
                "キャンセルしますか？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.terminate()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()