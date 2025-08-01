"""
画像処理モジュール
単一責任: 画像の変換・リサイズ・フォーマット変更処理
"""
import os
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image
import logging

from ..core.models import ProcessingOptions, ProcessingResult, ImageInfo, LogLevel
from ..core.exceptions import ImageProcessingError, ProcessingInterruptedError
from ..utils.file_handler import FileHandler
from ..utils.validators import ImageValidator


logger = logging.getLogger(__name__)


class ImageProcessor:
    """画像処理を行うクラス"""
    
    VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png')
    DEFAULT_DPI = (72, 72)
    
    def __init__(self, options: ProcessingOptions):
        """
        Args:
            options: 処理オプション
        """
        self.options = options
        self.file_handler = FileHandler()
        self.validator = ImageValidator()
        self._stop_requested = False
        
    def stop(self) -> None:
        """処理停止要求"""
        self._stop_requested = True
        
    def _check_stop(self) -> None:
        """停止要求をチェック"""
        if self._stop_requested:
            raise ProcessingInterruptedError("処理が中断されました")
            
    def process_image(self, image_path: str) -> ProcessingResult:
        """
        単一画像を処理
        
        Args:
            image_path: 画像ファイルパス
            
        Returns:
            ProcessingResult: 処理結果
        """
        result = ProcessingResult(success=True)
        
        try:
            self._check_stop()
            
            # 検証
            if not self.validator.validate_image_file(image_path):
                raise ImageProcessingError(f"無効な画像ファイル: {image_path}")
                
            # PNG→JPG変換
            if self.options.png_to_jpg and image_path.lower().endswith('.png'):
                image_path = self._convert_png_to_jpg(image_path, result)
                
            # 画像処理
            self._process_single_image(image_path, result)
            
            result.processed_count = 1
            
        except ProcessingInterruptedError:
            raise
        except Exception as e:
            logger.exception(f"画像処理エラー: {image_path}")
            result.success = False
            result.add_message(str(e), LogLevel.ERROR)
            
        return result
        
    def process_folder(self, folder_path: str) -> ProcessingResult:
        """
        フォルダ内の全画像を処理
        
        Args:
            folder_path: フォルダパス
            
        Returns:
            ProcessingResult: 処理結果
        """
        result = ProcessingResult(success=True)
        
        try:
            folder = Path(folder_path)
            if not folder.exists() or not folder.is_dir():
                raise ImageProcessingError(f"無効なフォルダ: {folder_path}")
                
            # バックアップフォルダを除外しながら画像ファイルを収集
            image_files = self._collect_image_files(folder)
            
            for image_file in image_files:
                self._check_stop()
                
                file_result = self.process_image(str(image_file))
                if file_result.success:
                    result.processed_count += 1
                else:
                    result.error_count += 1
                    
                # メッセージを統合
                result.messages.extend(file_result.messages)
                
        except ProcessingInterruptedError:
            raise
        except Exception as e:
            logger.exception("フォルダ処理エラー")
            result.success = False
            result.add_message(str(e), LogLevel.ERROR)
            
        return result
        
    def _collect_image_files(self, folder: Path) -> List[Path]:
        """画像ファイルを収集（バックアップフォルダを除外）"""
        image_files = []
        exclude_dirs = {"プロファイル除外前", "サイズ修正前", "PNG", "OVER"}
        
        for file_path in folder.rglob("*"):
            # 除外ディレクトリのチェック
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
                
            if file_path.is_file() and file_path.suffix.lower() in self.VALID_EXTENSIONS:
                image_files.append(file_path)
                
        return image_files
        
    def _convert_png_to_jpg(self, png_path: str, result: ProcessingResult) -> str:
        """PNG画像をJPGに変換"""
        try:
            # バックアップ
            if self.options.backup:
                self._backup_png_file(png_path, result)
                
            # 変換
            with Image.open(png_path) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                    
                jpg_path = os.path.splitext(png_path)[0] + ".jpg"
                dpi = (self.options.resolution, self.options.resolution) if self.options.change_resolution else self.DEFAULT_DPI
                
                img.save(jpg_path, "JPEG", dpi=dpi)
                result.add_message(f"PNG→JPG変換完了: {jpg_path}", LogLevel.INFO)
                
            # 元のPNGを削除
            os.remove(png_path)
            return jpg_path
            
        except Exception as e:
            raise ImageProcessingError(f"PNG変換エラー: {str(e)}")
            
    def _backup_png_file(self, png_path: str, result: ProcessingResult) -> None:
        """PNGファイルをバックアップ"""
        try:
            png_dir = os.path.join(os.path.dirname(png_path), "PNG")
            os.makedirs(png_dir, exist_ok=True)
            
            backup_path = os.path.join(png_dir, os.path.basename(png_path))
            shutil.copy2(png_path, backup_path)
            result.add_message(f"PNGバックアップ完了: {backup_path}", LogLevel.INFO)
            
        except Exception as e:
            result.add_message(f"PNGバックアップ失敗: {str(e)}", LogLevel.WARNING)
            
    def _process_single_image(self, image_path: str, result: ProcessingResult) -> None:
        """単一画像の処理実行"""
        try:
            with Image.open(image_path) as img:
                modified = False
                
                # 画像情報を取得
                info = ImageInfo(
                    path=image_path,
                    width=img.width,
                    height=img.height,
                    format=img.format,
                    mode=img.mode,
                    has_profile="icc_profile" in img.info
                )
                
                # カラープロファイル除去
                if self.options.remove_profile and info.has_profile:
                    img.info.pop('icc_profile')
                    modified = True
                    result.add_message("カラープロファイル除去", LogLevel.INFO)
                    
                # グレースケール変換
                if self.options.grayscale and img.mode != 'L':
                    img = img.convert('L')
                    modified = True
                    result.add_message("グレースケール変換", LogLevel.INFO)
                    
                # リサイズ
                if self.options.resize:
                    new_size = self._calculate_resize(info)
                    if new_size and new_size != (img.width, img.height):
                        img = img.resize(new_size, Image.LANCZOS)
                        modified = True
                        result.add_message(f"リサイズ: {new_size[0]}x{new_size[1]}", LogLevel.INFO)
                        
                # 保存
                if modified or self.options.change_resolution:
                    dpi = self._get_dpi_setting(img)
                    img.save(image_path, dpi=dpi)
                    result.add_message(f"保存完了: {image_path}", LogLevel.INFO)
                    
        except Exception as e:
            raise ImageProcessingError(f"画像処理エラー: {str(e)}")
            
    def _calculate_resize(self, info: ImageInfo) -> Optional[Tuple[int, int]]:
        """リサイズ後のサイズを計算"""
        try:
            max_pixels = int(self.options.max_pixels) * 10000
            current_pixels = info.pixel_count
            
            if current_pixels <= max_pixels:
                return None
                
            # アスペクト比を維持してリサイズ
            scale = (max_pixels / current_pixels) ** 0.5
            new_width = int(info.width * scale)
            new_height = int(info.height * scale)
            
            # 最大画素数を超えないよう調整
            while new_width * new_height > max_pixels and new_width > 0:
                new_width -= 1
                new_height = int(new_width / info.aspect_ratio)
                
            return (new_width, new_height)
            
        except ValueError:
            return None
            
    def _get_dpi_setting(self, img: Image.Image) -> Tuple[int, int]:
        """DPI設定を取得"""
        if self.options.change_resolution:
            return (self.options.resolution, self.options.resolution)
        else:
            return img.info.get("dpi", self.DEFAULT_DPI)