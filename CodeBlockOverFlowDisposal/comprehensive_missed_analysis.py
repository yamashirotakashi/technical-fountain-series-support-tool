#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Missed Pages Analysis - 全見逃しページの詳細分析
direct_test.pyの結果に基づく、false negativeの完全分析
"""

import pdfplumber
from pathlib import Path
from pure_algorithmic_detector import PureAlgorithmicDetector

# direct_test.pyの結果による見逃しページ（False Negatives）
missed_pages = {
    'sample.pdf': [48],
    'sample2.pdf': [128, 129], 
    'sample3.pdf': [80, 106],
    'sample4.pdf': [75],
    'sample5.pdf': [128, 129]  # sample2と同じ
}

def analyze_page_comprehensive(pdf_path: str, page_num: int):
    """特定ページの包括的分析"""
    print(f"\n{'='*80}")
    print(f"🔍 {pdf_path} Page {page_num} 包括的分析")
    print(f"{'='*80}")
    
    detector = PureAlgorithmicDetector()
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_num > len(pdf.pages):
                print(f"❌ Page {page_num} は存在しません (総ページ数: {len(pdf.pages)})")
                return
            
            page = pdf.pages[page_num - 1]
            
            # 1. 基本情報
            print(f"\n📏 基本情報:")
            print(f"  ページサイズ: {page.width:.1f} x {page.height:.1f}pt")
            print(f"  ページタイプ: {'奇数' if page_num % 2 == 1 else '偶数'}ページ")
            
            # 2. マージン計算
            if page_num % 2 == 1:  # 奇数ページ
                right_margin_pt = 10 * detector.mm_to_pt  # 28.3pt
            else:  # 偶数ページ
                right_margin_pt = 18 * detector.mm_to_pt  # 51.0pt
            
            text_right_edge = page.width - right_margin_pt
            
            print(f"  右マージン: {right_margin_pt:.1f}pt")
            print(f"  テキスト右端境界: {text_right_edge:.1f}pt")
            
            # 3. 文字統計
            total_chars = len(page.chars)
            ascii_chars = []
            non_ascii_chars = []
            
            for char in page.chars:
                if detector.is_ascii_char(char['text']):
                    ascii_chars.append(char)
                else:
                    non_ascii_chars.append(char)
            
            print(f"\n📊 文字統計:")
            print(f"  総文字数: {total_chars}")
            print(f"  ASCII文字数: {len(ascii_chars)} ({100*len(ascii_chars)/total_chars:.1f}%)")
            print(f"  非ASCII文字数: {len(non_ascii_chars)} ({100*len(non_ascii_chars)/total_chars:.1f}%)")
            
            # 4. 右端付近のASCII文字分析
            print(f"\n🎯 右端付近ASCII文字分析:")
            
            boundary_chars = []
            overflow_chars = []
            
            for char in ascii_chars:
                char_x1 = char['x1']
                distance_from_edge = char_x1 - text_right_edge
                
                # 境界から±10pt以内の文字を記録
                if abs(distance_from_edge) <= 10:
                    char_info = {
                        'char': char['text'],
                        'x0': char['x0'],
                        'x1': char_x1,
                        'y0': char['y0'],
                        'distance': distance_from_edge,
                        'is_overflow': distance_from_edge > 0.1
                    }
                    boundary_chars.append(char_info)
                    
                    if distance_from_edge > 0.1:
                        overflow_chars.append(char_info)
            
            print(f"  境界±10pt内のASCII文字: {len(boundary_chars)}文字")
            print(f"  0.1pt超過文字: {len(overflow_chars)}文字")
            
            # 5. 検出器の実行
            print(f"\n🤖 検出器実行結果:")
            detected_overflows = detector.detect_overflows(page, page_num)
            print(f"  検出されたはみ出し行数: {len(detected_overflows)}")
            
            if detected_overflows:
                print(f"  ✅ 検出内容:")
                for i, overflow in enumerate(detected_overflows):
                    print(f"    {i+1}. Y位置: {overflow['y_position']:.1f}")
                    print(f"       テキスト: '{overflow['overflow_text']}'")
                    print(f"       はみ出し量: {overflow['overflow_amount']:.1f}pt")
                    print(f"       文字数: {overflow['char_count']}")
            else:
                print(f"  ❌ はみ出し検出なし")
            
            # 6. 詳細分析
            if boundary_chars:
                print(f"\n📋 境界付近文字詳細 (距離順):")
                boundary_chars.sort(key=lambda x: x['distance'], reverse=True)
                
                for i, char_info in enumerate(boundary_chars[:15]):  # 上位15文字
                    status = "🔴超過" if char_info['is_overflow'] else "✅境界内"
                    print(f"  {i+1:2d}. '{char_info['char']}' "
                          f"x1={char_info['x1']:6.1f}pt "
                          f"Y={char_info['y0']:6.1f}pt "
                          f"距離={char_info['distance']:+6.2f}pt {status}")
            
            # 7. 行ごとの分析
            if overflow_chars:
                print(f"\n📝 はみ出し文字の行分析:")
                
                # Y座標でグルーピング
                y_groups = {}
                for char_info in overflow_chars:
                    y_pos = round(char_info['y0'])
                    if y_pos not in y_groups:
                        y_groups[y_pos] = []
                    y_groups[y_pos].append(char_info)
                
                for y_pos, chars_in_line in y_groups.items():
                    chars_in_line.sort(key=lambda x: x['x1'])
                    line_text = ''.join([c['char'] for c in chars_in_line])
                    max_overflow = max(c['distance'] for c in chars_in_line)
                    
                    print(f"  Y={y_pos}: '{line_text}' ({len(chars_in_line)}文字, 最大{max_overflow:.1f}pt)")
            
            # 8. 原因分析
            print(f"\n🔍 検出失敗の原因分析:")
            
            if not overflow_chars:
                print(f"  ❌ 実際にははみ出し文字が存在しない")
                print(f"     → Ground Truth誤りの可能性")
                
                if boundary_chars:
                    closest_char = max(boundary_chars, key=lambda x: x['distance'])
                    print(f"     → 最も右端に近い文字: '{closest_char['char']}' ({closest_char['distance']:+.2f}pt)")
                    
                    if closest_char['distance'] <= 0:
                        print(f"     → 閾値0.1ptを下回っているため正常動作")
                    else:
                        print(f"     → 0.1pt未満のため検出されない")
            else:
                print(f"  ✅ はみ出し文字は存在する")
                total_overflow_chars = len(overflow_chars)
                
                if len(detected_overflows) == 0:
                    print(f"     → 検出ロジックに問題がある可能性")
                    print(f"     → {total_overflow_chars}文字のはみ出しが見逃されている")
                    
                    # 行グルーピングが正しく動作していない可能性
                    print(f"     → 行グルーピング問題の可能性を調査中...")
                    
                    # 実際の検出プロセスをトレース
                    print(f"\n🔬 検出プロセストレース:")
                    line_overflows = {}
                    
                    for char_info in overflow_chars:
                        y_pos = round(char_info['y0'])
                        if y_pos not in line_overflows:
                            line_overflows[y_pos] = []
                        line_overflows[y_pos].append(char_info)
                    
                    print(f"     → Y座標グルーピング結果: {len(line_overflows)}行")
                    for y_pos, chars in line_overflows.items():
                        chars_text = ''.join([c['char'] for c in chars])
                        print(f"       Y={y_pos}: '{chars_text}' ({len(chars)}文字)")
                    
                    # 検出器内部の処理と比較
                    print(f"     → 検出器が認識した行数: {len(detected_overflows)}")
                    print(f"     → 不一致の理由: Y座標の丸め処理またはフィルタリング問題")
            
    except Exception as e:
        print(f"❌ エラー: {e}")

def main():
    print("包括的見逃しページ分析 - 100%検出達成のための調査")
    print("=" * 100)
    
    total_missed = 0
    
    for pdf_file, pages in missed_pages.items():
        if not Path(pdf_file).exists():
            print(f"\n❌ {pdf_file} が見つかりません")
            continue
        
        print(f"\n📄 {pdf_file} の分析:")
        total_missed += len(pages)
        
        for page_num in pages:
            analyze_page_comprehensive(pdf_file, page_num)
    
    print(f"\n{'='*100}")
    print(f"📊 分析完了サマリー:")
    print(f"  総見逃しページ数: {total_missed}ページ")
    print(f"  対象PDFファイル数: {len(missed_pages)}ファイル")
    print("=" * 100)

if __name__ == "__main__":
    main()