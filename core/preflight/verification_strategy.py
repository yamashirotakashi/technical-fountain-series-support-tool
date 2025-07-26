"""検証戦略パターンの実装"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .file_validator import ValidationResult


class VerificationMode(Enum):
    """検証モード"""
    QUICK = "quick"           # 高速検証（基本チェックのみ）
    STANDARD = "standard"     # 標準検証（通常の全チェック）
    THOROUGH = "thorough"     # 徹底検証（詳細セキュリティチェック含む）
    CUSTOM = "custom"         # カスタム検証（ユーザー定義）


@dataclass
class VerificationConfig:
    """検証設定"""
    mode: VerificationMode
    enable_file_validation: bool = True
    enable_security_check: bool = True
    enable_content_analysis: bool = False
    max_file_size_mb: int = 50
    allowed_extensions: List[str] = None
    custom_patterns: List[str] = None
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = ['.docx', '.doc']
        if self.custom_patterns is None:
            self.custom_patterns = []


@dataclass
class VerificationResult:
    """検証結果の統合"""
    success: bool
    mode: VerificationMode
    file_results: Dict[str, ValidationResult]
    security_issues: List[str]
    warnings: List[str]
    statistics: Dict[str, Any]
    execution_time_seconds: float
    
    @property
    def total_files(self) -> int:
        return len(self.file_results)
    
    @property
    def valid_files(self) -> int:
        return sum(1 for result in self.file_results.values() if result.is_valid)
    
    @property
    def invalid_files(self) -> int:
        return self.total_files - self.valid_files
    
    @property
    def has_security_issues(self) -> bool:
        return len(self.security_issues) > 0


class VerificationStrategy(ABC):
    """検証戦略の抽象基底クラス"""
    
    def __init__(self, config: VerificationConfig):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, file_paths: List[str]) -> VerificationResult:
        """検証を実行
        
        Args:
            file_paths: 検証対象のファイルパスリスト
            
        Returns:
            検証結果
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """戦略の説明を返す"""
        pass
    
    def _create_base_result(self, file_paths: List[str], execution_time: float) -> VerificationResult:
        """基本的な結果オブジェクトを作成"""
        return VerificationResult(
            success=False,  # サブクラスで更新
            mode=self.config.mode,
            file_results={},
            security_issues=[],
            warnings=[],
            statistics={},
            execution_time_seconds=execution_time
        )


class QuickVerificationStrategy(VerificationStrategy):
    """高速検証戦略 - 基本チェックのみ"""
    
    def execute(self, file_paths: List[str]) -> VerificationResult:
        import time
        from .file_validator import WordFileValidator
        
        start_time = time.time()
        validator = WordFileValidator()
        
        # 最低限の検証のみ実行
        file_results = {}
        security_issues = []
        warnings = []
        
        for file_path in file_paths:
            # ファイル存在とサイズのみチェック
            try:
                from pathlib import Path
                path_obj = Path(file_path)
                
                if not path_obj.exists():
                    # 簡易的な結果作成
                    file_results[file_path] = ValidationResult(
                        is_valid=False,
                        file_path=file_path,
                        file_size=0,
                        mime_type="",
                        issues=["ファイルが存在しません"],
                        warnings=[]
                    )
                else:
                    file_size = path_obj.stat().st_size
                    max_size = self.config.max_file_size_mb * 1024 * 1024
                    
                    issues = []
                    if file_size > max_size:
                        issues.append(f"ファイルサイズ超過: {file_size} bytes")
                    
                    # 拡張子チェック
                    if path_obj.suffix.lower() not in self.config.allowed_extensions:
                        issues.append(f"許可されていない拡張子: {path_obj.suffix}")
                    
                    file_results[file_path] = ValidationResult(
                        is_valid=len(issues) == 0,
                        file_path=file_path,
                        file_size=file_size,
                        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        issues=issues,
                        warnings=[]
                    )
                    
            except Exception as e:
                file_results[file_path] = ValidationResult(
                    is_valid=False,
                    file_path=file_path,
                    file_size=0,
                    mime_type="",
                    issues=[f"検証エラー: {str(e)}"],
                    warnings=[]
                )
        
        execution_time = time.time() - start_time
        
        return VerificationResult(
            success=all(result.is_valid for result in file_results.values()),
            mode=self.config.mode,
            file_results=file_results,
            security_issues=security_issues,
            warnings=warnings,
            statistics={
                'total_files': len(file_paths),
                'processing_time_per_file': execution_time / len(file_paths) if file_paths else 0
            },
            execution_time_seconds=execution_time
        )
    
    def get_description(self) -> str:
        return "高速検証: ファイル存在、サイズ、拡張子の基本チェックのみ"


