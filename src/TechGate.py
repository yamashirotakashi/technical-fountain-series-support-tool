#!/usr/bin/env python3
"""
TechGate - 3ツール統合ランチャー
バージョン自動検出対応統合ランチャー
"""

import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import threading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QTextEdit, QComboBox, QCheckBox,
    QProgressBar, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

class ToolInfo:
    def __init__(self, name: str, display_name: str, description: str, base_path: str, icon: str = "[TOOL]"):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.base_path = base_path
        self.icon = icon
        self.versions: List[Tuple[str, str]] = []
        self.latest_version: Optional[str] = None
        self.latest_exe_path: Optional[str] = None
        self.process: Optional[subprocess.Popen] = None
        self.status = "ready"

class VersionDetector:
    def __init__(self, dist_dir: Path):
        self.dist_dir = dist_dir
        self.version_patterns = {
            "pjinit": {
                "folder_pattern": r"PJinit\.(\d+\.\d+)",
                "exe_pattern": r"PJinit\.(\d+\.\d+)\.exe"
            },
            "techzip": {
                "folder_pattern": r"TECHZIP\.(\d+\.\d+)",
                "exe_pattern": r"TECHZIP\.(\d+\.\d+)\.exe"
            },
            "overflow": {
                "folder_pattern": r"OverflowChecker_v(\d+\.\d+\.\d+)",
                "exe_pattern": r"OverflowChecker\.exe"
            }
        }
    
    def detect_all_versions(self) -> Dict[str, ToolInfo]:
        tools = {
            "pjinit": ToolInfo("pjinit", "[PJ] PJinit", "プロジェクト初期化", "PJinit", "[PJ]"),
            "techzip": ToolInfo("techzip", "[ZIP] TECHZIP", "Re:VIEW → Word変換", "TECHZIP", "[ZIP]"),
            "overflow": ToolInfo("overflow", "[CHK] はみ出し分析", "PDF品質チェック", "OverflowChecker", "[CHK]")
        }
        
        for tool_id, tool_info in tools.items():
            self._detect_tool_versions(tool_id, tool_info)
        
        return tools
    
    def _detect_tool_versions(self, tool_id: str, tool_info: ToolInfo):
        patterns = self.version_patterns[tool_id]
        found_versions = []
        folder_pattern = re.compile(patterns["folder_pattern"])
        
        for item in self.dist_dir.iterdir():
            if not item.is_dir():
                continue
            
            match = folder_pattern.match(item.name)
            if match:
                version = match.group(1)
                
                if tool_id == "overflow":
                    exe_path = item / "OverflowChecker.exe"
                else:
                    exe_path = item / f"{tool_info.base_path}.{version}.exe"
                
                if exe_path.exists():
                    found_versions.append((version, str(exe_path)))
        
        found_versions.sort(key=lambda x: self._version_to_tuple(x[0]), reverse=True)
        tool_info.versions = found_versions
        if found_versions:
            tool_info.latest_version = found_versions[0][0]
            tool_info.latest_exe_path = found_versions[0][1]
    
    def _version_to_tuple(self, version: str) -> Tuple[int, ...]:
        try:
            return tuple(map(int, version.split('.')))
        except:
            return (0, 0, 0)

