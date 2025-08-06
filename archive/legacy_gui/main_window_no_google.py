from __future__ import annotations
"""メインウィンドウ - Google Sheets無効版"""繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ縺ｮ繝｡繧､繝ｳ繧ｦ繧｣繝ｳ繝峨え - Google Sheets讖滂ｿｽE辟｡蜉ｹ迚・""
    
    def __init__(self):
        """MainWindow繧抵ｿｽE譛溷喧"""
        super().__init__()
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
    
    def setup_ui(self):
        """UI繧呈ｧ狗ｯ・""
        self.setWindowTitle("謚陦難ｿｽE豕峨す繝ｪ繝ｼ繧ｺ蛻ｶ菴懈髪謠ｴ繝・・ｽE繝ｫ (Google Sheets辟｡蜉ｹ迚・")
        self.setGeometry(100, 100, 1200, 800)
        
        # 荳ｭ螟ｮ繧ｦ繧｣繧ｸ繧ｧ繝・・ｽ・ｽ
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 繝｡繧､繝ｳ繝ｬ繧､繧｢繧ｦ繝・        main_layout = QVBoxLayout(central_widget)
        
        # 豕ｨ諢上Γ繝・・ｽ・ｽ繝ｼ繧ｸ
        warning_label = QLabel(
            "笞・ｽE・ｽE豕ｨ諢・ Google Sheets讖滂ｿｽE縺檎┌蜉ｹ蛹悶＆繧後※縺・・ｽ・ｽ縺吶・n"
            "萓晏ｭ倬未菫ゑｿｽE蝠城｡後ｒ隗｣豎ｺ蠕後・・ｽ・ｽ蟶ｸ迚・main.py)繧偵＃蛻ｩ逕ｨ縺上□縺輔＞縲・
        )
        warning_label.setStyleSheet("""
            QLabel {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(warning_label)
        
        # 荳企Κ・ｽE・ｽ・ｽE蜉帙ヱ繝阪Ν・ｽE・ｽ辟｡蜉ｹ蛹厄ｼ・        self.input_panel = InputPanel()
        self.input_panel.setEnabled(False)
        
        # 荳ｭ螟ｮ・ｽE・ｽ繧ｹ繝励Μ繝・・ｽ・ｽ繝ｼ・ｽE・ｽ繝ｭ繧ｰ繝代ロ繝ｫ・ｽE・ｽE        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 繝ｭ繧ｰ繝代ロ繝ｫ
        self.log_panel = LogPanel()
        
        # 騾ｲ謐励ヱ繝阪Ν
        self.progress_panel = ProgressPanel()
        
        # 繧ｹ繝励Μ繝・・ｽ・ｽ繝ｼ縺ｫ霑ｽ蜉
        splitter.addWidget(self.log_panel)
        splitter.setStretchFactor(0, 1)
        
        # 繝・・ｽ・ｽ繝域ｩ滂ｿｽE繝懊ち繝ｳ
        test_layout = QHBoxLayout()
        test_dialog_btn = QPushButton("FilePasteDialog 繝・・ｽ・ｽ繝・)
        test_dialog_btn.clicked.connect(self.test_file_paste_dialog)
        test_layout.addWidget(test_dialog_btn)
        test_layout.addStretch()
        
        # 繝ｬ繧､繧｢繧ｦ繝医↓霑ｽ蜉
        main_layout.addWidget(self.input_panel)
        main_layout.addLayout(test_layout)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.progress_panel)
        
        # 繧ｹ繧ｿ繧､繝ｫ險ｭ螳・        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
    
    def setup_menu(self):
        """繝｡繝九Η繝ｼ繝撰ｿｽE繧定ｨｭ螳・""
        menubar = self.menuBar()
        
        # 繝輔ぃ繧､繝ｫ繝｡繝九Η繝ｼ
        file_menu = menubar.addMenu("繝輔ぃ繧､繝ｫ(&F)")
        
        # 邨ゆｺ・・ｽ・ｽ繧ｯ繧ｷ繝ｧ繝ｳ
        exit_action = QAction("邨ゆｺ・&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 繝・・ｽE繝ｫ繝｡繝九Η繝ｼ
        tools_menu = menubar.addMenu("繝・・ｽE繝ｫ(&T)")
        
        # 繝ｭ繧ｰ繧ｯ繝ｪ繧｢繧｢繧ｯ繧ｷ繝ｧ繝ｳ
        clear_log_action = QAction("繝ｭ繧ｰ繧ｯ繝ｪ繧｢(&C)", self)
        clear_log_action.triggered.connect(self.log_panel.clear_logs)
        tools_menu.addAction(clear_log_action)
        
        # 繝倥Ν繝励Γ繝九Η繝ｼ
        help_menu = menubar.addMenu("繝倥Ν繝・&H)")
        
        # 繝撰ｿｽE繧ｸ繝ｧ繝ｳ諠・・ｽ・ｽ繧｢繧ｯ繧ｷ繝ｧ繝ｳ
        about_action = QAction("繝撰ｿｽE繧ｸ繝ｧ繝ｳ諠・・ｽ・ｽ(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_statusbar(self):
        """繧ｹ繝・・ｽE繧ｿ繧ｹ繝撰ｿｽE繧定ｨｭ螳・""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("貅門ｙ螳御ｺ・(Google Sheets讖滂ｿｽE辟｡蜉ｹ)")
    
    def test_file_paste_dialog(self):
        """FilePasteDialog縺ｮ繝・・ｽ・ｽ繝・""
        try:
            from pathlib import Path
            from gui.dialogs.file_paste_dialog import FilePasteDialog
            
            # 繝・・ｽ・ｽ繝育畑縺ｮ繝繝滂ｿｽE繝輔ぃ繧､繝ｫ繝ｪ繧ｹ繝・            test_files = [
                Path("test_file1.docx"),
                Path("test_file2.docx"),
                Path("test_file3.docx")
            ]
            
            # 繝繧､繧｢繝ｭ繧ｰ繧定｡ｨ遉ｺ
            dialog = FilePasteDialog(test_files, "N02279", self)
            result = dialog.exec()
            
            if result == dialog.Accepted:
                self.log_panel.append_log("FilePasteDialog 繝・・ｽ・ｽ繝・ 豁｣蟶ｸ螳御ｺ・, "INFO")
            else:
                self.log_panel.append_log("FilePasteDialog 繝・・ｽ・ｽ繝・ 繧ｭ繝｣繝ｳ繧ｻ繝ｫ", "WARNING")
                
        except Exception as e:
            self.log_panel.append_log(f"FilePasteDialog 繝・・ｽ・ｽ繝医お繝ｩ繝ｼ: {e}", "ERROR")
            QMessageBox.critical(self, "繧ｨ繝ｩ繝ｼ", f"繝・・ｽ・ｽ繝亥ｮ溯｡後お繝ｩ繝ｼ:\n{e}")
    
    def show_about(self):
        """繝撰ｿｽE繧ｸ繝ｧ繝ｳ諠・・ｽ・ｽ繧定｡ｨ遉ｺ"""
        QMessageBox.about(
            self,
            "繝撰ｿｽE繧ｸ繝ｧ繝ｳ諠・・ｽ・ｽ",
            "謚陦難ｿｽE豕峨す繝ｪ繝ｼ繧ｺ蛻ｶ菴懈髪謠ｴ繝・・ｽE繝ｫ\\n\\n"
            "繝撰ｿｽE繧ｸ繝ｧ繝ｳ: 1.0.0 (Google Sheets辟｡蜉ｹ迚・\\n"
            "髢狗匱: Technical Fountain Team\\n\\n"
            "縺難ｿｽE繝・・ｽE繝ｫ縺ｯ謚陦難ｿｽE豕峨す繝ｪ繝ｼ繧ｺ縺ｮ蛻ｶ菴懶ｿｽE繝ｭ繧ｻ繧ｹ繧箪\n"
            "閾ｪ蜍募喧繝ｻ蜉ｹ邇・・ｽ・ｽ縺吶ｋ縺溘ａ縺ｫ髢狗匱縺輔ｌ縺ｾ縺励◆縲・
        )