#!/usr/bin/env python3
"""
コードブロックはみ出し検出システム 一気通貫開発ワークフロー
仕様書駆動開発による品質保証付き自動化開発プロセス
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from quality_check import IntegratedQualityChecker, QualityReport


@dataclass
class WorkflowStep:
    """ワークフローステップ"""
    name: str
    command: List[str]
    success_criteria: str
    timeout: int = 60
    required: bool = True


@dataclass
class WorkflowResult:
    """ワークフロー実行結果"""
    step_name: str
    success: bool
    execution_time: float
    output: str
    error: str


class SpecificationDrivenWorkflow:
    """仕様書駆動開発ワークフロー"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results: List[WorkflowResult] = []
        self.quality_checker = IntegratedQualityChecker(project_root)
    
    def run_phase1_workflow(self) -> bool:
        """Phase 1: 単独アプリケーション開発ワークフロー"""
        print("🚀 Phase 1 開発ワークフロー開始")
        print("=" * 60)
        
        # Phase 1 ワークフローステップ定義
        steps = [
            WorkflowStep(
                "環境セットアップ",
                ["pip", "install", "-r", "requirements_ocr.txt"],
                "依存関係の正常インストール"
            ),
            WorkflowStep(
                "静的解析",
                ["python", "-m", "flake8", "overflow_detector_ocr.py"],
                "コードスタイル準拠",
                required=False
            ),
            WorkflowStep(
                "基本動作確認",
                ["python", "overflow_detector_ocr.py", "--help"],
                "ヘルプメッセージ表示"
            ),
            WorkflowStep(
                "統合品質チェック",
                ["python", "quality_check.py"],
                "品質基準クリア",
                timeout=120
            ),
            WorkflowStep(
                "パッケージング準備",
                ["python", "-c", "import overflow_detector_ocr; print('Import OK')"],
                "モジュールインポート成功"
            )
        ]
        
        return self._execute_workflow_steps(steps, "Phase 1")
    
    def run_phase2_integration_plan(self) -> Dict:
        """Phase 2: 統合計画の策定と準備"""
        print("\n🔄 Phase 2 統合計画策定")
        print("=" * 60)
        
        integration_plan = {
            "target_system": "技術の泉シリーズ制作支援ツール",
            "integration_points": [
                {
                    "name": "PDF後処理フック",
                    "description": "Word変換後のPDFをはみ出し検査",
                    "location": "core/workflow_processor.py",
                    "method": "post_pdf_processing"
                },
                {
                    "name": "品質チェックGUI",
                    "description": "メインGUIに品質チェック機能追加",
                    "location": "gui/main_window_qt6.py", 
                    "method": "add_quality_check_tab"
                },
                {
                    "name": "バッチ処理統合",
                    "description": "複数PDF一括検査機能",
                    "location": "core/file_manager.py",
                    "method": "batch_overflow_check"
                }
            ],
            "technical_requirements": [
                "OCRBasedOverflowDetectorクラスの共通ライブラリ化",
                "Qt6 GUIコンポーネントの作成",
                "設定ファイル統合（settings.json拡張）",
                "ログシステム統合"
            ],
            "estimated_effort": "10-15時間",
            "dependencies": [
                "Phase 1完了",
                "メインシステムのQt6移行完了",
                "設定管理システムの拡張"
            ]
        }
        
        # 統合計画をファイルに保存
        plan_path = self.project_root / "phase2_integration_plan.json"
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(integration_plan, f, indent=2, ensure_ascii=False)
        
        print(f"📋 統合計画を保存: {plan_path}")
        
        # 統合可能性チェック
        compatibility_score = self._check_integration_compatibility()
        print(f"🔍 統合可能性スコア: {compatibility_score:.1%}")
        
        return integration_plan
    
    def _execute_workflow_steps(self, steps: List[WorkflowStep], phase_name: str) -> bool:
        """ワークフローステップの実行"""
        success_count = 0
        total_steps = len(steps)
        
        for i, step in enumerate(steps, 1):
            print(f"\n🔄 [{i}/{total_steps}] {step.name}")
            print(f"コマンド: {' '.join(step.command)}")
            
            result = self._execute_step(step)
            self.results.append(result)
            
            if result.success:
                print(f"✅ 成功 ({result.execution_time:.2f}秒)")
                success_count += 1
            else:
                status = "⚠️ スキップ" if not step.required else "❌ 失敗"
                print(f"{status} ({result.execution_time:.2f}秒)")
                if result.error:
                    print(f"   エラー: {result.error}")
                
                if step.required:
                    print(f"\n❌ {phase_name} ワークフロー中断")
                    return False
        
        success_rate = success_count / total_steps
        print(f"\n📊 {phase_name} 完了率: {success_rate:.1%} ({success_count}/{total_steps})")
        
        return success_rate >= 0.8  # 80%以上成功で合格
    
    def _execute_step(self, step: WorkflowStep) -> WorkflowResult:
        """単一ステップの実行"""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                step.command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=step.timeout
            )
            
            execution_time = time.time() - start_time
            success = result.returncode == 0
            
            return WorkflowResult(
                step_name=step.name,
                success=success,
                execution_time=execution_time,
                output=result.stdout,
                error=result.stderr
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return WorkflowResult(
                step_name=step.name,
                success=False,
                execution_time=execution_time,
                output="",
                error=f"タイムアウト ({step.timeout}秒)"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return WorkflowResult(
                step_name=step.name,
                success=False,
                execution_time=execution_time,
                output="",
                error=str(e)
            )
    
    def _check_integration_compatibility(self) -> float:
        """メインシステムとの統合可能性チェック"""
        compatibility_factors = []
        
        # 1. メインシステムファイルの存在確認
        main_system_files = [
            "../gui/main_window_qt6.py",
            "../core/workflow_processor.py",
            "../core/file_manager.py",
            "../config/settings.json"
        ]
        
        existing_files = 0
        for file_path in main_system_files:
            if (self.project_root / file_path).exists():
                existing_files += 1
        
        compatibility_factors.append(existing_files / len(main_system_files))
        
        # 2. 依存関係の互換性
        try:
            # PyQt6が利用可能かチェック
            result = subprocess.run(
                ["python", "-c", "import PyQt6; print('OK')"],
                capture_output=True,
                text=True
            )
            compatibility_factors.append(1.0 if result.returncode == 0 else 0.0)
        except:
            compatibility_factors.append(0.0)
        
        # 3. 現在の実装完成度
        impl_completeness = self._assess_implementation_completeness()
        compatibility_factors.append(impl_completeness)
        
        return sum(compatibility_factors) / len(compatibility_factors)
    
    def _assess_implementation_completeness(self) -> float:
        """現在の実装完成度評価"""
        required_components = [
            "overflow_detector_ocr.py",
            "requirements_ocr.txt",
            "requirements.md",
            "design.md",
            "quality_check.py",
            "README_OCR.md"
        ]
        
        existing_components = 0
        for component in required_components:
            if (self.project_root / component).exists():
                existing_components += 1
        
        return existing_components / len(required_components)
    
    def generate_workflow_report(self) -> str:
        """ワークフロー実行レポート生成"""
        report_lines = [
            "# 一気通貫開発ワークフロー実行レポート",
            f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # ステップ別結果
        if self.results:
            report_lines.extend([
                "## ステップ実行結果",
                ""
            ])
            
            for result in self.results:
                status = "✅ 成功" if result.success else "❌ 失敗"
                report_lines.extend([
                    f"### {result.step_name}",
                    f"- ステータス: {status}",
                    f"- 実行時間: {result.execution_time:.2f}秒",
                    ""
                ])
                
                if result.error:
                    report_lines.extend([
                        f"- エラー: {result.error}",
                        ""
                    ])
        
        # 統計情報
        success_count = sum(1 for r in self.results if r.success)
        total_count = len(self.results)
        total_time = sum(r.execution_time for r in self.results)
        
        report_lines.extend([
            "## 統計情報",
            f"- 成功率: {success_count/total_count:.1%} ({success_count}/{total_count})",
            f"- 総実行時間: {total_time:.2f}秒",
            ""
        ])
        
        report_content = "\n".join(report_lines)
        
        # レポートファイル保存
        report_path = self.project_root / "workflow_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_content


def main():
    """メインエントリーポイント"""
    project_root = Path(__file__).parent
    workflow = SpecificationDrivenWorkflow(project_root)
    
    print("🏗️ 仕様書駆動開発 一気通貫ワークフロー")
    print("=" * 60)
    
    # Phase 1: 単独アプリケーション開発
    phase1_success = workflow.run_phase1_workflow()
    
    if phase1_success:
        print("\n✅ Phase 1 完了")
        
        # Phase 2: 統合計画策定
        integration_plan = workflow.run_phase2_integration_plan()
        
        print("\n📋 Phase 2 統合計画完了")
        print("次のステップ:")
        print("1. 単独アプリケーションのテスト実行")
        print("2. メインシステムとの統合作業")
        print("3. 統合テストとリリース")
        
    else:
        print("\n❌ Phase 1 未完了")
        print("品質基準を満たすまで開発継続が必要です")
    
    # 最終レポート生成
    report = workflow.generate_workflow_report()
    print(f"\n📄 ワークフローレポート: workflow_report.md")
    
    # 終了コード設定
    sys.exit(0 if phase1_success else 1)


if __name__ == "__main__":
    main()