class ToolLauncher:
    def __init__(self):
        self.running_tools: Dict[str, ToolInfo] = {}
    
    def launch_tool(self, tool_info: ToolInfo, version: str = None) -> Dict[str, str]:
        if tool_info.name in self.running_tools:
            return {"status": "warning", "message": f"{tool_info.display_name}は既に実行中です"}
        
        exe_path = None
        if version:
            for v, path in tool_info.versions:
                if v == version:
                    exe_path = path
                    break
        else:
            exe_path = tool_info.latest_exe_path
        
        if not exe_path or not Path(exe_path).exists():
            return {"status": "error", "message": f"実行ファイルが見つかりません: {exe_path}"}
        
        try:
            process = subprocess.Popen(
                [exe_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            
            tool_info.process = process
            tool_info.status = "running"
            self.running_tools[tool_info.name] = tool_info
            
            return {
                "status": "success",
                "message": f"{tool_info.display_name} v{version or tool_info.latest_version}を起動しました",
                "pid": process.pid
            }
            
        except Exception as e:
            return {"status": "error", "message": f"起動に失敗しました: {str(e)}"}

class TechGateGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # EXE実行時とPython実行時でパスを調整
        if getattr(sys, 'frozen', False):
            # EXE実行時
            self.dist_dir = Path(sys.executable).parent.parent
        else:
            # Python実行時
            self.dist_dir = Path(__file__).parent.parent / "dist"
        self.version_detector = VersionDetector(self.dist_dir)
        self.launcher = ToolLauncher()
        self.tools: Dict[str, ToolInfo] = {}
        
        self.setup_ui()
        self.setup_timer()
        self.detect_tools()
    
    def setup_ui(self):
        self.setWindowTitle("TechGate v0.5 - 3ツール統合ランチャー")
        self.setGeometry(150, 150, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)
        
        central_widget.setLayout(main_layout)
    
    def create_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout()
        
        header = QGroupBox()
        header_layout = QVBoxLayout()
        title = QLabel("TechGate")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("3ツール統合ランチャー（バージョン自動検出対応）")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 12px;")
        header_layout.addWidget(subtitle)
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        tools_section = QGroupBox("ツール起動")
        self.tools_layout = QVBoxLayout()
        tools_section.setLayout(self.tools_layout)
        layout.addWidget(tools_section)
        
        batch_section = self.create_batch_section()
        layout.addWidget(batch_section)
        
        settings_section = self.create_settings_section()
        layout.addWidget(settings_section)
        
        panel.setLayout(layout)
        return panel
    
    def create_batch_section(self) -> QWidget:
        section = QGroupBox("一括操作")
        layout = QVBoxLayout()
        
        workflow_layout = QHBoxLayout()
        workflow_layout.addWidget(QLabel("ワークフロー:"))
        
        self.workflow_combo = QComboBox()
        self.workflow_combo.addItems([
            "カスタム選択",
            "完全ワークフロー (PJinit → TECHZIP → はみ出し分析)",
            "変換 + 品質チェック (TECHZIP → はみ出し分析)",
            "プロジェクト初期化のみ (PJinit)",
            "変換処理のみ (TECHZIP)",
            "品質チェックのみ (はみ出し分析)"
        ])
        workflow_layout.addWidget(self.workflow_combo)
        layout.addLayout(workflow_layout)
        
        batch_launch_btn = QPushButton("[実行] 選択ワークフロー実行")
        batch_launch_btn.clicked.connect(self.launch_workflow)
        layout.addWidget(batch_launch_btn)
        
        section.setLayout(layout)
        return section
    
    def create_settings_section(self) -> QWidget:
        section = QGroupBox("設定")
        layout = QVBoxLayout()
        
        refresh_btn = QPushButton("[更新] バージョン情報更新")
        refresh_btn.clicked.connect(self.detect_tools)
        layout.addWidget(refresh_btn)
        
        section.setLayout(layout)
        return section
    
    def create_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout()
        
        status_section = QGroupBox("実行状況")
        status_layout = QVBoxLayout()
        self.status_list = QListWidget()
        status_layout.addWidget(self.status_list)
        status_section.setLayout(status_layout)
        layout.addWidget(status_section)
        
        log_section = QGroupBox("実行ログ")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                color: #333;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        clear_btn = QPushButton("クリア")
        clear_btn.clicked.connect(self.log_text.clear)
        log_layout.addWidget(clear_btn)
        
        log_section.setLayout(log_layout)
        layout.addWidget(log_section)
        
        panel.setLayout(layout)
        return panel
    
    def setup_timer(self):
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_tool_status)
        self.status_timer.start(5000)
    
    def detect_tools(self):
        self.add_log("[DETECT] ツールバージョン検出を開始...")
        self.tools = self.version_detector.detect_all_versions()
        self.create_tool_panels()
        
        for tool_name, tool_info in self.tools.items():
            if tool_info.versions:
                versions_str = ", ".join([f"v{v}" for v, _ in tool_info.versions])
                self.add_log(f"[OK] {tool_info.display_name}: {versions_str} (最新: v{tool_info.latest_version})")
            else:
                self.add_log(f"[ERROR] {tool_info.display_name}: EXEファイルが見つかりません")
    
    def create_tool_panels(self):
        for i in reversed(range(self.tools_layout.count())):
            child = self.tools_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        for tool_name, tool_info in self.tools.items():
            panel = self.create_single_tool_panel(tool_info)
            self.tools_layout.addWidget(panel)
    
    def create_single_tool_panel(self, tool_info: ToolInfo) -> QWidget:
        panel = QGroupBox(f"{tool_info.icon} {tool_info.display_name}")
        layout = QVBoxLayout()
        
        desc_label = QLabel(tool_info.description)
        desc_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(desc_label)
        
        control_layout = QHBoxLayout()
        
        version_combo = QComboBox()
        if tool_info.versions:
            for version, _ in tool_info.versions:
                version_combo.addItem(f"v{version}")
        else:
            version_combo.addItem("利用不可")
            version_combo.setEnabled(False)
        
        control_layout.addWidget(QLabel("Version:"))
        control_layout.addWidget(version_combo)
        
        launch_btn = QPushButton("起動")
        launch_btn.setEnabled(bool(tool_info.versions))
        launch_btn.clicked.connect(
            lambda _, t=tool_info, c=version_combo: self.launch_selected_tool(t, c)
        )
        control_layout.addWidget(launch_btn)
        
        layout.addLayout(control_layout)
        panel.setLayout(layout)
        return panel
    
    def launch_selected_tool(self, tool_info: ToolInfo, version_combo: QComboBox):
        if not tool_info.versions:
            return
        
        selected_index = version_combo.currentIndex()
        selected_version = tool_info.versions[selected_index][0]
        
        result = self.launcher.launch_tool(tool_info, selected_version)
        
        if result["status"] == "success":
            self.add_log(f"[OK] {result['message']}")
        elif result["status"] == "warning":
            self.add_log(f"[WARN] {result['message']}")
        else:
            self.add_log(f"[ERROR] {result['message']}")
        
        self.update_tool_status()
    
    def launch_workflow(self):
        selected_workflow = self.workflow_combo.currentText()
        
        if "完全ワークフロー" in selected_workflow:
            self.add_log("[START] 完全ワークフローを開始します...")
            self.execute_sequential_workflow(["pjinit", "techzip", "overflow"])
        elif "変換 + 品質チェック" in selected_workflow:
            self.add_log("[START] 変換+品質チェックワークフローを開始します...")
            self.execute_sequential_workflow(["techzip", "overflow"])
        elif "プロジェクト初期化のみ" in selected_workflow:
            self.launch_single_tool("pjinit")
        elif "変換処理のみ" in selected_workflow:
            self.launch_single_tool("techzip")
        elif "品質チェックのみ" in selected_workflow:
            self.launch_single_tool("overflow")
    
    def execute_sequential_workflow(self, tool_sequence: List[str]):
        if tool_sequence:
            first_tool = tool_sequence[0]
            if first_tool in self.tools:
                result = self.launcher.launch_tool(self.tools[first_tool])
                if result["status"] == "success":
                    self.add_log(f"[OK] {result['message']}")
                else:
                    self.add_log(f"[ERROR] ワークフロー開始に失敗: {result['message']}")
    
    def launch_single_tool(self, tool_name: str):
        if tool_name in self.tools:
            result = self.launcher.launch_tool(self.tools[tool_name])
            if result["status"] == "success":
                self.add_log(f"[OK] {result['message']}")
            else:
                self.add_log(f"[ERROR] {result['message']}")
    
    def update_tool_status(self):
        self.status_list.clear()
        
        if self.launcher.running_tools:
            for tool_name, tool_info in self.launcher.running_tools.items():
                item_text = f"[RUN] {tool_info.display_name} v{tool_info.latest_version} - 実行中"
                item = QListWidgetItem(item_text)
                self.status_list.addItem(item)
        else:
            item = QListWidgetItem("[IDLE] 実行中のツールはありません")
            self.status_list.addItem(item)
    
    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TechGate")
    
    launcher = TechGateGUI()
    launcher.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()