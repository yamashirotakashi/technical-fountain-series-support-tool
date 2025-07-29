#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Filter Debugger - 誤検知フィルタの詳細デバッグ
sample4.pdf Page 38の1.160ptはみ出しが検出されない原因を調査
"""

import logging
from pathlib import Path
from typing import Dict
import sys

try:
    import pdfplumber
except ImportError:
    print("pdfplumber not available.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class FilterDebugger:
    """フィルタデバッグ"""
    
    def __init__(self):
        self.mm_to_pt = 2.83465
    
    def is_ascii_char(self, char: str) -> bool:
        """ASCII文字判定"""
        if not char or len(char) == 0:
            return False
        return ord(char[0]) < 128
    
    def debug_filter_step_by_step(self, overflow_text: str, overflow_amount: float, y_position: float) -> Dict:
        """ステップバイステップでフィルタを検証"""
        text_content = overflow_text.strip()
        text_length = len(overflow_text)
        
        debug_info = {
            'overflow_text': overflow_text,
            'overflow_amount': overflow_amount,
            'y_position': y_position,
            'text_content': text_content,
            'text_length': text_length,
            'filter_results': {}
        }
        
        # フィルタ1: 極めて小さいはみ出し量（0.5pt以下）
        filter1 = overflow_amount <= 0.5
        debug_info['filter_results']['小さいはみ出し(<=0.5pt)'] = {
            'triggered': filter1,
            'value': overflow_amount,
            'threshold': 0.5
        }
        
        # フィルタ2: (cid:X)文字
        filter2 = '(cid:' in text_content
        debug_info['filter_results']['(cid:X)文字'] = {
            'triggered': filter2,
            'contains_cid': filter2
        }
        
        # フィルタ3: ページ番号のみ
        filter3 = text_content.isdigit() and len(text_content) <= 3
        debug_info['filter_results']['ページ番号'] = {
            'triggered': filter3,
            'is_digit': text_content.isdigit(),
            'length_le_3': len(text_content) <= 3
        }
        
        # フィルタ4: 日本語文字のみ
        filter4 = all(ord(c) > 127 for c in text_content if c.isprintable())
        debug_info['filter_results']['日本語のみ'] = {
            'triggered': filter4,
            'char_analysis': [(c, ord(c), ord(c) > 127) for c in text_content if c.isprintable()]
        }
        
        # フィルタ5: PowerShell特有パターン
        filter5 = '::' in text_content and text_length > 10
        debug_info['filter_results']['PowerShellパターン'] = {
            'triggered': filter5,
            'contains_colon': '::' in text_content,
            'length_gt_10': text_length > 10
        }
        
        # フィルタ6: .ps1拡張子
        filter6 = '.ps1' in text_content
        debug_info['filter_results']['.ps1拡張子'] = {
            'triggered': filter6
        }
        
        # フィルタ7: 極端に短いテキストかつ記号のみ
        filter7 = text_length <= 2 and all(not c.isalnum() for c in text_content)
        debug_info['filter_results']['短いテキスト+記号のみ'] = {
            'triggered': filter7,
            'length_le_2': text_length <= 2,
            'all_non_alnum': all(not c.isalnum() for c in text_content),
            'char_analysis': [(c, c.isalnum()) for c in text_content]
        }
        
        # フィルタ8: 画像・線要素タグ
        filter8 = (text_content.startswith('[IMAGE:') or 
                  text_content.startswith('[LINE]') or 
                  text_content.startswith('[RECT:'))
        debug_info['filter_results']['画像・線要素タグ'] = {
            'triggered': filter8
        }
        
        # フィルタ9: 目次・索引パターン
        filter9 = '……' in text_content or '・・・' in text_content
        debug_info['filter_results']['目次・索引パターン'] = {
            'triggered': filter9
        }
        
        # 最終判定
        is_filtered = any([filter1, filter2, filter3, filter4, filter5, filter6, filter7, filter8, filter9])
        debug_info['final_decision'] = {
            'is_filtered_out': is_filtered,
            'triggered_filters': [name for name, result in debug_info['filter_results'].items() if result['triggered']]
        }
        
        return debug_info
    
    def debug_specific_page(self, pdf_path: Path, page_number: int):
        """特定ページの詳細デバッグ"""
        logger.info(f"=" * 90)
        logger.info(f"フィルタデバッグ: {pdf_path.name} Page {page_number}")
        logger.info(f"=" * 90)
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if page_number > len(pdf.pages):
                    logger.info(f"❌ Page {page_number} not found")
                    return
                
                page = pdf.pages[page_number - 1]
                
                # マージン計算
                if page_number % 2 == 1:  # 奇数ページ
                    right_margin_pt = 10 * self.mm_to_pt
                else:  # 偶数ページ
                    right_margin_pt = 18 * self.mm_to_pt
                
                text_right_edge = page.width - right_margin_pt
                
                logger.info(f"ページ情報:")
                logger.info(f"  サイズ: {page.width:.1f} x {page.height:.1f}pt")
                logger.info(f"  右マージン: {right_margin_pt:.1f}pt")
                logger.info(f"  テキスト右端: {text_right_edge:.1f}pt")
                
                # 全はみ出し候補を収集（フィルタ無し）
                potential_overflows = []
                
                for char in page.chars:
                    if self.is_ascii_char(char['text']):
                        char_x1 = char['x1']
                        if char_x1 > text_right_edge + 0.01:  # 極小閾値
                            overflow_amount = char_x1 - text_right_edge
                            potential_overflows.append({
                                'char': char['text'],
                                'x1': char_x1,
                                'y0': char['y0'],
                                'overflow': overflow_amount
                            })
                
                if not potential_overflows:
                    logger.info(f"\n❌ はみ出し候補が見つかりません")
                    return
                
                logger.info(f"\n📊 はみ出し候補: {len(potential_overflows)}個")
                
                # 行ごとにグループ化
                line_groups = {}
                for char_info in potential_overflows:
                    y_pos = round(char_info['y0'])
                    if y_pos not in line_groups:
                        line_groups[y_pos] = []
                    line_groups[y_pos].append(char_info)
                
                # 各行をフィルタデバッグ
                for y_pos, chars_in_line in line_groups.items():
                    chars_in_line.sort(key=lambda x: x['x1'])
                    overflow_text = ''.join([c['char'] for c in chars_in_line])
                    max_overflow = max(c['overflow'] for c in chars_in_line)
                    
                    logger.info(f"\n🔍 行 y={y_pos}:")
                    logger.info(f"  はみ出しテキスト: '{overflow_text}'")
                    logger.info(f"  はみ出し量: {max_overflow:.3f}pt")
                    logger.info(f"  文字数: {len(chars_in_line)}")
                    
                    # フィルタの詳細デバッグ
                    debug_result = self.debug_filter_step_by_step(overflow_text, max_overflow, y_pos)
                    
                    logger.info(f"  フィルタテスト結果:")
                    for filter_name, filter_result in debug_result['filter_results'].items():
                        status = "🔴BLOCK" if filter_result['triggered'] else "🟢PASS"
                        logger.info(f"    {filter_name}: {status}")
                        
                        # 詳細情報の表示
                        if filter_name == '小さいはみ出し(<=0.5pt)' and filter_result['triggered']:
                            logger.info(f"      → {filter_result['value']:.3f}pt <= {filter_result['threshold']}pt")
                        elif filter_name == '短いテキスト+記号のみ' and 'char_analysis' in filter_result:
                            logger.info(f"      → 文字解析: {filter_result['char_analysis']}")
                        elif filter_name == '日本語のみ' and 'char_analysis' in filter_result:
                            logger.info(f"      → 文字解析: {filter_result['char_analysis']}")
                    
                    final_decision = debug_result['final_decision']
                    if final_decision['is_filtered_out']:
                        logger.info(f"  🚫 最終判定: フィルタで除外")
                        logger.info(f"     発動フィルタ: {final_decision['triggered_filters']}")
                    else:
                        logger.info(f"  ✅ 最終判定: 検出対象")
                        
        except Exception as e:
            logger.info(f"❌ エラー: {str(e)}")
        
        logger.info(f"=" * 90)

def main():
    """メイン実行関数"""
    debugger = FilterDebugger()
    
    # sample4.pdf Page 38を詳細デバッグ
    pdf_path = Path("sample4.pdf")
    if pdf_path.exists():
        debugger.debug_specific_page(pdf_path, 38)
    else:
        logger.info("sample4.pdf が見つかりません")

if __name__ == "__main__":
    main()