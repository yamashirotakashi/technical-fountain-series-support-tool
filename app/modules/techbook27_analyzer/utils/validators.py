"""
バリデーターモジュール
単一責任: 入力値の検証
"""
import os
import zipfile
from typing import List, Optional
from pathlib import Path


class BaseValidator:
    """基底バリデータークラス"""
    
    def validate(self, value: any) -> bool:
        """検証メソッド（サブクラスで実装）"""
        raise NotImplementedError


class FileValidator(BaseValidator):
    """ファイル検証クラス"""
    
    def validate_file_exists(self, file_path: str) -> bool:
        """ファイルの存在を検証"""
        return os.path.exists(file_path) and os.path.isfile(file_path)
        
    def validate_directory_exists(self, dir_path: str) -> bool:
        """ディレクトリの存在を検証"""
        return os.path.exists(dir_path) and os.path.isdir(dir_path)
        
    def validate_zip_file(self, zip_path: str) -> bool:
        """ZIPファイルの妥当性を検証"""
        if not self.validate_file_exists(zip_path):
            return False
            
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # ZIPファイルのテスト
                bad_file = zip_ref.testzip()
                return bad_file is None
        except:
            return False


class ImageValidator(BaseValidator):
    """画像ファイル検証クラス"""
    
    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    def validate_image_file(self, image_path: str) -> bool:
        """画像ファイルの妥当性を検証"""
        path = Path(image_path)
        
        # 存在確認
        if not path.exists() or not path.is_file():
            return False
            
        # 拡張子確認
        if path.suffix.lower() not in self.VALID_EXTENSIONS:
            return False
            
        # ファイルサイズ確認
        if path.stat().st_size > self.MAX_FILE_SIZE:
            return False
            
        return True
        
    def validate_image_list(self, image_paths: List[str]) -> List[str]:
        """画像ファイルリストを検証し、有効なもののみ返す"""
        valid_paths = []
        
        for path in image_paths:
            if self.validate_image_file(path):
                valid_paths.append(path)
                
        return valid_paths


class ParameterValidator(BaseValidator):
    """パラメータ検証クラス"""
    
    def validate_resolution(self, resolution: any) -> Optional[int]:
        """解像度の検証"""
        try:
            res = int(resolution)
            if 1 <= res <= 600:  # 一般的な解像度の範囲
                return res
        except (ValueError, TypeError):
            pass
        return None
        
    def validate_max_pixels(self, max_pixels: any) -> Optional[int]:
        """最大画素数の検証（万画素単位）"""
        try:
            pixels = int(max_pixels)
            if 1 <= pixels <= 10000:  # 1万〜1億画素
                return pixels
        except (ValueError, TypeError):
            pass
        return None
        
    def validate_positive_number(self, value: any) -> Optional[float]:
        """正の数値の検証"""
        try:
            num = float(value)
            if num > 0:
                return num
        except (ValueError, TypeError):
            pass
        return None