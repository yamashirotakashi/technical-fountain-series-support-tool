#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct Test - 検出器を直接実行してテスト
"""

from pure_algorithmic_detector import PureAlgorithmicDetector
from pathlib import Path

# Ground truth
ground_truth = {
    'sample.pdf': [48],
    'sample2.pdf': [128, 129],
    'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124],
    'sample4.pdf': [27, 30, 38, 73, 75, 76],
    'sample5.pdf': [128, 129]
}

def test_pdf_direct(pdf_file):
    """PDFを直接テスト"""
    detector = PureAlgorithmicDetector()
    pdf_path = Path(pdf_file)
    
    if not pdf_path.exists():
        return []
    
    # 検出実行
    results = detector.process_pdf(pdf_path)
    
    # ページ番号を抽出
    detected_pages = [result['page'] for result in results]
    return sorted(detected_pages)

def main():
    print("Direct Test - 検出器直接実行")
    print("=" * 60)
    
    all_results = {}
    
    for pdf_file, expected_pages in ground_truth.items():
        print(f"\n{pdf_file}:")
        
        detected_pages = test_pdf_direct(pdf_file)
        
        # 分析
        true_positives = [p for p in detected_pages if p in expected_pages]
        false_positives = [p for p in detected_pages if p not in expected_pages]
        false_negatives = [p for p in expected_pages if p not in detected_pages]
        
        print(f"  Expected: {expected_pages}")
        print(f"  Detected: {detected_pages}")
        
        if true_positives:
            print(f"  ✅ True Positives: {true_positives}")
        if false_positives:
            print(f"  ❌ False Positives: {false_positives}")
        if false_negatives:
            print(f"  ⚠️  False Negatives: {false_negatives}")
        
        accuracy = len(true_positives) / len(expected_pages) if expected_pages else 0
        precision = len(true_positives) / len(detected_pages) if detected_pages else 0
        
        print(f"  Recall: {accuracy:.1%}")
        print(f"  Precision: {precision:.1%}")
        
        all_results[pdf_file] = {
            'expected': expected_pages,
            'detected': detected_pages,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'recall': accuracy,
            'precision': precision
        }
    
    # 全体サマリー
    print(f"\n{'='*60}")
    print("全体サマリー:")
    
    total_expected = sum(len(r['expected']) for r in all_results.values())
    total_detected = sum(len(r['detected']) for r in all_results.values())
    total_tp = sum(len(r['true_positives']) for r in all_results.values())
    total_fp = sum(len(r['false_positives']) for r in all_results.values())
    total_fn = sum(len(r['false_negatives']) for r in all_results.values())
    
    overall_recall = total_tp / total_expected if total_expected > 0 else 0
    overall_precision = total_tp / total_detected if total_detected > 0 else 0
    
    print(f"  Total Expected: {total_expected}")
    print(f"  Total Detected: {total_detected}")
    print(f"  True Positives: {total_tp}")
    print(f"  False Positives: {total_fp}")
    print(f"  False Negatives: {total_fn}")
    print(f"  Overall Recall: {overall_recall:.1%}")
    print(f"  Overall Precision: {overall_precision:.1%}")
    
    # 改善が必要な項目
    print(f"\n{'='*60}")
    print("改善項目:")
    
    for pdf_file, result in all_results.items():
        if result['false_negatives']:
            print(f"\n{pdf_file} - 見逃し ({len(result['false_negatives'])}ページ):")
            print(f"  {result['false_negatives']}")
        
        if result['false_positives']:
            print(f"\n{pdf_file} - 誤検知 ({len(result['false_positives'])}ページ):")
            print(f"  {result['false_positives']}")
    
    return all_results

if __name__ == "__main__":
    main()