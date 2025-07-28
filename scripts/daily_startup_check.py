#!/usr/bin/env python3
"""
Claude Code日次起動チェック・自動バックアップスクリプト
初回起動時の自動実行用エントリーポイント
"""

import sys
import os
from pathlib import Path

# スクリプトディレクトリをパスに追加
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from claude_code_backup_system import ClaudeCodeBackupSystem

def daily_startup_check():
    """日次起動チェック・バックアップ"""
    print("🚀 Claude Code日次起動チェック開始")
    print("=" * 50)
    
    backup_system = ClaudeCodeBackupSystem()
    
    # バックアップ実行
    backup_executed = backup_system.startup_check_and_backup()
    
    if backup_executed:
        print("\n✅ 起動時バックアップ完了")
        
        # バックアップ一覧表示
        backups = backup_system.list_backups()
        if len(backups) > 1:
            print(f"\n📋 利用可能なバックアップ: {len(backups)}個")
            for i, backup in enumerate(backups[:3]):  # 最新3個まで表示
                print(f"  {i+1}. {backup['name']} ({backup['created']})")
            if len(backups) > 3:
                print(f"     ... 他{len(backups)-3}個")
    else:
        print("\n✅ バックアップは最新です")
    
    print("\n" + "=" * 50)
    print("💡 認証エラー時の復旧方法:")
    print("   python scripts/claude_code_recovery_system.py full-recovery")
    print("💡 手動バックアップ:")
    print("   ［バックアップ］コマンドまたは")
    print("   python scripts/claude_code_backup_system.py backup")
    print("=" * 50)

if __name__ == "__main__":
    daily_startup_check()