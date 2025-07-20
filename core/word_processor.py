"""Word文書処理モジュール"""
from pathlib import Path
from typing import List
import docx

from utils.logger import get_logger


class WordProcessor:
    """Word文書を処理するクラス"""
    
    def __init__(self):
        """WordProcessorを初期化"""
        self.logger = get_logger(__name__)
    
    def process_word_files(self, folder_path: Path) -> int:
        """
        フォルダ内のすべてのWordファイルを処理
        
        Args:
            folder_path: 処理するフォルダのパス
        
        Returns:
            処理したファイル数
        """
        self.logger.info(f"Word処理開始: {folder_path}")
        
        if not folder_path.exists():
            self.logger.error(f"フォルダが存在しません: {folder_path}")
            return 0
        
        # .docxファイルを検索
        word_files = list(folder_path.glob("**/*.docx"))
        
        if not word_files:
            self.logger.warning("Wordファイルが見つかりませんでした")
            return 0
        
        processed_count = 0
        for word_file in word_files:
            try:
                if self.remove_first_line(word_file):
                    processed_count += 1
            except Exception as e:
                self.logger.error(f"ファイル処理エラー {word_file}: {e}")
        
        self.logger.info(f"Word処理完了: {processed_count}/{len(word_files)} ファイル")
        return processed_count
    
    def remove_first_line(self, doc_path: Path) -> bool:
        """
        Word文書の1行目を削除
        
        Args:
            doc_path: 処理するWord文書のパス
        
        Returns:
            処理が成功した場合True
        """
        try:
            self.logger.info(f"1行目削除処理: {doc_path}")
            
            # ドキュメントを開く
            doc = docx.Document(doc_path)
            
            # パラグラフが存在するか確認
            if not doc.paragraphs:
                self.logger.warning(f"空のドキュメント: {doc_path}")
                return True
            
            # 最初のパラグラフを削除
            first_para = doc.paragraphs[0]
            p = first_para._element
            p.getparent().remove(p)
            
            # 保存
            doc.save(doc_path)
            
            self.logger.info(f"1行目を削除しました: {doc_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"1行目削除エラー {doc_path}: {e}")
            return False
    
    def get_word_files(self, folder_path: Path) -> List[Path]:
        """
        フォルダ内のWordファイルのリストを取得
        
        Args:
            folder_path: 検索するフォルダのパス
        
        Returns:
            Wordファイルのパスリスト
        """
        if not folder_path.exists():
            return []
        
        return list(folder_path.glob("**/*.docx"))