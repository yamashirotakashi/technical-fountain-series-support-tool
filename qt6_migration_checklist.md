# PyQt5 → PyQt6 移行チェックリスト

## 主要な変更点

### 1. Enum名前空間の変更
- [ ] Qt.UserRole → Qt.ItemDataRole.UserRole
- [ ] Qt.DisplayRole → Qt.ItemDataRole.DisplayRole
- [ ] Qt.EditRole → Qt.ItemDataRole.EditRole
- [ ] Qt.KeepAspectRatio → Qt.AspectRatioMode.KeepAspectRatio
- [ ] Qt.IgnoreAspectRatio → Qt.AspectRatioMode.IgnoreAspectRatio
- [ ] Qt.SmoothTransformation → Qt.TransformationMode.SmoothTransformation
- [ ] Qt.FastTransformation → Qt.TransformationMode.FastTransformation
- [ ] Qt.Dialog → Qt.WindowType.Dialog
- [ ] Qt.WindowTitleHint → Qt.WindowType.WindowTitleHint
- [ ] Qt.WindowCloseButtonHint → Qt.WindowType.WindowCloseButtonHint
- [ ] Qt.Horizontal → Qt.Orientation.Horizontal
- [ ] Qt.Vertical → Qt.Orientation.Vertical
- [ ] Qt.AlignLeft → Qt.AlignmentFlag.AlignLeft
- [ ] Qt.AlignRight → Qt.AlignmentFlag.AlignRight
- [ ] Qt.AlignCenter → Qt.AlignmentFlag.AlignCenter
- [ ] Qt.AlignTop → Qt.AlignmentFlag.AlignTop
- [ ] Qt.AlignBottom → Qt.AlignmentFlag.AlignBottom
- [ ] Qt.LeftButton → Qt.MouseButton.LeftButton
- [ ] Qt.RightButton → Qt.MouseButton.RightButton
- [ ] Qt.MiddleButton → Qt.MouseButton.MiddleButton
- [ ] Qt.NoModifier → Qt.KeyboardModifier.NoModifier
- [ ] Qt.ShiftModifier → Qt.KeyboardModifier.ShiftModifier
- [ ] Qt.ControlModifier → Qt.KeyboardModifier.ControlModifier
- [ ] Qt.AltModifier → Qt.KeyboardModifier.AltModifier
- [ ] Qt.MetaModifier → Qt.KeyboardModifier.MetaModifier

### 2. QAction移動
- [ ] QtWidgets.QAction → QtGui.QAction

### 3. exec_() → exec()
- [ ] dialog.exec_() → dialog.exec()
- [ ] app.exec_() → app.exec()

### 4. QFont.Bold → QFont.Weight.Bold
- [ ] QFont.Bold → QFont.Weight.Bold
- [ ] QFont.Normal → QFont.Weight.Normal
- [ ] QFont.Light → QFont.Weight.Light

### 5. StandardButton変更
- [ ] QMessageBox.Yes → QMessageBox.StandardButton.Yes
- [ ] QMessageBox.No → QMessageBox.StandardButton.No
- [ ] QMessageBox.Ok → QMessageBox.StandardButton.Ok
- [ ] QMessageBox.Cancel → QMessageBox.StandardButton.Cancel

### 6. EchoMode変更
- [ ] QLineEdit.Password → QLineEdit.EchoMode.Password
- [ ] QLineEdit.Normal → QLineEdit.EchoMode.Normal

### 7. SP_アイコン変更
- [ ] style().SP_DirIcon → style().standardIcon(style().SP_DirIcon)
- [ ] style().SP_FileIcon → style().standardIcon(style().SP_FileIcon)

## 検査対象ファイル

### gui/
- [ ] main_window_qt6.py
- [ ] repository_settings_dialog.py
- [ ] components/input_panel_qt6.py
- [ ] components/log_panel_qt6.py
- [ ] components/progress_bar_qt6.py
- [ ] dialogs/folder_selector_dialog.py
- [ ] dialogs/simple_file_selector_dialog.py
- [ ] dialogs/process_mode_dialog.py
- [ ] dialogs/warning_dialog.py
- [ ] dialogs/simple_warning_dialog.py

### core/
- [ ] workflow_processor.py (PyQt6シグナル使用箇所)
- [ ] api_processor.py (PyQt6シグナル使用箇所)