from __future__ import annotations
"""Progress bar module"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
                             QLabel, QGroupBox, QPushButton)
from PyQt6.QtCore import pyqtSignal, pyqtSlot


class ProgressPanel(QWidget):
    """Progress display panel widget"""
    
    # Custom signals
    cancel_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Initialize ProgressPanel
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.total_items = 0
        self.completed_items = 0
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        
        # Group box
        group_box = QGroupBox("処理進行状況")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        group_layout = QVBoxLayout(group_box)
        
        # Status label
        self.status_label = QLabel("準備完了")
        self.status_label.setStyleSheet("color: #666; margin-bottom: 5px;")
        
        # Progress info layout
        info_layout = QHBoxLayout()
        
        # Progress label
        self.progress_label = QLabel("0 / 0 項目")
        self.progress_label.setStyleSheet("color: #333;")
        
        # Cancel button
        self.cancel_button = QPushButton("キャンセル")
        self.cancel_button.clicked.connect(self.cancel_requested.emit)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                padding: 4px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c01005;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        info_layout.addWidget(self.progress_label)
        info_layout.addStretch()
        info_layout.addWidget(self.cancel_button)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # Add to group layout
        group_layout.addWidget(self.status_label)
        group_layout.addLayout(info_layout)
        group_layout.addWidget(self.progress_bar)
        
        # Add to main layout
        layout.addWidget(group_box)
    
    def set_total_items(self, total: int):
        """
        Set total number of items
        
        Args:
            total: Total number of items
        """
        self.total_items = total
        self.completed_items = 0
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(0)
        self.update_label()
        self.cancel_button.setEnabled(True)
    
    @pyqtSlot(int)
    def update_progress(self, value: int):
        """
        Update progress
        
        Args:
            value: Progress value (0-100)
        """
        self.progress_bar.setValue(value)
        self.completed_items = int((value / 100) * self.total_items)
        self.update_label()
    
    @pyqtSlot(str)
    def update_status(self, status: str):
        """
        Update status text
        
        Args:
            status: Status message
        """
        self.status_label.setText(status)
    
    def update_label(self):
        """Update progress label"""
        self.progress_label.setText(f"{self.completed_items} / {self.total_items} 項目")
    
    def reset(self):
        """Reset progress"""
        self.total_items = 0
        self.completed_items = 0
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.status_label.setText("処理中...")
        self.update_label()
        self.cancel_button.setEnabled(True)
    
    def reset_progress(self):
        """Reset progress (alias)"""
        self.reset()
    
    def set_cancel_enabled(self, enabled: bool):
        """
        Set cancel button enabled state
        
        Args:
            enabled: True to enable cancel button
        """
        self.cancel_button.setEnabled(enabled)