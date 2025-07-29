#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
False Positives Analysis - 誤検知ページの分析
誤検知を除去するためのフィルタリングロジック開発
"""

import pdfplumber
from pathlib import Path
from pure_algorithmic_detector import PureAlgorithmicDetector

# False Positives（誤検知ページ）
false_positives = {
    'sample2.pdf': [60],
    'sample3.pdf': [75, 79, 121, 125],
    'sample5.pdf': [60]  # sample2と同じ
}

def analyze_false_positive_page(pdf_path: str, page_num: int):
    """誤検知ページの詳細分析とフィルタリング検討"""
    print(f"\n{'='*80}")
    print(f"🔍 {pdf_path} Page {page_num} 誤検知分析")
    print(f"{'='*80}")
    
    detector = PureAlgorithmicDetector()
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_num > len(pdf.pages):
                print(f"❌ Page {page_num} は存在しません (総ページ数: {len(pdf.pages)})")
                return
            
            page = pdf.pages[page_num - 1]
            
            # 基本情報
            print(f"\n📏 基本情報:")
            print(f"  ページサイズ: {page.width:.1f} x {page.height:.1f}pt")
            print(f"  ページタイプ: {'奇数' if page_num % 2 == 1 else '偶数'}ページ")
            
            # マージン計算
            if page_num % 2 == 1:  # 奇数ページ
                right_margin_pt = 10 * detector.mm_to_pt  # 28.3pt
            else:  # 偶数ページ
                right_margin_pt = 18 * detector.mm_to_pt  # 51.0pt
            
            text_right_edge = page.width - right_margin_pt
            print(f"  右マージン: {right_margin_pt:.1f}pt")
            print(f"  テキスト右端境界: {text_right_edge:.1f}pt")
            
            # 実際の検出実行
            detected_overflows = detector.detect_overflows(page, page_num)
            print(f"\n🤖 検出器実行結果:")
            print(f"  検出されたはみ出し行数: {len(detected_overflows)}")
            
            if detected_overflows:
                print(f"  ✅ 検出内容:")
                for i, overflow in enumerate(detected_overflows):
                    print(f"    {i+1}. Y位置: {overflow['y_position']:.1f}")
                    print(f"       テキスト: '{overflow['overflow_text']}'")
                    print(f"       はみ出し量: {overflow['overflow_amount']:.1f}pt")
                    print(f"       文字数: {overflow['char_count']}")
                    
                    # フィルタリング判定
                    text_length = len(overflow['overflow_text'])
                    overflow_amount = overflow['overflow_amount']
                    
                    print(f"       📊 分析:")
                    print(f"         - テキスト長: {text_length}文字")
                    print(f"         - はみ出し量: {overflow_amount:.1f}pt")
                    
                    # フィルタリング条件の検討
                    should_filter = False
                    filter_reasons = []
                    
                    # 1. 短すぎるテキスト（3文字以下）
                    if text_length <= 3:
                        should_filter = True
                        filter_reasons.append(f"短すぎるテキスト({text_length}文字)")
                    
                    # 2. はみ出し量が小さすぎる（2pt以下）
                    if overflow_amount <= 2.0:
                        should_filter = True
                        filter_reasons.append(f"はみ出し量が小さい({overflow_amount:.1f}pt)")
                    
                    # 3. 特定の文字パターン（記号のみ、空白のみ等）
                    text_content = overflow['overflow_text'].strip()
                    if not text_content or text_content in ['>', ')', ']', '}', ';', ':']:
                        should_filter = True
                        filter_reasons.append(f"記号のみ・空白のみのテキスト")
                    
                    # 4. PowerShellの一般的なパターン
                    if text_content.endswith('.ps1'))') or '::SecurityProtocol' in text_content:
                        should_filter = True
                        filter_reasons.append(f"PowerShell固有パターン")
                    
                    # 結論
                    if should_filter:
                        print(f"         🚫 フィルタリング推奨: {', '.join(filter_reasons)}")
                    else:
                        print(f"         ✅ 有効な検出として保持")
                    
                    print()
            
            # コードブロック分析
            print(f"\n📦 コードブロック分析:")
            
            # グレー背景の矩形（コードブロック）を検出
            code_blocks = []
            for rect in page.rects:
                if rect.get('fill'):
                    width = rect['x1'] - rect['x0']
                    height = rect['y1'] - rect['y0']
                    if width > 200 and height > 15:  # 十分な大きさのコードブロック
                        code_blocks.append(rect)
            
            print(f"  コードブロック数: {len(code_blocks)}")
            
            if code_blocks:
                print(f"  コードブロック詳細:")
                for i, block in enumerate(code_blocks):
                    print(f"    {i+1}. X: {block['x0']:.1f}-{block['x1']:.1f}pt, Y: {block['y0']:.1f}-{block['y1']:.1f}pt")
                    print(f"       サイズ: {block['x1']-block['x0']:.1f} x {block['y1']-block['y0']:.1f}pt")
            
            # 検出されたはみ出しがコードブロック内かチェック
            if detected_overflows and code_blocks:
                print(f"\n🎯 コードブロック内はみ出し検証:")
                for i, overflow in enumerate(detected_overflows):
                    y_pos = overflow['y_position']
                    
                    # どのコードブロックに含まれるかチェック
                    containing_blocks = []
                    for j, block in enumerate(code_blocks):
                        if block['y0'] <= y_pos <= block['y1']:
                            containing_blocks.append(j + 1)
                    
                    if containing_blocks:
                        print(f"    検出{i+1}: コードブロック {containing_blocks} 内")
                    else:
                        print(f"    検出{i+1}: ❌ コードブロック外 (要フィルタリング)")
    
    except Exception as e:
        print(f"❌ エラー: {e}")

def main():
    print("誤検知ページ分析 - フィルタリングロジック開発")
    print("=" * 100)
    
    for pdf_file, pages in false_positives.items():
        if not Path(pdf_file).exists():
            print(f"\n❌ {pdf_file} が見つかりません")
            continue
        
        print(f"\n📄 {pdf_file} の誤検知分析:")
        for page_num in pages:
            analyze_false_positive_page(pdf_file, page_num)
    
    print(f"\n{'='*100}")
    print("🎯 フィルタリング推奨ルール:")
    print("  1. テキスト長 ≤ 3文字")
    print("  2. はみ出し量 ≤ 2.0pt")
    print("  3. 記号のみ・空白のみのテキスト")
    print("  4. PowerShell固有パターン (.ps1'))、::SecurityProtocol)")
    print("  5. コードブロック外のはみ出し")
    print("=" * 100)

if __name__ == "__main__":
    main()