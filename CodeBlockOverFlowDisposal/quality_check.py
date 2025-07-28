#!/usr/bin/env python3
"""
コードブロックはみ出し検出システム 品質チェック統合スクリプト
仕様書駆動開発における継続的品質保証
"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QualityMetric:
    """品質メトリクス"""
    name: str
    value: float
    threshold: float
    status: str  # "PASS", "FAIL", "WARNING"
    message: str


@dataclass
class QualityReport:
    """品質レポート"""
    timestamp: str
    overall_status: str
    metrics: List[QualityMetric]
    execution_time: float
    errors: List[str]


class IntegratedQualityChecker:
    """統合品質チェッカー"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.start_time = None
        self.errors = []
        
    def run_comprehensive_check(self) -> QualityReport:
        """包括的品質チェックの実行"""
        self.start_time = time.time()
        print("🚀 統合品質チェック開始")
        print("=" * 60)
        
        metrics = []
        
        # 1. 仕様書整合性チェック
        print("\n📋 1. 仕様書整合性チェック")
        spec_metrics = self._check_specification_compliance()
        metrics.extend(spec_metrics)
        
        # 2. コード品質チェック
        print("\n🔍 2. コード品質チェック")
        code_metrics = self._check_code_quality()
        metrics.extend(code_metrics)
        
        # 3. 機能テスト
        print("\n🧪 3. 機能テスト実行")
        test_metrics = self._run_functional_tests()
        metrics.extend(test_metrics)
        
        # 4. 性能テスト
        print("\n⚡ 4. 性能テスト実行")
        perf_metrics = self._run_performance_tests()
        metrics.extend(perf_metrics)
        
        # 5. セキュリティチェック
        print("\n🔒 5. セキュリティチェック")
        sec_metrics = self._run_security_check()
        metrics.extend(sec_metrics)
        
        # 総合評価
        execution_time = time.time() - self.start_time
        overall_status = self._calculate_overall_status(metrics)
        
        report = QualityReport(
            timestamp=datetime.now().isoformat(),
            overall_status=overall_status,
            metrics=metrics,
            execution_time=execution_time,
            errors=self.errors
        )
        
        self._generate_quality_report(report)
        return report
        
    def _check_specification_compliance(self) -> List[QualityMetric]:
        """仕様書整合性チェック"""
        metrics = []
        
        try:
            # requirements.mdの存在確認
            requirements_path = self.project_root / "requirements.md"
            if requirements_path.exists():
                metrics.append(QualityMetric(
                    "要件仕様書", 1.0, 1.0, "PASS", "要件仕様書が存在します"
                ))
            else:
                metrics.append(QualityMetric(
                    "要件仕様書", 0.0, 1.0, "FAIL", "要件仕様書が存在しません"
                ))
            
            # design.mdの存在確認
            design_path = self.project_root / "design.md"
            if design_path.exists():
                metrics.append(QualityMetric(
                    "設計仕様書", 1.0, 1.0, "PASS", "設計仕様書が存在します"
                ))
            else:
                metrics.append(QualityMetric(
                    "設計仕様書", 0.0, 1.0, "FAIL", "設計仕様書が存在しません"
                ))
            
            # 実装ファイルと仕様の整合性
            impl_compliance = self._check_implementation_compliance()
            metrics.append(QualityMetric(
                "実装整合性", impl_compliance, 0.8, 
                "PASS" if impl_compliance >= 0.8 else "WARNING",
                f"仕様との整合性: {impl_compliance:.1%}"
            ))
            
        except Exception as e:
            self.errors.append(f"仕様書チェックエラー: {e}")
            
        return metrics
    
    def _check_implementation_compliance(self) -> float:
        """実装と仕様の整合性チェック"""
        # OCRBasedOverflowDetectorクラスの存在確認
        ocr_impl_path = self.project_root / "overflow_detector_ocr.py"
        if not ocr_impl_path.exists():
            return 0.0
            
        # 必須メソッドの存在確認
        try:
            with open(ocr_impl_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_methods = [
                "detect_file",
                "_check_text_overflow_ocr", 
                "generate_report",
                "__init__"
            ]
            
            found_methods = sum(1 for method in required_methods 
                              if f"def {method}" in content)
            
            return found_methods / len(required_methods)
            
        except Exception:
            return 0.0
    
    def _check_code_quality(self) -> List[QualityMetric]:
        """コード品質チェック"""
        metrics = []
        
        # Flake8チェック
        flake8_score = self._run_flake8()
        metrics.append(QualityMetric(
            "PEP8準拠", flake8_score, 0.9, 
            "PASS" if flake8_score >= 0.9 else "WARNING",
            f"コードスタイル適合率: {flake8_score:.1%}"
        ))
        
        # 複雑度チェック
        complexity_score = self._check_complexity()
        metrics.append(QualityMetric(
            "コード複雑度", complexity_score, 0.8,
            "PASS" if complexity_score >= 0.8 else "WARNING", 
            f"複雑度スコア: {complexity_score:.2f}"
        ))
        
        # 型ヒントチェック
        typing_score = self._check_type_hints()
        metrics.append(QualityMetric(
            "型ヒント", typing_score, 0.8,
            "PASS" if typing_score >= 0.8 else "WARNING",
            f"型ヒント適用率: {typing_score:.1%}"
        ))
        
        return metrics
    
    def _run_flake8(self) -> float:
        """Flake8による静的解析"""
        try:
            result = subprocess.run(
                ["python", "-m", "flake8", "--count", "overflow_detector_ocr.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return 1.0  # エラーなし
            else:
                # エラー数から品質スコアを計算
                error_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                # 100行あたり5エラー以下なら合格ラインとする
                return max(0.0, 1.0 - (error_count * 0.02))
                
        except Exception as e:
            self.errors.append(f"Flake8実行エラー: {e}")
            return 0.5
    
    def _check_complexity(self) -> float:
        """コード複雑度チェック"""
        try:
            # 簡易的な複雑度チェック（実際の実装では radon 等を使用）
            ocr_impl_path = self.project_root / "overflow_detector_ocr.py"
            if not ocr_impl_path.exists():
                return 0.0
                
            with open(ocr_impl_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 簡易指標：if/for/while文の数
            control_statements = content.count('if ') + content.count('for ') + content.count('while ')
            lines_of_code = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
            
            if lines_of_code == 0:
                return 0.0
                
            complexity_ratio = control_statements / lines_of_code
            # 10%以下なら良好とする
            return max(0.0, 1.0 - (complexity_ratio * 10))
            
        except Exception as e:
            self.errors.append(f"複雑度チェックエラー: {e}")
            return 0.5
    
    def _check_type_hints(self) -> float:
        """型ヒントの使用率チェック"""
        try:
            ocr_impl_path = self.project_root / "overflow_detector_ocr.py"
            if not ocr_impl_path.exists():
                return 0.0
                
            with open(ocr_impl_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 関数定義の数
            function_defs = content.count('def ')
            
            # 型ヒント付き関数の数
            typed_functions = content.count(' -> ')
            
            if function_defs == 0:
                return 0.0
                
            return typed_functions / function_defs
            
        except Exception as e:
            self.errors.append(f"型ヒントチェックエラー: {e}")
            return 0.5
    
    def _run_functional_tests(self) -> List[QualityMetric]:
        """機能テスト実行"""
        metrics = []
        
        # 基本動作テスト
        basic_test_result = self._test_basic_functionality()
        metrics.append(QualityMetric(
            "基本機能", basic_test_result, 1.0,
            "PASS" if basic_test_result == 1.0 else "FAIL",
            "基本機能の動作テスト"
        ))
        
        # エラーハンドリングテスト
        error_test_result = self._test_error_handling()
        metrics.append(QualityMetric(
            "エラーハンドリング", error_test_result, 1.0,
            "PASS" if error_test_result == 1.0 else "WARNING",
            "異常系処理のテスト"
        ))
        
        return metrics
    
    def _test_basic_functionality(self) -> float:
        """基本機能テスト"""
        try:
            # ヘルプメッセージ表示テスト
            result = subprocess.run(
                ["python", "overflow_detector_ocr.py", "--help"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "usage:" in result.stdout:
                return 1.0
            else:
                return 0.0
                
        except Exception as e:
            self.errors.append(f"基本機能テストエラー: {e}")
            return 0.0
    
    def _test_error_handling(self) -> float:
        """エラーハンドリングテスト"""
        try:
            # 存在しないファイルでのテスト
            result = subprocess.run(
                ["python", "overflow_detector_ocr.py", "nonexistent.pdf"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # エラーで終了するが、クラッシュしないことを確認
            if result.returncode != 0 and "エラー" in result.stdout:
                return 1.0
            else:
                return 0.5
                
        except Exception as e:
            self.errors.append(f"エラーハンドリングテストエラー: {e}")
            return 0.0
    
    def _run_performance_tests(self) -> List[QualityMetric]:
        """性能テスト実行"""
        metrics = []
        
        # 起動時間テスト
        startup_time = self._measure_startup_time()
        metrics.append(QualityMetric(
            "起動時間", min(1.0, 3.0 / max(startup_time, 0.1)), 0.8,
            "PASS" if startup_time <= 3.0 else "WARNING",
            f"起動時間: {startup_time:.2f}秒"
        ))
        
        return metrics
    
    def _measure_startup_time(self) -> float:
        """起動時間の測定"""
        try:
            start_time = time.time()
            result = subprocess.run(
                ["python", "overflow_detector_ocr.py", "--help"],
                cwd=self.project_root,
                capture_output=True,
                timeout=10
            )
            end_time = time.time()
            
            if result.returncode == 0:
                return end_time - start_time
            else:
                return 10.0  # エラー時はペナルティ
                
        except Exception:
            return 10.0
    
    def _run_security_check(self) -> List[QualityMetric]:
        """セキュリティチェック"""
        metrics = []
        
        # 簡易セキュリティスキャン
        security_score = self._basic_security_scan()
        metrics.append(QualityMetric(
            "セキュリティ", security_score, 0.9,
            "PASS" if security_score >= 0.9 else "WARNING",
            f"セキュリティスコア: {security_score:.2f}"
        ))
        
        return metrics
    
    def _basic_security_scan(self) -> float:
        """基本的なセキュリティスキャン"""
        try:
            ocr_impl_path = self.project_root / "overflow_detector_ocr.py"
            if not ocr_impl_path.exists():
                return 0.0
                
            with open(ocr_impl_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 危険なパターンをチェック
            dangerous_patterns = [
                "eval(",
                "exec(",
                "input(",  # 対話型入力
                "subprocess.call(",
                "os.system("
            ]
            
            issues = sum(1 for pattern in dangerous_patterns if pattern in content)
            
            # 問題が多いほどスコアが下がる
            return max(0.0, 1.0 - (issues * 0.2))
            
        except Exception as e:
            self.errors.append(f"セキュリティスキャンエラー: {e}")
            return 0.5
    
    def _calculate_overall_status(self, metrics: List[QualityMetric]) -> str:
        """総合ステータスの計算"""
        if not metrics:
            return "UNKNOWN"
            
        fail_count = sum(1 for m in metrics if m.status == "FAIL")
        warning_count = sum(1 for m in metrics if m.status == "WARNING")
        
        if fail_count > 0:
            return "FAIL"
        elif warning_count > len(metrics) * 0.3:  # 30%以上が警告
            return "WARNING"
        else:
            return "PASS"
    
    def _generate_quality_report(self, report: QualityReport):
        """品質レポートの生成"""
        print("\n" + "=" * 60)
        print("📊 品質チェック結果サマリー")
        print("=" * 60)
        
        # 総合ステータス
        status_emoji = {"PASS": "✅", "WARNING": "⚠️", "FAIL": "❌"}
        print(f"\n総合ステータス: {status_emoji.get(report.overall_status, '❓')} {report.overall_status}")
        print(f"実行時間: {report.execution_time:.2f}秒")
        
        # メトリクス詳細
        print(f"\n📈 品質メトリクス詳細:")
        for metric in report.metrics:
            status_mark = status_emoji.get(metric.status, "❓") 
            print(f"  {status_mark} {metric.name}: {metric.message}")
        
        # エラーがあれば表示
        if report.errors:
            print(f"\n⚠️ エラーログ:")
            for error in report.errors:
                print(f"  - {error}")
        
        # JSONレポート保存
        report_path = self.project_root / "quality_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': report.timestamp,
                'overall_status': report.overall_status,
                'execution_time': report.execution_time,
                'metrics': [
                    {
                        'name': m.name,
                        'value': m.value,
                        'threshold': m.threshold,
                        'status': m.status,
                        'message': m.message
                    } for m in report.metrics
                ],
                'errors': report.errors
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 詳細レポート: {report_path}")


def main():
    """メインエントリーポイント"""
    project_root = Path(__file__).parent
    checker = IntegratedQualityChecker(project_root)
    
    report = checker.run_comprehensive_check()
    
    # 終了コード設定
    if report.overall_status == "FAIL":
        sys.exit(1)
    elif report.overall_status == "WARNING":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()