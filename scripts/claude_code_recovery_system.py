#!/usr/bin/env python3
"""
Claude Code認証エラー復旧システム
認証エラー時の完全復旧（設定削除→再認証→バックアップ復元）
"""

import os
import sys
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import tempfile

from claude_code_backup_system import ClaudeCodeBackupSystem

class ClaudeCodeRecoverySystem:
    """Claude Code認証エラー完全復旧システム"""
    
    def __init__(self):
        self.backup_system = ClaudeCodeBackupSystem()
        self.claude_config_dir = Path.home() / ".config" / "claude"
        
    def diagnose_auth_issue(self) -> Dict:
        """認証問題の診断を実行"""
        print("🔍 Claude Code認証状況診断中...")
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "config_exists": self.claude_config_dir.exists(),
            "config_files": {},
            "mcp_status": None,
            "claude_command_works": False,
            "auth_error_detected": False
        }
        
        # 設定ファイルの存在確認
        config_files = ["mcp_servers.json", "settings.json", "auth.json"]
        for config_file in config_files:
            config_path = self.claude_config_dir / config_file
            diagnosis["config_files"][config_file] = {
                "exists": config_path.exists(),
                "size": config_path.stat().st_size if config_path.exists() else 0,
                "modified": config_path.stat().st_mtime if config_path.exists() else None
            }
        
        # Claude コマンドの動作確認
        try:
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            diagnosis["claude_command_works"] = result.returncode == 0
            if result.returncode == 0:
                diagnosis["claude_version"] = result.stdout.strip()
        except Exception as e:
            diagnosis["claude_command_error"] = str(e)
        
        # MCP設定状況確認
        try:
            result = subprocess.run(
                ["claude", "mcp", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            diagnosis["mcp_status"] = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # 認証エラー検出
            if "authentication_error" in result.stderr or "OAuth token has expired" in result.stderr:
                diagnosis["auth_error_detected"] = True
                
        except Exception as e:
            diagnosis["mcp_error"] = str(e)
        
        return diagnosis
    
    def clean_claude_config(self) -> bool:
        """Claude設定の完全クリーンアップ"""
        print("🧹 Claude Code設定の完全クリーンアップ実行中...")
        
        if not self.claude_config_dir.exists():
            print("  ✅ 設定ディレクトリは既に存在しません")
            return True
        
        # 現在の設定を緊急バックアップ
        emergency_backup = Path("/mnt/c/Users/tky99/dev/.claude_code_backups") / f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        try:
            self.backup_system._backup_current_config(emergency_backup)
            print(f"  🔄 緊急バックアップ作成: {emergency_backup}")
        except Exception as e:
            print(f"  ⚠️  緊急バックアップ失敗: {e}")
        
        # 設定ディレクトリ完全削除
        try:
            shutil.rmtree(self.claude_config_dir)
            print(f"  ✅ 設定ディレクトリ削除完了: {self.claude_config_dir}")
            return True
        except Exception as e:
            print(f"  ❌ 設定削除エラー: {e}")
            return False
    
    def wait_for_authentication(self, timeout: int = 300) -> bool:
        """
        ユーザーの再認証完了を待機
        
        Args:
            timeout: タイムアウト時間（秒）
            
        Returns:
            認証成功かどうか
        """
        print("🔐 Claude Code再認証の完了を待機中...")
        print("     ブラウザでClaude Codeに再ログインしてください")
        print("     認証完了後、任意のキーを押してください")
        
        start_time = time.time()
        
        # ユーザー入力待ち
        try:
            input("認証完了後、Enterキーを押してください: ")
        except KeyboardInterrupt:
            print("\n認証待機をキャンセルしました")
            return False
        
        # 認証確認
        print("🔍 認証状況確認中...")
        for attempt in range(3):
            try:
                result = subprocess.run(
                    ["claude", "mcp", "list"], 
                    capture_output=True, 
                    text=True, 
                    timeout=15
                )
                
                if result.returncode == 0:
                    print("  ✅ 認証確認完了")
                    return True
                elif "authentication_error" in result.stderr:
                    print(f"  ⚠️  認証エラーが継続中 (試行 {attempt + 1}/3)")
                    time.sleep(5)
                else:
                    print(f"  ⚠️  予期しないエラー: {result.stderr}")
                    
            except Exception as e:
                print(f"  ⚠️  認証確認エラー: {e}")
            
            if attempt < 2:
                print("    5秒後に再試行...")
                time.sleep(5)
        
        print("❌ 認証確認に失敗しました")
        return False
    
    def full_recovery(self, backup_file: Optional[str] = None) -> bool:
        """
        完全復旧プロセス実行
        
        Args:
            backup_file: 使用するバックアップファイル
            
        Returns:
            復旧成功かどうか
        """
        print("🚨 Claude Code完全復旧プロセス開始")
        print("=" * 60)
        
        # Step 1: 診断
        print("\n📋 Step 1: 問題診断")
        diagnosis = self.diagnose_auth_issue()
        print(f"  設定ディレクトリ: {'存在' if diagnosis['config_exists'] else '不存在'}")
        print(f"  Claudeコマンド: {'動作' if diagnosis['claude_command_works'] else '不動作'}")
        print(f"  認証エラー: {'検出' if diagnosis['auth_error_detected'] else '未検出'}")
        
        # Step 2: バックアップ確認
        print("\n📦 Step 2: バックアップ確認")
        backups = self.backup_system.list_backups()
        if not backups:
            print("❌ 利用可能なバックアップがありません")
            print("    復旧には手動設定が必要です")
            return False
        
        if backup_file is None:
            backup_file = backups[0]["file"]
            print(f"  最新バックアップを使用: {backups[0]['name']}")
        else:
            print(f"  指定バックアップを使用: {backup_file}")
        
        # Step 3: 設定クリーンアップ
        print("\n🧹 Step 3: 設定クリーンアップ")
        if diagnosis["config_exists"]:
            if not self.clean_claude_config():
                print("❌ 設定クリーンアップに失敗しました")
                return False
        else:
            print("  ✅ 設定は既にクリーンです")
        
        # Step 4: 再認証待機
        print("\n🔐 Step 4: 再認証")
        print("  次の手順で再認証してください:")
        print("  1. ブラウザでhttps://claude.ai/codeにアクセス")
        print("  2. ログインしてClaude Codeを認証")
        print("  3. 必要に応じて再度認証プロセスを実行")
        
        if not self.wait_for_authentication():
            print("❌ 再認証に失敗しました")
            return False
        
        # Step 5: バックアップ復元
        print("\n🔄 Step 5: バックアップ復元")
        if not self.backup_system.restore_from_backup(backup_file):
            print("❌ バックアップ復元に失敗しました")
            return False
        
        # Step 6: 最終確認
        print("\n✅ Step 6: 復旧確認")
        final_diagnosis = self.diagnose_auth_issue()
        
        success = (
            final_diagnosis["claude_command_works"] and 
            not final_diagnosis["auth_error_detected"]
        )
        
        if success:
            print("🎉 Claude Code完全復旧成功！")
            print("=" * 60)
            
            # MCP設定状況表示
            try:
                result = subprocess.run(
                    ["claude", "mcp", "list"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    print("📋 復元されたMCP設定:")
                    print(result.stdout)
            except Exception:
                pass
                
        else:
            print("❌ 復旧に問題があります")
            print("    手動での設定確認が必要です")
        
        return success
    
    def quick_recovery(self) -> bool:
        """
        クイック復旧（認証OKの場合のバックアップ復元のみ）
        """
        print("⚡ Claude Codeクイック復旧開始")
        
        # 認証状況確認
        diagnosis = self.diagnose_auth_issue()
        if diagnosis["auth_error_detected"]:
            print("❌ 認証エラーが検出されました")
            print("    full-recoveryを使用してください")
            return False
        
        if not diagnosis["claude_command_works"]:
            print("❌ Claudeコマンドが動作しません")
            return False
        
        # 最新バックアップから復元
        return self.backup_system.restore_from_backup()


def main():
    """メインエントリーポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code認証エラー復旧システム")
    parser.add_argument("action", choices=["diagnose", "clean", "full-recovery", "quick-recovery"], 
                       help="実行するアクション")
    parser.add_argument("--backup-file", help="使用するバックアップファイル")
    parser.add_argument("--timeout", type=int, default=300, help="認証待機タイムアウト（秒）")
    
    args = parser.parse_args()
    
    recovery_system = ClaudeCodeRecoverySystem()
    
    if args.action == "diagnose":
        # 診断のみ
        diagnosis = recovery_system.diagnose_auth_issue()
        print(json.dumps(diagnosis, indent=2, default=str, ensure_ascii=False))
        
    elif args.action == "clean":
        # 設定クリーンアップのみ
        success = recovery_system.clean_claude_config()
        sys.exit(0 if success else 1)
        
    elif args.action == "full-recovery":
        # 完全復旧
        success = recovery_system.full_recovery(args.backup_file)
        sys.exit(0 if success else 1)
        
    elif args.action == "quick-recovery":
        # クイック復旧
        success = recovery_system.quick_recovery()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()