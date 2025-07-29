#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete Analysis - 全PDFの完全分析と100%検出器の実装
"""

import subprocess
import json
from pathlib import Path

# Ground truth (元の定義)
original_ground_truth = {
    'sample.pdf': [48],
    'sample2.pdf': [128, 129],
    'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124],
    'sample4.pdf': [27, 30, 38, 73, 75, 76],
    'sample5.pdf': [128, 129]
}

def run_detector(pdf_file):
    """検出器を実行して結果を取得"""
    try:
        result = subprocess.run(
            ['python', 'pure_algorithmic_detector.py', pdf_file],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 出力から検出ページを抽出
        detected_pages = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            if 'はみ出し検出ページ:' in line:
                try:
                    pages_str = line.split('はみ出し検出ページ:')[1].strip()
                    pages_str = pages_str.strip('[]')
                    if pages_str:
                        detected_pages = [int(p.strip()) for p in pages_str.split(',')]
                except:
                    continue
                break
        
        # 個別ページからも抽出
        if not detected_pages:
            for line in lines:
                if line.startswith('Page ') and 'はみ出し検出' in line:
                    try:
                        page_num = int(line.split()[1].rstrip(':'))
                        detected_pages.append(page_num)
                    except:
                        continue
        
        return sorted(set(detected_pages))
    except Exception as e:
        print(f"Error with {pdf_file}: {e}")
        return []

def analyze_specific_pages(pdf_file, pages_to_check):
    """特定ページの詳細分析"""
    print(f"\n=== {pdf_file} 詳細分析 ===")
    
    for page_num in pages_to_check:
        print(f"\nPage {page_num} の分析:")
        try:
            result = subprocess.run(
                ['python', 'debug_margins.py'],
                input=f"{pdf_file}\n{page_num}\n",
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # マージン分析結果を解析
            lines = result.stdout.split('\n')
            for line in lines:
                if f"Page {page_num}" in line or "ASCII overflow:" in line or "Rightmost ASCII:" in line:
                    print(f"  {line}")
        except:
            print(f"  分析エラー")

def main():
    print("完全分析 - 100%検出を目指す")
    print("=" * 60)
    
    analysis_results = {}
    
    for pdf_file, expected_pages in original_ground_truth.items():
        if not Path(pdf_file).exists():
            print(f"{pdf_file} が見つかりません")
            continue
            
        print(f"\n{pdf_file}:")
        detected_pages = run_detector(pdf_file)
        
        # 分析
        true_positives = [p for p in detected_pages if p in expected_pages]
        false_positives = [p for p in detected_pages if p not in expected_pages]
        false_negatives = [p for p in expected_pages if p not in detected_pages]
        
        # 結果表示
        print(f"  Expected: {expected_pages}")
        print(f"  Detected: {detected_pages}")
        print(f"  True Positives: {true_positives} ({len(true_positives)})")
        print(f"  False Positives: {false_positives} ({len(false_positives)})")
        print(f"  False Negatives: {false_negatives} ({len(false_negatives)})")
        
        accuracy = len(true_positives) / len(expected_pages) if expected_pages else 0
        precision = len(true_positives) / len(detected_pages) if detected_pages else 0
        
        print(f"  Accuracy: {accuracy:.1%}")
        print(f"  Precision: {precision:.1%}")
        
        analysis_results[pdf_file] = {
            'expected': expected_pages,
            'detected': detected_pages,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'accuracy': accuracy,
            'precision': precision
        }
    
    # 全体サマリー
    print(f"\n{'='*60}")
    print("全体サマリー:")
    
    total_expected = sum(len(r['expected']) for r in analysis_results.values())
    total_detected = sum(len(r['detected']) for r in analysis_results.values())
    total_tp = sum(len(r['true_positives']) for r in analysis_results.values())
    total_fp = sum(len(r['false_positives']) for r in analysis_results.values())
    total_fn = sum(len(r['false_negatives']) for r in analysis_results.values())
    
    overall_accuracy = total_tp / total_expected
    overall_precision = total_tp / total_detected if total_detected > 0 else 0
    
    print(f"  Total Expected: {total_expected}")
    print(f"  Total Detected: {total_detected}")
    print(f"  True Positives: {total_tp}")
    print(f"  False Positives: {total_fp}")
    print(f"  False Negatives: {total_fn}")
    print(f"  Overall Accuracy: {overall_accuracy:.1%}")
    print(f"  Overall Precision: {overall_precision:.1%}")
    
    # 問題のあるページを特定
    print(f"\n{'='*60}")
    print("要改善ページ:")
    
    for pdf_file, result in analysis_results.items():
        if result['false_positives']:
            print(f"\n{pdf_file} - 誤検知:")
            for page in result['false_positives']:
                print(f"  Page {page}: 誤検知 - 除外ロジック要検討")
        
        if result['false_negatives']:  
            print(f"\n{pdf_file} - 見逃し:")
            for page in result['false_negatives']:
                print(f"  Page {page}: 見逃し - 検出強化要検討")
    
    # 結果をJSONで保存
    with open('complete_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    return analysis_results

if __name__ == "__main__":
    main()