class StandardVerificationStrategy(VerificationStrategy):
    """標準検証戦略 - 通常の全チェック"""
    
    def execute(self, file_paths: List[str]) -> VerificationResult:
        import time
        from .file_validator import WordFileValidator
        
        start_time = time.time()
        validator = WordFileValidator()
        
        # 通常の検証を実行
        file_results = validator.validate_batch(file_paths)
        security_issues = []
        warnings = []
        
        # セキュリティ問題の集約
        for result in file_results.values():
            for issue in result.issues:
                if any(keyword in issue for keyword in ['危険', 'セキュリティ', 'マクロ']):
                    security_issues.append(f"{result.file_path}: {issue}")
            warnings.extend(result.warnings)
        
        execution_time = time.time() - start_time
        summary = validator.get_validation_summary(file_results)
        
        return VerificationResult(
            success=all(result.is_valid for result in file_results.values()),
            mode=self.config.mode,
            file_results=file_results,
            security_issues=security_issues,
            warnings=warnings,
            statistics=summary,
            execution_time_seconds=execution_time
        )
    
    def get_description(self) -> str:
        return "標準検証: ファイル構造、セキュリティ、MIME型の包括的チェック"


class ThoroughVerificationStrategy(VerificationStrategy):
    """徹底検証戦略 - 詳細セキュリティチェック含む"""
    
    def execute(self, file_paths: List[str]) -> VerificationResult:
        import time
        from .file_validator import WordFileValidator
        
        start_time = time.time()
        validator = WordFileValidator()
        
        # 標準検証 + 追加セキュリティチェック
        file_results = validator.validate_batch(file_paths)
        security_issues = []
        warnings = []
        
        # 追加のセキュリティ分析
        for file_path, result in file_results.items():
            if result.is_valid and file_path.endswith('.docx'):
                additional_issues = self._perform_deep_security_check(file_path)
                security_issues.extend(additional_issues)
            
            # 既存の問題を分類
            for issue in result.issues:
                if any(keyword in issue for keyword in ['危険', 'セキュリティ', 'マクロ', 'スクリプト']):
                    security_issues.append(f"{file_path}: {issue}")
            
            warnings.extend([f"{file_path}: {w}" for w in result.warnings])
        
        execution_time = time.time() - start_time
        summary = validator.get_validation_summary(file_results)
        
        # 統計に詳細情報を追加
        summary.update({
            'deep_security_checks': len(file_paths),
            'security_issues_found': len(security_issues),
            'warnings_total': len(warnings)
        })
        
        return VerificationResult(
            success=all(result.is_valid for result in file_results.values()) and len(security_issues) == 0,
            mode=self.config.mode,
            file_results=file_results,
            security_issues=security_issues,
            warnings=warnings,
            statistics=summary,
            execution_time_seconds=execution_time
        )
    
    def _perform_deep_security_check(self, file_path: str) -> List[str]:
        """詳細セキュリティチェックを実行"""
        issues = []
        
        try:
            import zipfile
            from pathlib import Path
            
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                namelist = zip_file.namelist()
                
                # 詳細なファイル分析
                suspicious_files = [
                    name for name in namelist 
                    if any(pattern in name.lower() for pattern in [
                        'macro', 'vba', 'script', 'active', 'ole'
                    ])
                ]
                
                if suspicious_files:
                    issues.append(f"疑わしいファイル検出: {', '.join(suspicious_files[:3])}")
                
                # メタデータ分析
                try:
                    doc_props = zip_file.read('docProps/core.xml').decode('utf-8', errors='ignore')
                    if '<dc:creator>' in doc_props and 'unknown' not in doc_props.lower():
                        issues.append("作成者情報が含まれています（プライバシー注意）")
                except:
                    pass
                
                # 外部参照チェック
                external_refs = [
                    name for name in namelist
                    if name.startswith('word/embeddings/') or 'external' in name.lower()
                ]
                
                if external_refs:
                    issues.append(f"外部参照検出: {len(external_refs)}件")
                    
        except Exception as e:
            issues.append(f"詳細分析エラー: {str(e)}")
        
        return issues
    
    def get_description(self) -> str:
        return "徹底検証: 標準チェック + 詳細セキュリティ分析、メタデータ検査"


