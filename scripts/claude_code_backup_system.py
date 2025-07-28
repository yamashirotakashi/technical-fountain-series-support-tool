#!/usr/bin/env python3
"""
Claude Code認証エラー対策 - 自動バックアップ・復旧システム
初回起動時の自動バックアップと認証エラー時の復旧機能
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import zipfile
import tempfile

class ClaudeCodeBackupSystem:
    """Claude Code設定の自動バックアップ・復旧システム"""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.claude_config_dir = self.home_dir / ".config" / "claude"
        self.backup_base_dir = Path("/mnt/c/Users/tky99/dev/.claude_code_backups")
        self.backup_base_dir.mkdir(parents=True, exist_ok=True)
        
        # バックアップ対象ファイル・ディレクトリ
        self.backup_targets = {
            "mcp_config": self.claude_config_dir / "mcp_servers.json",
            "claude_settings": self.claude_config_dir / "settings.json",
            "auth_config": self.claude_config_dir / "auth.json",
            "session_data": self.claude_config_dir / "sessions",
            "user_data": self.claude_config_dir / "user_data"
        }
        
        # CLAUDE.mdファイル群
        self.claude_md_files = [
            "/mnt/c/Users/tky99/CLAUDE.md",
            "/mnt/c/Users/tky99/dev/CLAUDE.md",
            "/mnt/c/Users/tky99/dev/technical-fountain-series-support-tool/CLAUDE.md",
            "/mnt/c/Users/tky99/dev/narou_converter/CLAUDE.md",
            "/mnt/c/Users/tky99/dev/techbookfest_scraper/CLAUDE.md",
            "/mnt/c/Users/tky99/dev/techbookanalytics/CLAUDE.md",
            "/mnt/c/Users/tky99/dev/miszen/CLAUDE.md",
            "/mnt/c/Users/tky99/dev/cc_changewatch/CLAUDE.md"
        ]
        
    def check_should_backup(self) -> Tuple[bool, str]:
        """
        バックアップが必要かチェック
        
        Returns:
            (should_backup, reason)
        """
        today = datetime.now().strftime("%Y%m%d")
        today_backup = self.backup_base_dir / f"daily_backup_{today}.zip"
        
        if not today_backup.exists():
            return True, f"今日の日次バックアップが存在しません: {today}"
        
        # 設定ファイルの変更チェック
        for name, path in self.backup_targets.items():
            if path.exists():
                file_mtime = datetime.fromtimestamp(path.stat().st_mtime)
                backup_mtime = datetime.fromtimestamp(today_backup.stat().st_mtime)
                if file_mtime > backup_mtime:
                    return True, f"設定ファイル '{name}' が更新されています"
        
        # CLAUDE.mdファイル変更チェック
        for claude_md in self.claude_md_files:
            path = Path(claude_md)
            if path.exists():
                file_mtime = datetime.fromtimestamp(path.stat().st_mtime)
                backup_mtime = datetime.fromtimestamp(today_backup.stat().st_mtime)
                if file_mtime > backup_mtime:
                    return True, f"CLAUDE.mdファイルが更新されています: {claude_md}"
        
        return False, "バックアップは最新です"
    
    def create_daily_backup(self) -> str:
        """
        日次バックアップを作成
        
        Returns:
            作成されたバックアップファイルのパス
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_base_dir / f"daily_backup_{timestamp}.zip"
        
        print(f"📦 日次バックアップ作成中: {backup_file}")
        
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Claude Code設定ファイル
            for name, path in self.backup_targets.items():
                if path.exists():
                    if path.is_file():
                        zf.write(path, f"claude_config/{name}/{path.name}")
                        print(f"  ✅ {name}: {path}")
                    elif path.is_dir():
                        for file_path in path.rglob("*"):
                            if file_path.is_file():
                                rel_path = file_path.relative_to(path)
                                zf.write(file_path, f"claude_config/{name}/{rel_path}")
                        print(f"  ✅ {name} (ディレクトリ): {path}")
                else:
                    print(f"  ⚠️  {name} は存在しません: {path}")
            
            # CLAUDE.mdファイル群
            for claude_md in self.claude_md_files:
                path = Path(claude_md)
                if path.exists():
                    # パス構造を保持してアーカイブ
                    archive_path = f"claude_md_files{claude_md}"
                    zf.write(path, archive_path)
                    print(f"  ✅ CLAUDE.md: {claude_md}")
            
            # MCP設定のクリーンアップ（claude mcp listの出力）
            try:
                mcp_list_result = subprocess.run(
                    ["claude", "mcp", "list"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if mcp_list_result.returncode == 0:
                    zf.writestr("mcp_status/mcp_list_output.txt", mcp_list_result.stdout)
                    print("  ✅ MCP設定状況を保存")
            except Exception as e:
                print(f"  ⚠️  MCP設定取得エラー: {e}")
            
            # システム情報
            system_info = {
                "backup_timestamp": timestamp,
                "claude_code_version": self._get_claude_version(),
                "system_info": {
                    "os": os.name,
                    "platform": sys.platform,
                    "python_version": sys.version
                }
            }
            zf.writestr("system_info.json", json.dumps(system_info, indent=2, ensure_ascii=False))
        
        # 今日の日次バックアップのシンボリックリンク作成
        today = datetime.now().strftime("%Y%m%d")
        daily_link = self.backup_base_dir / f"daily_backup_{today}.zip"
        if daily_link.exists():
            daily_link.unlink()
        
        # Windows環境でのシンボリックリンク代替
        try:
            shutil.copy2(backup_file, daily_link)
            print(f"📅 日次バックアップリンク作成: {daily_link}")
        except Exception as e:
            print(f"⚠️  日次リンク作成失敗: {e}")
        
        print(f"✅ バックアップ完了: {backup_file}")
        
        # 復旧方法の案内を表示
        print()
        print("🚨 " + "=" * 50)
        print("📢 Claude Code認証エラー発生時の復旧方法:")
        print("   devディレクトリで以下のコマンドを実行してください:")
        print("   .\\\\clauderestore.ps1")
        print("=" * 54)
        
        return str(backup_file)
    
    def list_backups(self) -> List[Dict]:
        """利用可能なバックアップ一覧を取得"""
        backups = []
        for backup_file in self.backup_base_dir.glob("daily_backup_*.zip"):
            try:
                stat = backup_file.stat()
                backups.append({
                    "file": str(backup_file),
                    "name": backup_file.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                print(f"⚠️  バックアップファイル読み取りエラー: {backup_file} - {e}")
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def restore_from_backup(self, backup_file: Optional[str] = None) -> bool:
        """
        バックアップから復元
        
        Args:
            backup_file: 復元するバックアップファイル。Noneの場合は最新を使用
            
        Returns:
            復元成功かどうか
        """
        if backup_file is None:
            backups = self.list_backups()
            if not backups:
                print("❌ 利用可能なバックアップがありません")
                return False
            backup_file = backups[0]["file"]
        
        backup_path = Path(backup_file)
        if not backup_path.exists():
            print(f"❌ バックアップファイルが存在しません: {backup_file}")
            return False
        
        print(f"🔄 バックアップから復元中: {backup_file}")
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # 一時ディレクトリに展開
                with tempfile.TemporaryDirectory() as temp_dir:
                    zf.extractall(temp_dir)
                    temp_path = Path(temp_dir)
                    
                    # Claude設定復元
                    claude_config_backup = temp_path / "claude_config"
                    if claude_config_backup.exists():
                        # Claude設定ディレクトリのバックアップ
                        if self.claude_config_dir.exists():
                            backup_current = self.backup_base_dir / f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                            self._backup_current_config(backup_current)
                        
                        # 設定復元
                        self.claude_config_dir.mkdir(parents=True, exist_ok=True)
                        
                        for config_type in claude_config_backup.iterdir():
                            if config_type.is_dir():
                                target_path = self.backup_targets.get(config_type.name)
                                if target_path:
                                    if target_path.exists():
                                        if target_path.is_file():
                                            target_path.unlink()
                                        else:
                                            shutil.rmtree(target_path)
                                    
                                    source_files = list(config_type.rglob("*"))
                                    if len(source_files) == 1 and source_files[0].is_file():
                                        # 単一ファイルの場合
                                        shutil.copy2(source_files[0], target_path)
                                        print(f"  ✅ 復元: {config_type.name} -> {target_path}")
                                    else:
                                        # ディレクトリの場合
                                        shutil.copytree(config_type, target_path, dirs_exist_ok=True)
                                        print(f"  ✅ 復元 (ディレクトリ): {config_type.name} -> {target_path}")
                    
                    # CLAUDE.mdファイル復元
                    claude_md_backup = temp_path / "claude_md_files"
                    if claude_md_backup.exists():
                        for claude_md_path in self.claude_md_files:
                            backup_md_path = claude_md_backup / claude_md_path.lstrip("/")
                            if backup_md_path.exists():
                                target_path = Path(claude_md_path)
                                target_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(backup_md_path, target_path)
                                print(f"  ✅ CLAUDE.md復元: {claude_md_path}")
            
            print("✅ バックアップからの復元完了")
            return True
            
        except Exception as e:
            print(f"❌ 復元エラー: {e}")
            return False
    
    def _backup_current_config(self, backup_file: Path):
        """現在の設定を緊急バックアップ"""
        try:
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for name, path in self.backup_targets.items():
                    if path.exists():
                        if path.is_file():
                            zf.write(path, f"{name}/{path.name}")
                        elif path.is_dir():
                            for file_path in path.rglob("*"):
                                if file_path.is_file():
                                    rel_path = file_path.relative_to(path)
                                    zf.write(file_path, f"{name}/{rel_path}")
            print(f"🔄 現在の設定をバックアップ: {backup_file}")
        except Exception as e:
            print(f"⚠️  現在設定のバックアップ失敗: {e}")
    
    def _get_claude_version(self) -> str:
        """Claude Codeのバージョンを取得"""
        try:
            result = subprocess.run(
                ["claude", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"
    
    def startup_check_and_backup(self) -> bool:
        """
        起動時チェック・バックアップ実行
        
        Returns:
            バックアップを実行したかどうか
        """
        print("🚀 Claude Code起動時チェック開始")
        
        should_backup, reason = self.check_should_backup()
        
        if should_backup:
            print(f"📦 バックアップが必要です: {reason}")
            try:
                self.create_daily_backup()
                return True
            except Exception as e:
                print(f"❌ バックアップ失敗: {e}")
                return False
        else:
            print(f"✅ {reason}")
            return False


def main():
    """メインエントリーポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Code認証エラー対策システム")
    parser.add_argument("action", choices=["check", "backup", "restore", "list", "startup"], 
                       help="実行するアクション")
    parser.add_argument("--backup-file", help="復元するバックアップファイル")
    parser.add_argument("--force", action="store_true", help="強制実行")
    
    args = parser.parse_args()
    
    backup_system = ClaudeCodeBackupSystem()
    
    if args.action == "startup":
        # 起動時チェック・バックアップ
        backup_system.startup_check_and_backup()
        
    elif args.action == "check":
        # バックアップ必要性チェック
        should_backup, reason = backup_system.check_should_backup()
        print(f"バックアップ必要: {should_backup}")
        print(f"理由: {reason}")
        
    elif args.action == "backup":
        # 手動バックアップ
        backup_system.create_daily_backup()
        
    elif args.action == "list":
        # バックアップ一覧
        backups = backup_system.list_backups()
        print(f"📋 利用可能なバックアップ: {len(backups)}個")
        for backup in backups:
            print(f"  📦 {backup['name']} ({backup['created']}, {backup['size']:,} bytes)")
    
    elif args.action == "restore":
        # 復元
        if args.backup_file or args.force:
            success = backup_system.restore_from_backup(args.backup_file)
            sys.exit(0 if success else 1)
        else:
            backups = backup_system.list_backups()
            if backups:
                print(f"最新のバックアップから復元しますか？")
                print(f"📦 {backups[0]['name']} ({backups[0]['created']})")
                confirm = input("復元を実行しますか？ (y/N): ")
                if confirm.lower() == 'y':
                    success = backup_system.restore_from_backup()
                    sys.exit(0 if success else 1)
                else:
                    print("復元をキャンセルしました")


if __name__ == "__main__":
    main()