"""Word2XHTML5フォーム設定管理モジュール"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Word2XhtmlFormSettings:
    """Word2XHTML5サービス用フォーム設定（横書きB5技術書専用）"""
    
    # 固定設定（横書きB5技術書専用）
    project_name: str = "山城技術の泉"
    layout_orientation: int = -10  # 横（B5技術書）
    cover_page: int = 0            # 扉なし
    crop_marks: int = 0            # トンボなし
    style_selection: int = 2       # 本文（ソースコード）- 横書き用 ※実際の値
    index_page: int = 0            # 索引なし
    
    # 動的設定
    email: str = ""
    email_confirm: str = ""
    
    def __post_init__(self):
        """初期化後の設定調整"""
        # メールアドレス確認の自動設定
        if self.email and not self.email_confirm:
            self.email_confirm = self.email
            
        # 環境変数からメールアドレスを取得（未設定の場合）
        if not self.email:
            self.email = os.getenv('GMAIL_ADDRESS', '')
            self.email_confirm = self.email
    
    def validate(self) -> bool:
        """設定値の妥当性チェック"""
        # メールアドレスの必須チェック
        if not self.email:
            return False
            
        # メールアドレス確認の一致チェック
        if self.email != self.email_confirm:
            return False
            
        # 基本的なメールアドレス形式チェック
        if '@' not in self.email:
            return False
        parts = self.email.split('@')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            return False
        if '.' not in parts[1] or parts[1].startswith('.') or parts[1].endswith('.'):
            return False
            
        return True
    
    def get_form_data(self) -> dict:
        """フォーム送信用のデータ辞書を取得（実際のHTML name属性に対応）"""
        return {
            'project_name': self.project_name,
            'direction': self.layout_orientation,     # 実際のname属性: direction
            'tobira': self.cover_page,               # 実際のname属性: tobira
            'tombo': self.crop_marks,                # 実際のname属性: tombo
            'syoko': self.style_selection,           # 実際のname属性: syoko (横書き用)
            'index': self.index_page,                # 実際のname属性: index
            'mail': self.email,
            'mailconf': self.email_confirm
        }
    
    @classmethod
    def create_default(cls, email: Optional[str] = None) -> 'Word2XhtmlFormSettings':
        """デフォルト設定でインスタンスを作成"""
        return cls(email=email or os.getenv('GMAIL_ADDRESS', ''))
    
    def __str__(self) -> str:
        """設定内容の文字列表現"""
        return (
            f"Word2XHTML5設定:\n"
            f"  プロジェクト名: {self.project_name}\n"
            f"  レイアウト: 横書き（B5技術書）\n"
            f"  スタイル: 本文（ソースコード）\n"
            f"  メール: {self.email}"
        )