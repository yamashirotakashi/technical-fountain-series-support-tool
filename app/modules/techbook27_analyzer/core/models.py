"""
データモデル定義
単一責任: データ構造の定義と検証
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class ProcessingMode(Enum):
    """処理モードの列挙型"""
    FOLDER = "folder"
    FILE = "file"


class LogLevel(Enum):
    """ログレベルの列挙型"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


@dataclass
class ProcessingOptions:
    """画像処理オプションを管理するデータクラス"""
    remove_profile: bool = False
    grayscale: bool = False
    change_resolution: bool = True
    resize: bool = True
    backup: bool = True
    png_to_jpg: bool = True
    max_pixels: str = "400"
    resolution: int = 100

    def to_dict(self) -> Dict[str, Any]:
        """オプションを辞書形式に変換"""
        return {
            "remove_profile": self.remove_profile,
            "grayscale": self.grayscale,
            "change_resolution": self.change_resolution,
            "resize": self.resize,
            "backup": self.backup,
            "png_to_jpg": self.png_to_jpg,
            "max_pixels": self.max_pixels,
            "resolution": self.resolution
        }

    def validate(self) -> List[str]:
        """オプションの妥当性を検証"""
        errors = []
        
        try:
            pixels = int(self.max_pixels)
            if pixels <= 0:
                errors.append("最大画素数は正の数である必要があります")
        except ValueError:
            errors.append("最大画素数は数値である必要があります")
            
        if self.resolution <= 0:
            errors.append("解像度は正の数である必要があります")
            
        return errors


@dataclass
class ProcessingResult:
    """処理結果を格納するデータクラス"""
    success: bool
    processed_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    messages: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, message: str, level: LogLevel = LogLevel.INFO) -> None:
        """メッセージを追加"""
        self.messages.append(f"[{level.value}] {message}")
        
        if level == LogLevel.ERROR:
            self.error_count += 1
        elif level == LogLevel.WARNING:
            self.warning_count += 1


@dataclass
class ImageInfo:
    """画像情報を格納するデータクラス"""
    path: str
    width: int
    height: int
    format: str
    mode: str
    has_profile: bool = False
    file_size: int = 0
    
    @property
    def pixel_count(self) -> int:
        """総画素数を計算"""
        return self.width * self.height
        
    @property
    def aspect_ratio(self) -> float:
        """アスペクト比を計算"""
        return self.width / self.height if self.height > 0 else 0