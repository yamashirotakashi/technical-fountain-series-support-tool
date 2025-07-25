#!/usr/bin/env python3
"""
Qt6移行の完全性を検証するスクリプト
潜在的な問題を事前に検出します
"""

import re
import ast
from pathlib import Path
from typing import List, Dict, Set

class Qt6MigrationVerifier(ast.NodeVisitor):
    """ASTを使用してQt6移行の問題を検出"""
    
    def __init__(self):
        self.issues = []
        self.imports = set()
        self.qt_usage = []
        
    def visit_ImportFrom(self, node):
        """import文を記録"""
        if node.module and 'PyQt6' in node.module:
            for alias in node.names:
                self.imports.add((node.module, alias.name))
        self.generic_visit(node)
        
    def visit_Attribute(self, node):
        """Qt列挙型の使用を検出"""
        if isinstance(node.value, ast.Name) and node.value.id == 'Qt':
            # Qt.Something の形式
            attr_name = node.attr
            self.qt_usage.append((node.lineno, f"Qt.{attr_name}"))
        self.generic_visit(node)


def check_file_syntax(file_path: Path) -> List[str]:
    """ファイルの構文を解析してQt6移行の問題を検出"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # AST解析
        tree = ast.parse(content)
        verifier = Qt6MigrationVerifier()
        verifier.visit(tree)
        
        # PyQt6でのQAction import位置チェック
        for module, name in verifier.imports:
            if name == 'QAction' and module == 'PyQt6.QtWidgets':
                issues.append(f"Line import: QAction should be imported from PyQt6.QtGui, not QtWidgets")
        
        # Qt列挙型の使用チェック
        known_enums = {
            'UserRole', 'DisplayRole', 'EditRole', 'DecorationRole',
            'KeepAspectRatio', 'IgnoreAspectRatio',
            'SmoothTransformation', 'FastTransformation',
            'Dialog', 'Window', 'Popup',
            'Horizontal', 'Vertical',
            'AlignLeft', 'AlignRight', 'AlignCenter',
            'LeftButton', 'RightButton', 'MiddleButton',
            'NoModifier', 'ShiftModifier', 'ControlModifier',
            'Checked', 'Unchecked',
            'WindowTitleHint', 'WindowCloseButtonHint'
        }
        
        for line_no, usage in verifier.qt_usage:
            enum_name = usage.split('.')[1]
            if enum_name in known_enums:
                issues.append(f"Line {line_no}: {usage} - Missing namespace in Qt6")
        
        # exec_() パターンの検出
        exec_pattern = re.compile(r'\.exec_\(\)')
        for i, line in enumerate(content.split('\n'), 1):
            if exec_pattern.search(line):
                issues.append(f"Line {i}: exec_() should be exec() in Qt6")
        
        # QFont.Bold パターンの検出
        font_pattern = re.compile(r'QFont\.(Bold|Normal|Light|DemiBold|Black|Thin)\b')
        for i, line in enumerate(content.split('\n'), 1):
            match = font_pattern.search(line)
            if match:
                issues.append(f"Line {i}: QFont.{match.group(1)} should be QFont.Weight.{match.group(1)}")
        
        # QMessageBox.Yes/No パターンの検出
        msgbox_pattern = re.compile(r'QMessageBox\.(Yes|No|Ok|Cancel|Close|Save|Open|Abort|Retry|Ignore)\b')
        for i, line in enumerate(content.split('\n'), 1):
            match = msgbox_pattern.search(line)
            if match:
                issues.append(f"Line {i}: QMessageBox.{match.group(1)} should be QMessageBox.StandardButton.{match.group(1)}")
        
        # QLineEdit.Password パターンの検出
        lineedit_pattern = re.compile(r'QLineEdit\.(Normal|NoEcho|Password|PasswordEchoOnEdit)\b')
        for i, line in enumerate(content.split('\n'), 1):
            match = lineedit_pattern.search(line)
            if match:
                issues.append(f"Line {i}: QLineEdit.{match.group(1)} should be QLineEdit.EchoMode.{match.group(1)}")
                
    except SyntaxError as e:
        issues.append(f"Syntax Error: {e}")
    except Exception as e:
        issues.append(f"Error: {e}")
    
    return issues


def verify_imports(file_path: Path) -> List[str]:
    """インポートの正確性を検証"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # QActionが正しくインポートされているか
        if 'QAction' in content:
            if 'from PyQt6.QtWidgets import' in content and 'QAction' in content:
                # QtWidgetsからQActionをインポートしているか確認
                import_line = None
                for line in content.split('\n'):
                    if 'from PyQt6.QtWidgets import' in line and 'QAction' in line:
                        import_line = line
                        break
                if import_line:
                    issues.append(f"Import issue: {import_line.strip()} - QAction should be from PyQt6.QtGui")
        
    except Exception as e:
        issues.append(f"Import verification error: {e}")
    
    return issues


def main():
    """メイン処理"""
    print("Qt6移行検証スクリプト")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    gui_dir = base_dir / "gui"
    core_dir = base_dir / "core"
    
    # 対象ファイル
    target_files = []
    for pattern in ["*.py", "**/*.py"]:
        target_files.extend(gui_dir.glob(pattern))
    
    # Coreファイル
    core_files = ["workflow_processor.py", "api_processor.py"]
    for file_name in core_files:
        file_path = core_dir / file_name
        if file_path.exists():
            target_files.append(file_path)
    
    # バックアップ除外
    target_files = [f for f in target_files if "backup" not in str(f)]
    
    total_issues = 0
    file_issues = {}
    
    for file_path in sorted(set(target_files)):
        issues = []
        
        # 構文チェック
        syntax_issues = check_file_syntax(file_path)
        issues.extend(syntax_issues)
        
        # インポートチェック
        import_issues = verify_imports(file_path)
        issues.extend(import_issues)
        
        if issues:
            file_issues[file_path] = issues
            total_issues += len(issues)
    
    # 結果表示
    if file_issues:
        print(f"\n🚨 検出された問題: {total_issues}件\n")
        
        for file_path, issues in file_issues.items():
            print(f"\n📄 {file_path.relative_to(base_dir)}")
            for issue in issues:
                print(f"   ⚠️  {issue}")
    else:
        print("\n✅ すべてのファイルがQt6に正しく移行されています")
    
    # 推奨事項
    print("\n📋 推奨される次のステップ:")
    print("1. 検出された問題を修正")
    print("2. 各コンポーネントの個別テスト")
    print("3. 統合テストの実行")
    print("4. exe化前の最終確認")


if __name__ == "__main__":
    main()