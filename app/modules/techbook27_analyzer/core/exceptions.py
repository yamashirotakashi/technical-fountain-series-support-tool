"""
カスタム例外定義
単一責任: アプリケーション固有の例外管理
"""


class TechBookAnalyzerError(Exception):
    """基底例外クラス"""
    pass


class ProcessingInterruptedError(TechBookAnalyzerError):
    """処理が中断された場合の例外"""
    pass


class ValidationError(TechBookAnalyzerError):
    """検証エラー"""
    pass


class FileProcessingError(TechBookAnalyzerError):
    """ファイル処理エラー"""
    pass


class ImageProcessingError(TechBookAnalyzerError):
    """画像処理エラー"""
    pass


class WordProcessingError(TechBookAnalyzerError):
    """Word文書処理エラー"""
    pass