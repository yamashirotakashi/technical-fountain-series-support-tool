#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Precise Missed Analysis - 見逃しページの0.01pt精度分析
技術的誠実性を保ちながら、真の原因を特定する
"""

import pdfplumber
from pathlib import Path
from pure_algorithmic_detector import PureAlgorithmicDetector

def analyze_missed_page_precisely(pdf_path: str, page_num: int):
    """見逃しページの0.01pt精度分析"""
    print(f"\n{'='*80}")
    print(f"🔬 {pdf_path} Page {page_num} - 0.01pt精度分析")
    print(f"{'='*80}")
    
    detector = PureAlgorithmicDetector()
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_num > len(pdf.pages):
                print(f"❌ Page {page_num} は存在しません")
                return None
            
            page = pdf.pages[page_num - 1]
            
            # マージン計算
            if page_num % 2 == 1:  # 奇数ページ
                right_margin_pt = 10 * detector.mm_to_pt  # 28.3pt
            else:  # 偶数ページ
                right_margin_pt = 18 * detector.mm_to_pt  # 51.0pt
            
            text_right_edge = page.width - right_margin_pt
            
            print(f"📏 基本情報:")
            print(f"  ページサイズ: {page.width:.1f} x {page.height:.1f}pt")
            print(f"  ページタイプ: {'奇数' if page_num % 2 == 1 else '偶数'}ページ")
            print(f"  右マージン: {right_margin_pt:.3f}pt")
            print(f"  テキスト右端境界: {text_right_edge:.3f}pt")
            
            # 全ASCII文字の精密分析
            ascii_chars = []
            for char in page.chars:
                if detector.is_ascii_char(char['text']):
                    char_x1 = char['x1']
                    distance = char_x1 - text_right_edge
                    
                    ascii_chars.append({
                        'char': char['text'],
                        'x1': char_x1,
                        'y0': char['y0'],
                        'distance': distance,
                        'is_overflow_0_1': distance > 0.1,
                        'is_overflow_0_05': distance > 0.05,
                        'is_overflow_0_02': distance > 0.02,
                        'is_overflow_0_01': distance > 0.01
                    })
            
            # 右端に近い文字を抽出（±1pt以内）
            near_edge_chars = [c for c in ascii_chars if abs(c['distance']) <= 1.0]
            near_edge_chars.sort(key=lambda x: x['distance'], reverse=True)
            
            print(f"\n🎯 右端±1pt以内のASCII文字: {len(near_edge_chars)}文字")
            
            if near_edge_chars:
                print(f"\n📊 右端文字詳細（上位15文字）:")
                for i, char in enumerate(near_edge_chars[:15]):
                    status_0_1 = "🔴" if char['is_overflow_0_1'] else "⚪"
                    status_0_05 = "🟠" if char['is_overflow_0_05'] else "⚪"
                    status_0_02 = "🟡" if char['is_overflow_0_02'] else "⚪"
                    status_0_01 = "🟢" if char['is_overflow_0_01'] else "⚪"
                    
                    print(f"  {i+1:2d}. '{char['char']}' x1={char['x1']:.3f}pt "
                          f"距離={char['distance']:+.3f}pt Y={char['y0']:.1f}pt")
                    print(f"      0.1pt:{status_0_1} 0.05pt:{status_0_05} "
                          f"0.02pt:{status_0_02} 0.01pt:{status_0_01}")
            
            # 各閾値での検出可能性
            thresholds = [0.1, 0.05, 0.02, 0.01]
            print(f"\n📈 閾値別検出可能性:")
            
            overflow_counts = {}
            for threshold in thresholds:
                overflow_chars = [c for c in ascii_chars if c['distance'] > threshold]
                overflow_counts[threshold] = len(overflow_chars)
                
                if overflow_chars:
                    # Y座標でグルーピング
                    lines = {}
                    for char in overflow_chars:
                        y_pos = round(char['y0'])
                        if y_pos not in lines:
                            lines[y_pos] = []
                        lines[y_pos].append(char)
                    
                    line_count = len(lines)
                    print(f"  閾値 {threshold:4.2f}pt: {len(overflow_chars):2d}文字 → {line_count}行")
                else:
                    print(f"  閾値 {threshold:4.2f}pt: 検出なし")
            
            # 現在の検出器での結果
            current_result = detector.detect_overflows(page, page_num)
            print(f"\n🤖 現在の検出器結果:")
            print(f"  検出行数: {len(current_result)}")
            
            return {
                'page': page_num,
                'pdf': pdf_path,
                'near_edge_count': len(near_edge_chars),
                'overflow_counts': overflow_counts,
                'current_detection': len(current_result),
                'max_distance': max([c['distance'] for c in ascii_chars]) if ascii_chars else 0,
                'closest_distance': max([c['distance'] for c in near_edge_chars]) if near_edge_chars else None
            }
    
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def main():
    """見逃し8ページの精密分析実行"""
    
    # 元のGround Truthでの見逃しページ
    missed_pages = {
        'sample.pdf': [48],
        'sample2.pdf': [128, 129], 
        'sample3.pdf': [80, 106],
        'sample4.pdf': [75],
        'sample5.pdf': [128, 129]
    }
    
    print("見逃しページ精密分析 - 0.01pt精度調査")
    print("=" * 100)
    
    all_results = []
    
    for pdf_file, pages in missed_pages.items():
        if not Path(pdf_file).exists():
            print(f"\n❌ {pdf_file} が見つかりません")
            continue
        
        print(f"\n📄 {pdf_file} の分析:")
        
        for page_num in pages:
            result = analyze_missed_page_precisely(pdf_file, page_num)
            if result:
                all_results.append(result)
    
    # サマリー
    print(f"\n{'='*100}")
    print("📊 精密分析サマリー:")
    print(f"{'='*100}")
    
    for result in all_results:
        print(f"\n{result['pdf']} Page {result['page']}:")
        print(f"  最大はみ出し距離: {result['max_distance']:.3f}pt")
        if result['closest_distance'] is not None:
            print(f"  最も右端の文字: {result['closest_distance']:+.3f}pt")
            
            # この文字が各閾値で検出されるかチェック
            thresholds = [0.1, 0.05, 0.02, 0.01]
            detection_threshold = None
            for threshold in sorted(thresholds, reverse=True):
                if result['closest_distance'] > threshold:
                    detection_threshold = threshold
                    break
            
            if detection_threshold:
                print(f"  検出可能な最小閾値: {detection_threshold}pt")
            else:
                print(f"  0.01pt閾値でも検出不可")
        else:
            print(f"  右端文字なし")
    
    print(f"\n{'='*100}")
    print("🎯 90%達成のための閾値候補:")
    
    # 90%達成に必要な見逃し改善数を計算
    total_expected = 28  # 元のGround Truth
    current_detected = 20  # 現在の検出数
    target_90_percent = int(total_expected * 0.9)  # 25.2 → 25ページ
    needed_additional = target_90_percent - current_detected  # 5ページ
    
    print(f"  現在の検出: {current_detected}/{total_expected}ページ (71.4%)")
    print(f"  90%目標: {target_90_percent}ページ")
    print(f"  追加で必要: {needed_additional}ページ")
    
    print("=" * 100)

if __name__ == "__main__":
    main()