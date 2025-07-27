#!/usr/bin/env python3
"""
PyQt5からPyQt6への包括的な移行修正スクリプト
すべての既知のAPI変更を自動的に修正します
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Qt6で変更されたEnum名前空間のマッピング
ENUM_MAPPINGS = [
    # ItemDataRole
    (r'\bQt\.UserRole\b', 'Qt.ItemDataRole.UserRole'),
    (r'\bQt\.DisplayRole\b', 'Qt.ItemDataRole.DisplayRole'),
    (r'\bQt\.EditRole\b', 'Qt.ItemDataRole.EditRole'),
    (r'\bQt\.DecorationRole\b', 'Qt.ItemDataRole.DecorationRole'),
    (r'\bQt\.ToolTipRole\b', 'Qt.ItemDataRole.ToolTipRole'),
    (r'\bQt\.StatusTipRole\b', 'Qt.ItemDataRole.StatusTipRole'),
    (r'\bQt\.WhatsThisRole\b', 'Qt.ItemDataRole.WhatsThisRole'),
    
    # AspectRatioMode
    (r'\bQt\.KeepAspectRatio\b', 'Qt.AspectRatioMode.KeepAspectRatio'),
    (r'\bQt\.IgnoreAspectRatio\b', 'Qt.AspectRatioMode.IgnoreAspectRatio'),
    (r'\bQt\.KeepAspectRatioByExpanding\b', 'Qt.AspectRatioMode.KeepAspectRatioByExpanding'),
    
    # TransformationMode
    (r'\bQt\.SmoothTransformation\b', 'Qt.TransformationMode.SmoothTransformation'),
    (r'\bQt\.FastTransformation\b', 'Qt.TransformationMode.FastTransformation'),
    
    # WindowType
    (r'\bQt\.Dialog\b', 'Qt.WindowType.Dialog'),
    (r'\bQt\.Window\b', 'Qt.WindowType.Window'),
    (r'\bQt\.Popup\b', 'Qt.WindowType.Popup'),
    (r'\bQt\.Tool\b', 'Qt.WindowType.Tool'),
    (r'\bQt\.ToolTip\b', 'Qt.WindowType.ToolTip'),
    (r'\bQt\.SplashScreen\b', 'Qt.WindowType.SplashScreen'),
    (r'\bQt\.Desktop\b', 'Qt.WindowType.Desktop'),
    (r'\bQt\.SubWindow\b', 'Qt.WindowType.SubWindow'),
    (r'\bQt\.WindowTitleHint\b', 'Qt.WindowType.WindowTitleHint'),
    (r'\bQt\.WindowSystemMenuHint\b', 'Qt.WindowType.WindowSystemMenuHint'),
    (r'\bQt\.WindowMinimizeButtonHint\b', 'Qt.WindowType.WindowMinimizeButtonHint'),
    (r'\bQt\.WindowMaximizeButtonHint\b', 'Qt.WindowType.WindowMaximizeButtonHint'),
    (r'\bQt\.WindowCloseButtonHint\b', 'Qt.WindowType.WindowCloseButtonHint'),
    (r'\bQt\.WindowContextHelpButtonHint\b', 'Qt.WindowType.WindowContextHelpButtonHint'),
    (r'\bQt\.WindowShadeButtonHint\b', 'Qt.WindowType.WindowShadeButtonHint'),
    (r'\bQt\.WindowStaysOnTopHint\b', 'Qt.WindowType.WindowStaysOnTopHint'),
    (r'\bQt\.CustomizeWindowHint\b', 'Qt.WindowType.CustomizeWindowHint'),
    
    # Orientation
    (r'\bQt\.Horizontal\b', 'Qt.Orientation.Horizontal'),
    (r'\bQt\.Vertical\b', 'Qt.Orientation.Vertical'),
    
    # AlignmentFlag
    (r'\bQt\.AlignLeft\b', 'Qt.AlignmentFlag.AlignLeft'),
    (r'\bQt\.AlignRight\b', 'Qt.AlignmentFlag.AlignRight'),
    (r'\bQt\.AlignHCenter\b', 'Qt.AlignmentFlag.AlignHCenter'),
    (r'\bQt\.AlignJustify\b', 'Qt.AlignmentFlag.AlignJustify'),
    (r'\bQt\.AlignTop\b', 'Qt.AlignmentFlag.AlignTop'),
    (r'\bQt\.AlignBottom\b', 'Qt.AlignmentFlag.AlignBottom'),
    (r'\bQt\.AlignVCenter\b', 'Qt.AlignmentFlag.AlignVCenter'),
    (r'\bQt\.AlignCenter\b', 'Qt.AlignmentFlag.AlignCenter'),
    (r'\bQt\.AlignBaseline\b', 'Qt.AlignmentFlag.AlignBaseline'),
    
    # MouseButton
    (r'\bQt\.LeftButton\b', 'Qt.MouseButton.LeftButton'),
    (r'\bQt\.RightButton\b', 'Qt.MouseButton.RightButton'),
    (r'\bQt\.MiddleButton\b', 'Qt.MouseButton.MiddleButton'),
    (r'\bQt\.BackButton\b', 'Qt.MouseButton.BackButton'),
    (r'\bQt\.ForwardButton\b', 'Qt.MouseButton.ForwardButton'),
    (r'\bQt\.NoButton\b', 'Qt.MouseButton.NoButton'),
    
    # KeyboardModifier
    (r'\bQt\.NoModifier\b', 'Qt.KeyboardModifier.NoModifier'),
    (r'\bQt\.ShiftModifier\b', 'Qt.KeyboardModifier.ShiftModifier'),
    (r'\bQt\.ControlModifier\b', 'Qt.KeyboardModifier.ControlModifier'),
    (r'\bQt\.AltModifier\b', 'Qt.KeyboardModifier.AltModifier'),
    (r'\bQt\.MetaModifier\b', 'Qt.KeyboardModifier.MetaModifier'),
    (r'\bQt\.KeypadModifier\b', 'Qt.KeyboardModifier.KeypadModifier'),
    
    # Key
    (r'\bQt\.Key_([A-Za-z0-9_]+)\b', r'Qt.Key.Key_\1'),
    
    # CheckState
    (r'\bQt\.Unchecked\b', 'Qt.CheckState.Unchecked'),
    (r'\bQt\.PartiallyChecked\b', 'Qt.CheckState.PartiallyChecked'),
    (r'\bQt\.Checked\b', 'Qt.CheckState.Checked'),
    
    # TextInteractionFlag
    (r'\bQt\.NoTextInteraction\b', 'Qt.TextInteractionFlag.NoTextInteraction'),
    (r'\bQt\.TextSelectableByMouse\b', 'Qt.TextInteractionFlag.TextSelectableByMouse'),
    (r'\bQt\.TextSelectableByKeyboard\b', 'Qt.TextInteractionFlag.TextSelectableByKeyboard'),
    (r'\bQt\.LinksAccessibleByMouse\b', 'Qt.TextInteractionFlag.LinksAccessibleByMouse'),
    (r'\bQt\.LinksAccessibleByKeyboard\b', 'Qt.TextInteractionFlag.LinksAccessibleByKeyboard'),
    (r'\bQt\.TextEditable\b', 'Qt.TextInteractionFlag.TextEditable'),
    (r'\bQt\.TextEditorInteraction\b', 'Qt.TextInteractionFlag.TextEditorInteraction'),
    (r'\bQt\.TextBrowserInteraction\b', 'Qt.TextInteractionFlag.TextBrowserInteraction'),
    
    # FocusPolicy
    (r'\bQt\.NoFocus\b', 'Qt.FocusPolicy.NoFocus'),
    (r'\bQt\.TabFocus\b', 'Qt.FocusPolicy.TabFocus'),
    (r'\bQt\.ClickFocus\b', 'Qt.FocusPolicy.ClickFocus'),
    (r'\bQt\.StrongFocus\b', 'Qt.FocusPolicy.StrongFocus'),
    (r'\bQt\.WheelFocus\b', 'Qt.FocusPolicy.WheelFocus'),
]

# QStyle StandardPixmap
QSTYLE_MAPPINGS = [
    # スタイルのアイコン - standardIcon()メソッド内での使用
    (r'\.standardIcon\(self\.style\(\)\.SP_([A-Za-z]+)\)', r'.standardIcon(QStyle.StandardPixmap.SP_\1)'),
    (r'\.standardIcon\(style\(\)\.SP_([A-Za-z]+)\)', r'.standardIcon(QStyle.StandardPixmap.SP_\1)'),
    # その他の場所での使用
    (r'self\.style\(\)\.SP_([A-Za-z]+)', r'QStyle.StandardPixmap.SP_\1'),
    (r'style\(\)\.SP_([A-Za-z]+)', r'QStyle.StandardPixmap.SP_\1'),
]

# その他の変更
OTHER_MAPPINGS = [
    # exec_() -> exec()
    (r'\.exec_\(\)', '.exec()'),
    
    # QFont weight
    (r'\bQFont\.Bold\b', 'QFont.Weight.Bold'),
    (r'\bQFont\.Normal\b', 'QFont.Weight.Normal'),
    (r'\bQFont\.Light\b', 'QFont.Weight.Light'),
    (r'\bQFont\.DemiBold\b', 'QFont.Weight.DemiBold'),
    (r'\bQFont\.Black\b', 'QFont.Weight.Black'),
    (r'\bQFont\.Thin\b', 'QFont.Weight.Thin'),
    
    # QMessageBox StandardButton
    (r'\bQMessageBox\.Yes\b', 'QMessageBox.StandardButton.Yes'),
    (r'\bQMessageBox\.No\b', 'QMessageBox.StandardButton.No'),
    (r'\bQMessageBox\.Ok\b', 'QMessageBox.StandardButton.Ok'),
    (r'\bQMessageBox\.Cancel\b', 'QMessageBox.StandardButton.Cancel'),
    (r'\bQMessageBox\.Close\b', 'QMessageBox.StandardButton.Close'),
    (r'\bQMessageBox\.Save\b', 'QMessageBox.StandardButton.Save'),
    (r'\bQMessageBox\.SaveAll\b', 'QMessageBox.StandardButton.SaveAll'),
    (r'\bQMessageBox\.Open\b', 'QMessageBox.StandardButton.Open'),
    (r'\bQMessageBox\.Reset\b', 'QMessageBox.StandardButton.Reset'),
    (r'\bQMessageBox\.RestoreDefaults\b', 'QMessageBox.StandardButton.RestoreDefaults'),
    (r'\bQMessageBox\.Abort\b', 'QMessageBox.StandardButton.Abort'),
    (r'\bQMessageBox\.Retry\b', 'QMessageBox.StandardButton.Retry'),
    (r'\bQMessageBox\.Ignore\b', 'QMessageBox.StandardButton.Ignore'),
    
    # QLineEdit EchoMode
    (r'\bQLineEdit\.Normal\b', 'QLineEdit.EchoMode.Normal'),
    (r'\bQLineEdit\.NoEcho\b', 'QLineEdit.EchoMode.NoEcho'),
    (r'\bQLineEdit\.Password\b', 'QLineEdit.EchoMode.Password'),
    (r'\bQLineEdit\.PasswordEchoOnEdit\b', 'QLineEdit.EchoMode.PasswordEchoOnEdit'),
]

# インポート文の修正
IMPORT_MAPPINGS = [
    (r'from PyQt6\.QtWidgets import ([^,\n]*,\s*)*QAction', 
     lambda m: m.group(0).replace('from PyQt6.QtWidgets', 'from PyQt6.QtGui')),
]

# QStyleインポートの追加
def ensure_qstyle_import(content):
    """QStyle.StandardPixmapを使用している場合、QStyleのインポートを確認"""
    if 'QStyle.StandardPixmap' in content and 'from PyQt6.QtWidgets import' in content:
        # QStyleがインポートされているか確認
        import_line_match = re.search(r'from PyQt6\.QtWidgets import\s*\((.*?)\)', content, re.DOTALL)
        if import_line_match:
            imports = import_line_match.group(1)
            if 'QStyle' not in imports:
                # 複数行のインポートの場合
                content = re.sub(
                    r'(from PyQt6\.QtWidgets import\s*\([^)]+)',
                    lambda m: m.group(1).rstrip() + ', QStyle',
                    content
                )
        else:
            # 単一行のインポートの場合
            import_line_match = re.search(r'from PyQt6\.QtWidgets import\s+([^\n]+)', content)
            if import_line_match and 'QStyle' not in import_line_match.group(1):
                content = re.sub(
                    r'(from PyQt6\.QtWidgets import\s+[^\n]+)',
                    lambda m: m.group(1) + ', QStyle',
                    content
                )
    return content


def fix_file(file_path: Path) -> List[str]:
    """単一ファイルのQt6移行修正を実行"""
    changes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Enum名前空間の修正
        for pattern, replacement in ENUM_MAPPINGS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                matches = re.findall(pattern, content)
                for match in matches:
                    changes.append(f"  - {match} → {replacement}")
                content = new_content
        
        # QStyle StandardPixmapの修正
        for pattern, replacement in QSTYLE_MAPPINGS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        # グループがある場合
                        changes.append(f"  - SP_{match[0]} → QStyle.StandardPixmap.SP_{match[0]}")
                    else:
                        changes.append(f"  - SP_{match} → QStyle.StandardPixmap.SP_{match}")
                content = new_content
        
        # その他の修正
        for pattern, replacement in OTHER_MAPPINGS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                matches = re.findall(pattern, content)
                for match in matches:
                    changes.append(f"  - {match} → {replacement}")
                content = new_content
        
        # インポート文の修正
        for pattern, replacement in IMPORT_MAPPINGS:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes.append(f"  - QAction import moved from QtWidgets to QtGui")
                content = new_content
        
        # QStyleインポートの確認と追加
        content = ensure_qstyle_import(content)
        
        # 変更がある場合はファイルを更新
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
    except Exception as e:
        changes.append(f"  ! Error: {e}")
    
    return changes


def main():
    """メイン処理"""
    print("PyQt5 → PyQt6 包括的移行修正スクリプト")
    print("=" * 50)
    
    # 対象ディレクトリ
    base_dir = Path(__file__).parent
    gui_dir = base_dir / "gui"
    core_dir = base_dir / "core"
    
    # 対象ファイルの収集
    target_files = []
    
    # GUIファイル
    for pattern in ["*.py", "**/*.py"]:
        target_files.extend(gui_dir.glob(pattern))
    
    # CoreファイルでQtを使用するもの
    core_files = ["workflow_processor.py", "api_processor.py"]
    for file_name in core_files:
        file_path = core_dir / file_name
        if file_path.exists():
            target_files.append(file_path)
    
    # バックアップディレクトリは除外
    target_files = [f for f in target_files if "backup" not in str(f)]
    
    total_changes = 0
    
    for file_path in sorted(set(target_files)):
        print(f"\n処理中: {file_path.relative_to(base_dir)}")
        changes = fix_file(file_path)
        
        if changes:
            print(f"  修正箇所: {len(changes)}件")
            for change in changes[:5]:  # 最初の5件のみ表示
                print(change)
            if len(changes) > 5:
                print(f"  ... 他 {len(changes) - 5} 件")
            total_changes += len(changes)
        else:
            print("  修正なし")
    
    print(f"\n完了: 合計 {total_changes} 箇所を修正しました")
    
    if total_changes > 0:
        print("\n⚠️  重要: 修正後は必ず動作確認を行ってください")
        print("実行: .\\run_qt6_windows.ps1")


if __name__ == "__main__":
    main()