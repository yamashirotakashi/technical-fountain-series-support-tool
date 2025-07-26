"""Word文書ファイルの検証モジュール"""
import os
import zipfile
import mimetypes
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from utils.logger import get_logger


@dataclass
class ValidationResult:
    """ファイル検証結果"""
    is_valid: bool
    file_path: str
    file_size: int
    mime_type: str
    issues: List[str]
    warnings: List[str]
    
    @property
    def has_issues(self) -> bool:
        """重大な問題があるかどうか"""
        return len(self.issues) > 0
        
    @property
    def has_warnings(self) -> bool:
        """警告があるかどうか"""
        return len(self.warnings) > 0


class WordFileValidator:
    """Word文書ファイルの安全性検証クラス"""
    
    # ファイルサイズ制限
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    MIN_FILE_SIZE = 512  # 512 bytes（テスト用DOCXファイルを考慮）
    
    # 許可されるMIMEタイプ
    ALLOWED_MIME_TYPES = {
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'application/msword',  # .doc（古い形式）
    }
    
    # 許可される拡張子
    ALLOWED_EXTENSIONS = {'.docx', '.doc'}
    
    # 危険なファイル名パターン
    DANGEROUS_PATTERNS = [
        '../',  # ディレクトリトラバーサル
        '..\\',
        '<script',  # スクリプトタグ
        'javascript:',
        'vbscript:',
        'data:',
        'file://',
        'ftp://',
        'http://',
        'https://',
    ]
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def validate_single(self, file_path: str) -> ValidationResult:
        """単一ファイルの検証
        
        Args:
            file_path: 検証対象のファイルパス
            
        Returns:
            検証結果
        """
        issues = []
        warnings = []
        
        try:
            path_obj = Path(file_path)
            
            # ファイル存在確認
            if not path_obj.exists():
                issues.append(f"ファイルが存在しません: {file_path}")
                return ValidationResult(
                    is_valid=False,
                    file_path=file_path,
                    file_size=0,
                    mime_type="",
                    issues=issues,
                    warnings=warnings
                )
            
            # ファイルサイズ確認
            file_size = path_obj.stat().st_size
            if file_size > self.MAX_FILE_SIZE:
                issues.append(f"ファイルサイズが制限を超過: {file_size:,} bytes (制限: {self.MAX_FILE_SIZE:,} bytes)")
            elif file_size < self.MIN_FILE_SIZE:
                issues.append(f"ファイルサイズが小さすぎます: {file_size} bytes (最小: {self.MIN_FILE_SIZE} bytes)")
            
            # 拡張子確認
            file_extension = path_obj.suffix.lower()
            if file_extension not in self.ALLOWED_EXTENSIONS:
                issues.append(f"許可されていない拡張子: {file_extension}")
            
            # MIMEタイプ確認
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type not in self.ALLOWED_MIME_TYPES:
                # 拡張子ベースでの再確認
                if file_extension == '.docx':
                    mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                elif file_extension == '.doc':
                    mime_type = 'application/msword'
                else:
                    issues.append(f"許可されていないMIMEタイプ: {mime_type}")
            
            # ファイル名の安全性確認
            filename = path_obj.name
            for pattern in self.DANGEROUS_PATTERNS:
                if pattern.lower() in filename.lower():
                    issues.append(f"危険なファイル名パターン: {pattern}")
            
            # Word文書の内部構造検証（.docxのみ）
            if file_extension == '.docx' and len(issues) == 0:
                docx_issues, docx_warnings = self._validate_docx_structure(file_path)
                issues.extend(docx_issues)
                warnings.extend(docx_warnings)
            
            # ファイル読み取り権限確認
            if not os.access(file_path, os.R_OK):
                issues.append("ファイルに読み取り権限がありません")
            
            # 結果判定
            is_valid = len(issues) == 0
            
            self.logger.info(f"ファイル検証完了: {file_path} - {'有効' if is_valid else '無効'}")
            if issues:
                self.logger.warning(f"検証問題: {', '.join(issues)}")
            if warnings:
                self.logger.info(f"検証警告: {', '.join(warnings)}")
            
            return ValidationResult(
                is_valid=is_valid,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type or "",
                issues=issues,
                warnings=warnings
            )
            
        except Exception as e:
            self.logger.error(f"ファイル検証エラー: {file_path} - {e}", exc_info=True)
            issues.append(f"検証処理エラー: {str(e)}")
            
            return ValidationResult(
                is_valid=False,
                file_path=file_path,
                file_size=0,
                mime_type="",
                issues=issues,
                warnings=warnings
            )
    
    def _validate_docx_structure(self, file_path: str) -> Tuple[List[str], List[str]]:
        """DOCX形式の内部構造を検証
        
        Args:
            file_path: DOCXファイルのパス
            
        Returns:
            (issues, warnings)のタプル
        """
        issues = []
        warnings = []
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # 必須ファイルの存在確認
                required_files = [
                    '[Content_Types].xml',
                    '_rels/.rels',
                    'word/document.xml'
                ]
                
                zip_namelist = zip_file.namelist()
                
                for required_file in required_files:
                    if required_file not in zip_namelist:
                        issues.append(f"必須ファイルが不足: {required_file}")
                
                # 危険なファイルの検出
                dangerous_files = []
                for file_name in zip_namelist:
                    # マクロファイルの検出
                    if file_name.startswith('word/vbaProject'):
                        warnings.append("VBAマクロが含まれています")
                    
                    # 外部参照の検出
                    if file_name.startswith('word/embeddings/'):
                        warnings.append("埋め込みオブジェクトが含まれています")
                    
                    # 危険なパスの検出
                    if '../' in file_name or '..\\' in file_name:
                        issues.append(f"危険なファイルパス: {file_name}")
                
                # ZIPボム検証（展開サイズ確認）
                total_uncompressed_size = sum(info.file_size for info in zip_file.infolist())
                compressed_size = os.path.getsize(file_path)
                
                if total_uncompressed_size > compressed_size * 100:  # 100倍以上の展開率
                    warnings.append(f"高い圧縮率を検出: {total_uncompressed_size/compressed_size:.1f}倍")
                
                if total_uncompressed_size > 500 * 1024 * 1024:  # 500MB
                    warnings.append(f"展開後サイズが大きい: {total_uncompressed_size:,} bytes")
                
        except zipfile.BadZipFile:
            issues.append("不正なZIPファイル形式")
        except Exception as e:
            warnings.append(f"内部構造検証エラー: {str(e)}")
        
        return issues, warnings
    
    def validate_batch(self, file_paths: List[str]) -> Dict[str, ValidationResult]:
        """複数ファイルの一括検証
        
        Args:
            file_paths: 検証対象のファイルパスリスト
            
        Returns:
            ファイルパス -> 検証結果の辞書
        """
        results = {}
        
        self.logger.info(f"バッチ検証開始: {len(file_paths)}ファイル")
        
        for i, file_path in enumerate(file_paths, 1):
            self.logger.info(f"検証中 ({i}/{len(file_paths)}): {file_path}")
            results[file_path] = self.validate_single(file_path)
        
        # 統計情報のログ出力
        valid_count = sum(1 for result in results.values() if result.is_valid)
        invalid_count = len(results) - valid_count
        warning_count = sum(1 for result in results.values() if result.has_warnings)
        
        self.logger.info(
            f"バッチ検証完了: 有効 {valid_count}, 無効 {invalid_count}, 警告 {warning_count}"
        )
        
        return results
    
    def get_validation_summary(self, results: Dict[str, ValidationResult]) -> Dict[str, any]:
        """検証結果のサマリーを生成
        
        Args:
            results: validate_batchの結果
            
        Returns:
            サマリー情報の辞書
        """
        total_files = len(results)
        valid_files = [r for r in results.values() if r.is_valid]
        invalid_files = [r for r in results.values() if not r.is_valid]
        warning_files = [r for r in results.values() if r.has_warnings]
        
        total_size = sum(r.file_size for r in results.values())
        
        all_issues = []
        all_warnings = []
        
        for result in results.values():
            all_issues.extend(result.issues)
            all_warnings.extend(result.warnings)
        
        return {
            'total_files': total_files,
            'valid_count': len(valid_files),
            'invalid_count': len(invalid_files),
            'warning_count': len(warning_files),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'all_issues': all_issues,
            'all_warnings': all_warnings,
            'invalid_files': [r.file_path for r in invalid_files],
            'warning_files': [r.file_path for r in warning_files]
        }