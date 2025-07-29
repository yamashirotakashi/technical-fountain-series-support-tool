#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test pure algorithmic detector on all PDFs
"""

import subprocess
from pathlib import Path

# Ground truth
ground_truth = {
    'sample.pdf': [48],
    'sample2.pdf': [128, 129],
    'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124],
    'sample4.pdf': [27, 30, 38, 73, 75, 76],
    'sample5.pdf': [128, 129]
}

def test_pdf(pdf_file):
    """Test a single PDF and return detected pages"""
    try:
        result = subprocess.run(
            ['python', 'pure_algorithmic_detector.py', pdf_file],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Parse output to extract page numbers
        detected_pages = []
        for line in result.stdout.split('\n'):
            if line.startswith('Page ') and ('はみ出し検出' in line or 'overflow' in line):
                try:
                    # Extract page number from "Page 13: 1個のはみ出し検出"
                    page_num = int(line.split()[1].rstrip(':'))
                    detected_pages.append(page_num)
                except (ValueError, IndexError):
                    continue
        
        # Also check summary line "はみ出し検出ページ: [13, 35, ...]"
        if not detected_pages:
            for line in result.stdout.split('\n'):
                if 'はみ出し検出ページ:' in line:
                    try:
                        # Extract page list from summary
                        pages_str = line.split('はみ出し検出ページ:')[1].strip()
                        pages_str = pages_str.strip('[]')
                        if pages_str:
                            detected_pages = [int(p.strip()) for p in pages_str.split(',')]
                    except:
                        continue
        
        return sorted(set(detected_pages))
    except Exception as e:
        print(f"Error testing {pdf_file}: {e}")
        return []

def main():
    print("Testing Pure Algorithmic Detector")
    print("=" * 60)
    
    all_results = {}
    
    for pdf_file, expected_pages in ground_truth.items():
        if Path(pdf_file).exists():
            detected_pages = test_pdf(pdf_file)
            all_results[pdf_file] = detected_pages
            
            # Compare with ground truth
            false_positives = [p for p in detected_pages if p not in expected_pages]
            false_negatives = [p for p in expected_pages if p not in detected_pages]
            
            if not false_positives and not false_negatives:
                status = "✅ Perfect"
                accuracy = "100%"
            else:
                correct = len([p for p in detected_pages if p in expected_pages])
                total_expected = len(expected_pages)
                accuracy = f"{correct}/{total_expected} ({100*correct/total_expected if total_expected > 0 else 0:.1f}%)"
                status = f"⚠️  {accuracy}"
            
            print(f"\n{pdf_file}: {status}")
            print(f"  Expected: {expected_pages}")
            print(f"  Detected: {detected_pages}")
            
            if false_positives:
                print(f"  Extra detections: {false_positives}")
            if false_negatives:
                print(f"  Missed pages: {false_negatives}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    for pdf_file, detected in all_results.items():
        expected = ground_truth[pdf_file]
        correct = len([p for p in detected if p in expected])
        total = len(expected)
        accuracy = 100 * correct / total if total > 0 else 0
        print(f"  {pdf_file}: {correct}/{total} pages ({accuracy:.1f}%)")

if __name__ == "__main__":
    main()