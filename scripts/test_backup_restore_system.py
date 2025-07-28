#!/usr/bin/env python3
"""
バックアップ・復旧システムのドライランテスト
設定削除や認証を行わない安全なテストモード
"""

import os
import json
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from claude_code_backup_system import ClaudeCodeBackupSystem
from claude_code_recovery_system import ClaudeCodeRecoverySystem

class BackupRestoreTester:
    """バックアップ・復旧システムの安全テスト実行クラス"""
    
    def __init__(self):
        self.backup_system = ClaudeCodeBackupSystem()
        self.recovery_system = ClaudeCodeRecoverySystem()
        self.test_dir = Path("/tmp/claude_code_test")
        self.results = {
            "test_timestamp": datetime.now().isoformat(),
            "tests": []
        }
        
    def setup_test_environment(self):
        """テスト環境のセットアップ"""
        print("🧪 テスト環境セットアップ中...")
        
        # テストディレクトリ作成
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # 模擬Claude設定の作成
        mock_config = self.test_dir / "mock_claude_config"
        mock_config.mkdir(exist_ok=True)
        
        # 模擬設定ファイル作成
        mock_files = {
            "mcp_servers.json": {
                "memory-integration": {
                    "command": "python",
                    "args": ["-m", "memory_integration.server"],
                    "env": {"LOG_LEVEL": "INFO"}
                }
            },
            "settings.json": {
                "theme": "dark",
                "auto_backup": True
            },
            "auth.json": {
                "token": "mock_token_12345",
                "expires": "2025-12-31T23:59:59Z"
            }
        }
        
        for filename, content in mock_files.items():
            file_path = mock_config / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 模擬設定作成: {mock_config}")
        return mock_config
    
    def test_backup_functionality(self) -> Dict:
        """バックアップ機能のテスト"""
        print("\n📦 バックアップ機能テスト開始")
        test_result = {
            "test_name": "backup_functionality",
            "start_time": datetime.now().isoformat(),
            "success": True,
            "details": []
        }
        
        try:
            # バックアップ必要性チェック
            should_backup, reason = self.backup_system.check_should_backup()
            test_result["details"].append({
                "step": "backup_necessity_check",
                "result": f"Should backup: {should_backup}, Reason: {reason}"
            })
            print(f"  📋 バックアップ必要性: {should_backup} - {reason}")
            
            # バックアップ一覧取得
            backups = self.backup_system.list_backups()
            test_result["details"].append({
                "step": "list_backups",
                "result": f"Available backups: {len(backups)}"
            })
            print(f"  📋 利用可能バックアップ: {len(backups)}個")
            
            if backups:
                # 最新バックアップの詳細
                latest = backups[0]
                print(f"    最新: {latest['name']} ({latest['created']})")
                test_result["details"].append({
                    "step": "latest_backup_info",
                    "result": f"Latest: {latest['name']} - {latest['created']}"
                })
            
        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            print(f"  ❌ バックアップテストエラー: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def test_restore_dry_run(self) -> Dict:
        """復元機能のドライランテスト"""
        print("\n🔄 復元機能ドライランテスト開始")
        test_result = {
            "test_name": "restore_dry_run",
            "start_time": datetime.now().isoformat(),
            "success": True,
            "details": []
        }
        
        try:
            # 利用可能なバックアップ確認
            backups = self.backup_system.list_backups()
            if not backups:
                test_result["success"] = False
                test_result["error"] = "利用可能なバックアップが存在しません"
                print("  ❌ テスト用バックアップが存在しません")
                return test_result
            
            latest_backup = backups[0]["file"]
            print(f"  📦 テスト対象バックアップ: {Path(latest_backup).name}")
            
            # バックアップ内容の検証
            backup_content = self._analyze_backup_content(latest_backup)
            test_result["details"].append({
                "step": "backup_content_analysis",
                "result": backup_content
            })
            
            # 復元プロセスのシミュレーション
            restore_simulation = self._simulate_restore_process(latest_backup)
            test_result["details"].append({
                "step": "restore_simulation",
                "result": restore_simulation
            })
            
            print("  ✅ 復元ドライランテスト完了")
            
        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            print(f"  ❌ 復元テストエラー: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def test_recovery_diagnosis(self) -> Dict:
        """復旧診断機能のテスト"""
        print("\n🔍 復旧診断機能テスト開始")
        test_result = {
            "test_name": "recovery_diagnosis",
            "start_time": datetime.now().isoformat(),
            "success": True,
            "details": []
        }
        
        try:
            # 診断実行
            diagnosis = self.recovery_system.diagnose_auth_issue()
            
            # 診断結果の分析
            analysis = {
                "config_exists": diagnosis.get("config_exists", False),
                "config_files_count": len(diagnosis.get("config_files", {})),
                "claude_command_works": diagnosis.get("claude_command_works", False),
                "auth_error_detected": diagnosis.get("auth_error_detected", False)
            }
            
            test_result["details"].append({
                "step": "diagnosis_execution",
                "result": analysis
            })
            
            print(f"  📋 設定ディレクトリ: {'存在' if analysis['config_exists'] else '不存在'}")
            print(f"  📋 設定ファイル数: {analysis['config_files_count']}")
            print(f"  📋 Claudeコマンド: {'動作' if analysis['claude_command_works'] else '不動作'}")
            print(f"  📋 認証エラー: {'検出' if analysis['auth_error_detected'] else '未検出'}")
            
        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            print(f"  ❌ 診断テストエラー: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def test_powershell_command(self) -> Dict:
        """PowerShellコマンドのテスト"""
        print("\n💻 PowerShellコマンドテスト開始")
        test_result = {
            "test_name": "powershell_command",
            "start_time": datetime.now().isoformat(),
            "success": True,
            "details": []
        }
        
        try:
            # PowerShellスクリプトの存在確認
            ps_script = Path("/mnt/c/Users/tky99/dev/clauderestore.ps1")
            script_exists = ps_script.exists()
            
            test_result["details"].append({
                "step": "script_existence_check",
                "result": f"PowerShell script exists: {script_exists}"
            })
            
            print(f"  📋 PowerShellスクリプト: {'存在' if script_exists else '不存在'}")
            
            if script_exists:
                # スクリプト内容の基本検証
                with open(ps_script, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 重要なコマンドラインオプションの確認
                required_actions = ["full-recovery", "quick-recovery", "diagnose", "backup", "list"]
                available_actions = [action for action in required_actions if action in content]
                
                test_result["details"].append({
                    "step": "script_content_validation",
                    "result": f"Available actions: {available_actions}"
                })
                
                print(f"  📋 利用可能アクション: {len(available_actions)}/{len(required_actions)}")
                
                # WSL統合の確認
                wsl_integration = "wsl python3" in content
                test_result["details"].append({
                    "step": "wsl_integration_check",
                    "result": f"WSL integration: {wsl_integration}"
                })
                
                print(f"  📋 WSL統合: {'有効' if wsl_integration else '無効'}")
            
        except Exception as e:
            test_result["success"] = False
            test_result["error"] = str(e)
            print(f"  ❌ PowerShellテストエラー: {e}")
        
        test_result["end_time"] = datetime.now().isoformat()
        return test_result
    
    def _analyze_backup_content(self, backup_file: str) -> Dict:
        """バックアップファイルの内容分析"""
        analysis = {
            "file_size": Path(backup_file).stat().st_size,
            "contains_claude_config": False,
            "contains_claude_md": False,
            "contains_system_info": False,
            "file_count": 0
        }
        
        try:
            with zipfile.ZipFile(backup_file, 'r') as zf:
                file_list = zf.namelist()
                analysis["file_count"] = len(file_list)
                
                # 主要コンテンツの確認
                for file_path in file_list:
                    if "claude_config/" in file_path:
                        analysis["contains_claude_config"] = True
                    elif "claude_md_files/" in file_path:
                        analysis["contains_claude_md"] = True
                    elif "system_info.json" in file_path:
                        analysis["contains_system_info"] = True
                
                print(f"    📁 ファイル数: {analysis['file_count']}")
                print(f"    📁 Claude設定: {'含む' if analysis['contains_claude_config'] else '含まない'}")
                print(f"    📁 CLAUDE.md: {'含む' if analysis['contains_claude_md'] else '含まない'}")
                print(f"    📁 システム情報: {'含む' if analysis['contains_system_info'] else '含まない'}")
                
        except Exception as e:
            analysis["error"] = str(e)
            print(f"    ⚠️  バックアップ分析エラー: {e}")
        
        return analysis
    
    def _simulate_restore_process(self, backup_file: str) -> Dict:
        """復元プロセスのシミュレーション"""
        simulation = {
            "backup_file": backup_file,
            "extraction_test": False,
            "file_structure_valid": False,
            "restoration_steps": []
        }
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # バックアップの展開テスト
                with zipfile.ZipFile(backup_file, 'r') as zf:
                    zf.extractall(temp_path)
                simulation["extraction_test"] = True
                
                # ファイル構造の検証
                expected_dirs = ["claude_config", "claude_md_files"]
                valid_structure = all((temp_path / dir_name).exists() for dir_name in expected_dirs)
                simulation["file_structure_valid"] = valid_structure
                
                # 復元ステップのシミュレーション
                steps = [
                    "1. バックアップ展開",
                    "2. 設定ファイル準備",
                    "3. CLAUDE.mdファイル準備",
                    "4. システム情報確認"
                ]
                
                simulation["restoration_steps"] = steps
                
                print(f"    🔄 展開テスト: {'成功' if simulation['extraction_test'] else '失敗'}")
                print(f"    🔄 構造検証: {'有効' if simulation['file_structure_valid'] else '無効'}")
                print(f"    🔄 復元ステップ: {len(steps)}個")
                
        except Exception as e:
            simulation["error"] = str(e)
            print(f"    ⚠️  シミュレーションエラー: {e}")
        
        return simulation
    
    def run_all_tests(self) -> Dict:
        """全テストの実行"""
        print("🧪 バックアップ・復旧システム 包括テスト開始")
        print("=" * 60)
        
        # テスト実行
        self.results["tests"].append(self.test_backup_functionality())
        self.results["tests"].append(self.test_restore_dry_run())
        self.results["tests"].append(self.test_recovery_diagnosis())
        self.results["tests"].append(self.test_powershell_command())
        
        # 結果サマリー
        successful_tests = sum(1 for test in self.results["tests"] if test["success"])
        total_tests = len(self.results["tests"])
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": f"{successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)"
        }
        
        print("\n" + "=" * 60)
        print("📊 テスト結果サマリー")
        print(f"   総テスト数: {total_tests}")
        print(f"   成功: {successful_tests}")
        print(f"   成功率: {successful_tests/total_tests*100:.1f}%")
        
        # 各テストの結果
        for test in self.results["tests"]:
            status = "✅ 成功" if test["success"] else "❌ 失敗"
            print(f"   {test['test_name']}: {status}")
            if not test["success"] and "error" in test:
                print(f"     エラー: {test['error']}")
        
        # テスト結果のファイル出力
        results_file = Path("/mnt/c/Users/tky99/dev/technical-fountain-series-support-tool") / "backup_restore_test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 詳細結果: {results_file}")
        
        return self.results

def main():
    """メインエントリーポイント"""
    import argparse
    
    parser = argparse.ArgumentParser(description="バックアップ・復旧システムドライランテスト")
    parser.add_argument("--test", choices=["all", "backup", "restore", "diagnosis", "powershell"], 
                       default="all", help="実行するテスト")
    parser.add_argument("--verbose", action="store_true", help="詳細出力")
    
    args = parser.parse_args()
    
    tester = BackupRestoreTester()
    
    if args.test == "all":
        results = tester.run_all_tests()
    elif args.test == "backup":
        results = {"tests": [tester.test_backup_functionality()]}
    elif args.test == "restore":
        results = {"tests": [tester.test_restore_dry_run()]}
    elif args.test == "diagnosis":
        results = {"tests": [tester.test_recovery_diagnosis()]}
    elif args.test == "powershell":
        results = {"tests": [tester.test_powershell_command()]}
    
    # 結果に基づく終了コード
    if results.get("summary"):
        success_rate = results["summary"]["successful_tests"] / results["summary"]["total_tests"]
        exit_code = 0 if success_rate == 1.0 else 1
    else:
        exit_code = 0 if all(test["success"] for test in results["tests"]) else 1
    
    exit(exit_code)

if __name__ == "__main__":
    main()