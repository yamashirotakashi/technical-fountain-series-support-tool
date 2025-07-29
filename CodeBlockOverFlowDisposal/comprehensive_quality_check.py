#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Quality Check - Phase 1実装の包括的品質検証
コード品質、セキュリティ、保守性、テスト可能性の多角的検証
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sys
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveQualityChecker:
    """包括的品質チェッカー"""
    
    def __init__(self):
        self.issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }
        
        # 主要な実装ファイル
        self.main_files = [
            'maximum_ocr_detector_v2.py',
            'maximum_ocr_detector_fixed.py', 
            'missed_page_analyzer.py',
            'threshold_optimizer.py',
            'filter_debugger.py',
            'final_optimization.py'
        ]
    
    def add_issue(self, severity: str, category: str, file: str, message: str, line: int = None):
        """問題を記録"""
        issue = {
            'category': category,
            'file': file,
            'message': message,
            'line': line
        }
        self.issues[severity].append(issue)
    
    def check_code_quality(self, file_path: Path) -> Dict:
        """コード品質チェック"""
        if not file_path.exists():
            return {'error': 'File not found'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # AST解析
            tree = ast.parse(content)
            
            # 複雑度チェック
            complexity_issues = self._check_complexity(tree, file_path.name)
            
            # 重複コードチェック
            duplication_issues = self._check_duplication(content, file_path.name)
            
            # 命名規則チェック
            naming_issues = self._check_naming_conventions(tree, file_path.name)
            
            # docstringチェック
            docstring_issues = self._check_docstrings(tree, file_path.name)
            
            return {
                'complexity': complexity_issues,
                'duplication': duplication_issues,
                'naming': naming_issues,
                'docstrings': docstring_issues
            }
            
        except Exception as e:
            self.add_issue('high', 'syntax', file_path.name, f'Parse error: {str(e)}')
            return {'error': str(e)}
    
    def _check_complexity(self, tree, filename: str) -> List[Dict]:
        """複雑度チェック"""
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.functions = []
                self.current_function = None
                
            def visit_FunctionDef(self, node):
                # McCabe複雑度の簡易計算
                complexity = self._calculate_complexity(node)
                self.functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'complexity': complexity
                })
                
                old_function = self.current_function
                self.current_function = node.name
                self.generic_visit(node)
                self.current_function = old_function
                
            def _calculate_complexity(self, node):
                """簡易McCabe複雑度計算"""
                complexity = 1  # 基本複雑度
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                        
                return complexity
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        issues = []
        for func in visitor.functions:
            if func['complexity'] > 15:  # 高複雑度
                self.add_issue('high', 'complexity', filename, 
                             f"Function '{func['name']}' has high complexity: {func['complexity']}", func['line'])
                issues.append(func)
            elif func['complexity'] > 10:  # 中複雑度
                self.add_issue('medium', 'complexity', filename,
                             f"Function '{func['name']}' has moderate complexity: {func['complexity']}", func['line'])
                issues.append(func)
                
        return issues
    
    def _check_duplication(self, content: str, filename: str) -> List[Dict]:
        """重複コードチェック"""
        lines = content.split('\n')
        duplicates = []
        
        # 5行以上の重複を検出
        for i in range(len(lines) - 5):
            block = lines[i:i+5]
            block_str = '\n'.join(block).strip()
            
            if len(block_str) < 50:  # 短すぎるブロックは無視
                continue
                
            # 後続の行で同じブロックを検索
            for j in range(i + 5, len(lines) - 5):
                other_block = lines[j:j+5]
                other_block_str = '\n'.join(other_block).strip()
                
                if block_str == other_block_str and len(block_str) > 0:
                    duplicate = {
                        'line1': i + 1,
                        'line2': j + 1,
                        'block': block_str[:100] + '...' if len(block_str) > 100 else block_str
                    }
                    duplicates.append(duplicate)
                    self.add_issue('medium', 'duplication', filename,
                                 f"Duplicate code block found at lines {i+1} and {j+1}", i+1)
                    break
                    
        return duplicates
    
    def _check_naming_conventions(self, tree, filename: str) -> List[Dict]:
        """命名規則チェック"""
        class NamingVisitor(ast.NodeVisitor):
            def __init__(self, checker):
                self.checker = checker
                self.filename = filename
                
            def visit_FunctionDef(self, node):
                # 関数名はsnake_case
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('_'):
                    self.checker.add_issue('medium', 'naming', self.filename,
                                         f"Function '{node.name}' should use snake_case", node.lineno)
                
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                # クラス名はPascalCase
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.checker.add_issue('medium', 'naming', self.filename,
                                         f"Class '{node.name}' should use PascalCase", node.lineno)
                
                self.generic_visit(node)
        
        visitor = NamingVisitor(self, filename)
        visitor.visit(tree)
        return []
    
    def _check_docstrings(self, tree, filename: str) -> List[Dict]:
        """docstringチェック"""
        class DocstringVisitor(ast.NodeVisitor):
            def __init__(self, checker):
                self.checker = checker
                self.filename = filename
                
            def visit_FunctionDef(self, node):
                # パブリック関数のdocstringチェック
                if not node.name.startswith('_'):
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        self.checker.add_issue('low', 'docstring', self.filename,
                                             f"Function '{node.name}' lacks docstring", node.lineno)
                    elif len(docstring.strip()) < 10:
                        self.checker.add_issue('low', 'docstring', self.filename,
                                             f"Function '{node.name}' has inadequate docstring", node.lineno)
                
                self.generic_visit(node)
                
            def visit_ClassDef(self, node):
                # クラスのdocstringチェック
                docstring = ast.get_docstring(node)
                if not docstring:
                    self.checker.add_issue('low', 'docstring', self.filename,
                                         f"Class '{node.name}' lacks docstring", node.lineno)
                
                self.generic_visit(node)
        
        visitor = DocstringVisitor(self, filename)
        visitor.visit(tree)
        return []
    
    def check_security(self, file_path: Path) -> Dict:
        """セキュリティチェック"""
        if not file_path.exists():
            return {'error': 'File not found'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            security_issues = []
            
            # 危険な関数呼び出しチェック
            dangerous_patterns = [
                (r'exec\s*\(', 'Use of exec() function'),
                (r'eval\s*\(', 'Use of eval() function'),
                (r'subprocess\.call\s*\(.*shell\s*=\s*True', 'Shell injection risk'),
                (r'open\s*\([^,]*,\s*["\']w', 'File overwrite without validation'),
                (r'import\s+os.*system', 'Use of os.system()'),
            ]
            
            for pattern, message in dangerous_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_no = content[:match.start()].count('\n') + 1
                    self.add_issue('high', 'security', file_path.name, message, line_no)
                    security_issues.append({'pattern': pattern, 'message': message, 'line': line_no})
            
            # ハードコーディングされた秘密情報チェック
            secret_patterns = [
                (r'password\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
                (r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
                (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded secret'),
            ]
            
            for pattern, message in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_no = content[:match.start()].count('\n') + 1
                    self.add_issue('critical', 'security', file_path.name, message, line_no)
                    security_issues.append({'pattern': pattern, 'message': message, 'line': line_no})
            
            return {'issues': security_issues}
            
        except Exception as e:
            self.add_issue('medium', 'security', file_path.name, f'Security check error: {str(e)}')
            return {'error': str(e)}
    
    def check_maintainability(self, file_path: Path) -> Dict:
        """保守性チェック"""
        if not file_path.exists():
            return {'error': 'File not found'}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            maintainability_issues = []
            
            # ファイルサイズチェック
            if len(lines) > 500:
                self.add_issue('medium', 'maintainability', file_path.name,
                             f'File is large ({len(lines)} lines), consider splitting')
                maintainability_issues.append({'type': 'file_size', 'lines': len(lines)})
            
            # 長い行チェック
            for i, line in enumerate(lines):
                if len(line) > 120:
                    self.add_issue('low', 'maintainability', file_path.name,
                                 f'Line {i+1} is too long ({len(line)} chars)', i+1)
            
            # TODO/FIXME/HACKコメントチェック
            todo_patterns = [
                (r'#.*TODO', 'TODO comment found'),
                (r'#.*FIXME', 'FIXME comment found'),
                (r'#.*HACK', 'HACK comment found'),
                (r'#.*XXX', 'XXX comment found'),
            ]
            
            for pattern, message in todo_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_no = content[:match.start()].count('\n') + 1
                    self.add_issue('info', 'maintainability', file_path.name, message, line_no)
            
            return {'issues': maintainability_issues, 'lines': len(lines)}
            
        except Exception as e:
            self.add_issue('medium', 'maintainability', file_path.name, f'Maintainability check error: {str(e)}')
            return {'error': str(e)}
    
    def check_test_coverage(self) -> Dict:
        """テストカバレッジ評価"""
        test_files = list(Path('.').glob('*test*.py'))
        
        # 主要機能のテスト存在チェック
        critical_functions = [
            'detect_overflows',
            'is_likely_false_positive',
            'analyze_page_details',
            'calculate_metrics'
        ]
        
        test_coverage = {}
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for func in critical_functions:
                    if func in content:
                        test_coverage[func] = test_coverage.get(func, []) + [test_file.name]
            except Exception:
                continue
        
        # カバレッジ不足の警告
        for func in critical_functions:
            if func not in test_coverage:
                self.add_issue('medium', 'testing', 'general',
                             f'Critical function "{func}" lacks dedicated tests')
        
        return {
            'test_files': [f.name for f in test_files],
            'coverage': test_coverage,
            'missing_tests': [f for f in critical_functions if f not in test_coverage]
        }
    
    def run_comprehensive_check(self):
        """包括的品質チェック実行"""
        logger.info("=" * 90)
        logger.info("CodeBlockOverFlowDisposal Phase 1 - 包括的品質チェック")
        logger.info("=" * 90)
        
        # 各ファイルの品質チェック
        for filename in self.main_files:
            file_path = Path(filename)
            if not file_path.exists():
                self.add_issue('high', 'general', filename, 'File not found')
                continue
                
            logger.info(f"\n🔍 {filename} 品質チェック:")
            logger.info("-" * 60)
            
            # コード品質
            quality_result = self.check_code_quality(file_path)
            if 'error' not in quality_result:
                logger.info(f"  ✅ コード品質: 解析完了")
            else:
                logger.info(f"  ❌ コード品質: {quality_result['error']}")
            
            # セキュリティ
            security_result = self.check_security(file_path)
            if 'error' not in security_result:
                logger.info(f"  ✅ セキュリティ: 検査完了")
            else:
                logger.info(f"  ❌ セキュリティ: {security_result['error']}")
            
            # 保守性
            maintain_result = self.check_maintainability(file_path)
            if 'error' not in maintain_result:
                lines = maintain_result.get('lines', 0)
                logger.info(f"  ✅ 保守性: {lines}行, 検査完了")
            else:
                logger.info(f"  ❌ 保守性: {maintain_result['error']}")
        
        # テストカバレッジ
        logger.info(f"\n🧪 テストカバレッジ評価:")
        logger.info("-" * 60)
        test_result = self.check_test_coverage()
        logger.info(f"  テストファイル数: {len(test_result['test_files'])}")
        logger.info(f"  カバレッジ不足機能: {len(test_result['missing_tests'])}")
        
        # 総合レポート
        self.print_summary_report()
    
    def print_summary_report(self):
        """総合レポート出力"""
        logger.info(f"\n📊 品質チェック総合レポート:")
        logger.info("=" * 70)
        
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        logger.info(f"総問題数: {total_issues}")
        for severity, issues in self.issues.items():
            if issues:
                logger.info(f"  {severity.upper()}: {len(issues)}件")
        
        # 重要度別詳細
        for severity in ['critical', 'high', 'medium']:
            if self.issues[severity]:
                logger.info(f"\n{severity.upper()}問題の詳細:")
                logger.info("-" * 40)
                for issue in self.issues[severity][:5]:  # 最初の5件のみ表示
                    line_info = f" (行{issue['line']})" if issue['line'] else ""
                    logger.info(f"  [{issue['category']}] {issue['file']}{line_info}: {issue['message']}")
                if len(self.issues[severity]) > 5:
                    logger.info(f"  ... 他{len(self.issues[severity]) - 5}件")
        
        # 品質評価
        logger.info(f"\n🏆 総合品質評価:")
        logger.info("-" * 40)
        
        critical_count = len(self.issues['critical'])
        high_count = len(self.issues['high'])
        medium_count = len(self.issues['medium'])
        
        if critical_count == 0 and high_count == 0:
            if medium_count <= 5:
                logger.info("  ✅ 優秀 - 本番運用可能")
            else:
                logger.info("  🟡 良好 - 軽微な改善推奨")
        elif critical_count == 0 and high_count <= 2:
            logger.info("  🟡 可 - 改善推奨")
        else:
            logger.info("  🔴 要改善 - 重要な問題あり")
        
        # 推奨アクション
        logger.info(f"\n💡 推奨アクション:")
        if critical_count > 0:
            logger.info("  1. CRITICAL問題の即座の修正")
        if high_count > 0:
            logger.info("  2. HIGH問題の優先的な修正")
        if medium_count > 10:
            logger.info("  3. MEDIUM問題の段階的な改善")
        if not self.issues['critical'] and not self.issues['high']:
            logger.info("  現在の品質レベルで本番運用可能")
        
        logger.info("=" * 90)

def main():
    """メイン実行"""
    checker = ComprehensiveQualityChecker()
    checker.run_comprehensive_check()

if __name__ == "__main__":
    main()