#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
False Positives Analysis - 誤検知ページの分析
誤検知を除去するためのフィルタリングロジック開発
"""

import pdfplumber
from pathlib import Path
from pure_algorithmic_detector import PureAlgorithmicDetector

# False Positives（誤検知ページ）- direct_test.pyの結果から
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
                    text_content = overflow['overflow_text'].strip()
                    
                    print(f"       📊 分析:")
                    print(f"         - テキスト長: {text_length}文字")
                    print(f"         - はみ出し量: {overflow_amount:.1f}pt")
                    print(f"         - 内容: '{text_content}'")
                    
                    # フィルタリング条件の検討
                    should_filter = False
                    filter_reasons = []
                    
                    # 1. 短すぎるテキスト（5文字以下）
                    if text_length <= 5:
                        should_filter = True
                        filter_reasons.append(f"短すぎるテキスト({text_length}文字)")
                    
                    # 2. はみ出し量が小さすぎる（10pt以下）
                    if overflow_amount <= 10.0:
                        should_filter = True
                        filter_reasons.append(f"はみ出し量が小さい({overflow_amount:.1f}pt)")
                    
                    # 3. 特定の文字パターン（記号のみ、空白のみ等）
                    if not text_content or text_content in ['>', ')', ']', '}', ';', ':', '"']:
                        should_filter = True
                        filter_reasons.append(f"記号のみ・空白のみのテキスト")
                    
                    # 4. PowerShellの一般的なパターン
                    powershell_patterns = ['.ps1))', '::SecurityProtocol', 'tall.ps1']
                    if any(pattern in text_content for pattern in powershell_patterns):
                        should_filter = True
                        filter_reasons.append(f"PowerShell固有パターン")
                    
                    # 結論
                    if should_filter:
                        print(f"         🚫 フィルタリング推奨: {', '.join(filter_reasons)}")
                    else:
                        print(f"         ✅ 有効な検出として保持")
                    
                    print()
    
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
    print("  1. テキスト長 ≤ 5文字")
    print("  2. はみ出し量 ≤ 10.0pt")
    print("  3. 記号のみ・空白のみのテキスト")
    print("  4. PowerShell固有パターン (.ps1)), ::SecurityProtocol, tall.ps1)")
    print("=" * 100)

if __name__ == "__main__":
    main()