class CustomVerificationStrategy(VerificationStrategy):
    """カスタム検証戦略 - ユーザー定義ルール"""
    
    def execute(self, file_paths: List[str]) -> VerificationResult:
        import time
        from .file_validator import WordFileValidator
        
        start_time = time.time()
        validator = WordFileValidator()
        
        # 基本検証を実行
        file_results = validator.validate_batch(file_paths)
        security_issues = []
        warnings = []
        
        # カスタムパターンによる追加チェック
        for file_path, result in file_results.items():
            custom_issues = self._apply_custom_patterns(file_path, result)
            security_issues.extend(custom_issues)
        
        execution_time = time.time() - start_time
        summary = validator.get_validation_summary(file_results)
        
        return VerificationResult(
            success=all(result.is_valid for result in file_results.values()),
            mode=self.config.mode,
            file_results=file_results,
            security_issues=security_issues,
            warnings=warnings,
            statistics=summary,
            execution_time_seconds=execution_time
        )
    
    def _apply_custom_patterns(self, file_path: str, result: ValidationResult) -> List[str]:
        """カスタムパターンを適用"""
        issues = []
        
        # ファイル名パターンチェック
        from pathlib import Path
        filename = Path(file_path).name.lower()
        
        for pattern in self.config.custom_patterns:
            if pattern.lower() in filename:
                issues.append(f"カスタムパターン検出: {pattern}")
        
        return issues
    
    def get_description(self) -> str:
        patterns_str = ', '.join(self.config.custom_patterns[:3])
        return f"カスタム検証: ユーザー定義パターン ({patterns_str}...)"


class VerificationStrategyFactory:
    """検証戦略のファクトリクラス"""
    
    _strategies = {
        VerificationMode.QUICK: QuickVerificationStrategy,
        VerificationMode.STANDARD: StandardVerificationStrategy,
        VerificationMode.THOROUGH: ThoroughVerificationStrategy,
        VerificationMode.CUSTOM: CustomVerificationStrategy,
    }
    
    @classmethod
    def create_strategy(cls, config: VerificationConfig) -> VerificationStrategy:
        """設定に基づいて適切な戦略を作成
        
        Args:
            config: 検証設定
            
        Returns:
            検証戦略インスタンス
        """
        strategy_class = cls._strategies.get(config.mode)
        if not strategy_class:
            raise ValueError(f"未知の検証モード: {config.mode}")
        
        return strategy_class(config)
    
    @classmethod
    def get_available_modes(cls) -> List[VerificationMode]:
        """利用可能な検証モードを取得"""
        return list(cls._strategies.keys())
    
    @classmethod
    def get_mode_descriptions(cls) -> Dict[VerificationMode, str]:
        """各モードの説明を取得"""
        descriptions = {}
        for mode, strategy_class in cls._strategies.items():
            # デフォルト設定で一時的にインスタンス作成
            temp_config = VerificationConfig(mode=mode)
            temp_strategy = strategy_class(temp_config)
            descriptions[mode] = temp_strategy.get_description()
        return descriptions