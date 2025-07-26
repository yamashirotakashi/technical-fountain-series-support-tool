#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Qt6移行状況チェックスクリプト"""
import os
import re
from pathlib import Path

def check_python_file(file_path):
    """Pythonファイルの移行状況をチェック"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        # PyQt5の残存チェック
        if 'PyQt5' in content:
            for i, line in enumerate(lines, 1):
                if 'PyQt5' in line and not line.strip().startswith('#'):
                    issues.append(f"Line {i}: PyQt5が残っています: {line.strip()}")
        
        # QActionのインポート位置チェック
        if 'from PyQt6.QtWidgets import' in content and 'QAction' in content:
            for i, line in enumerate(lines, 1):
                if 'from PyQt6.QtWidgets import' in line and 'QAction' in line:
                    issues.append(f"Line {i}: QActionはQtGuiからインポートする必要があります")
        
        # exec_()の使用チェック
        if '.exec_()' in content:
            for i, line in enumerate(lines, 1):
                if '.exec_()' in line and not line.strip().startswith('#'):
                    issues.append(f"Line {i}: exec_()はexec()に変更する必要があります")
        
        # High DPI属性チェック
        if 'Qt.AA_EnableHighDpiScaling' in content or 'Qt.AA_UseHighDpiPixmaps' in content:
            for i, line in enumerate(lines, 1):
                if ('Qt.AA_EnableHighDpiScaling' in line or 'Qt.AA_UseHighDpiPixmaps' in line) and not line.strip().startswith('#'):
                    issues.append(f"Line {i}: Qt6では自動的に有効なので削除が必要です")
        
    except Exception as e:
        issues.append(f"ファイル読み込みエラー: {e}")
    
    return issues

def main():
    """メイン処理"""
    print("Qt6移行状況チェックを開始します...\n")
    
    # チェック対象ディレクトリ
    target_dirs = ['gui', 'core', 'utils']
    
    all_issues = {}
    total_files = 0
    files_with_issues = 0
    
    for target_dir in target_dirs:
        if not os.path.exists(target_dir):
            continue
            
        for root, dirs, files in os.walk(target_dir):
            # 仮想環境とキャッシュを除外
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', 'test_venv', 'venv_windows']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    total_files += 1
                    
                    issues = check_python_file(file_path)
                    if issues:
                        all_issues[file_path] = issues
                        files_with_issues += 1
    
    # 結果を表示
    if all_issues:
        print(f"❌ {files_with_issues}個のファイルに問題が見つかりました:\n")
        
        for file_path, issues in all_issues.items():
            print(f"📄 {file_path}")
            for issue in issues:
                print(f"   - {issue}")
            print()
    else:
        print(f"✅ すべてのファイル（{total_files}個）がQt6に正しく移行されています！")
    
    # サマリー
    print("\n--- サマリー ---")
    print(f"チェックしたファイル数: {total_files}")
    print(f"問題のあるファイル数: {files_with_issues}")
    print(f"成功率: {((total_files - files_with_issues) / total_files * 100):.1f}%")

if __name__ == "__main__":
    main()