#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test all PDFs with final detector
"""

import subprocess
import json
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
            ['python', 'overflow_detector_final.py', pdf_file],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Parse output to extract page numbers
        detected_pages = []
        for line in result.stdout.split('\n'):
            if line.startswith('Page ') and 'はみ出し検出' in line:
                page_num = int(line.split()[1].rstrip(':'))
                detected_pages.append(page_num)
        
        return sorted(set(detected_pages))
    except Exception as e:
        print(f"Error testing {pdf_file}: {e}")
        return []

def main():
    print("Testing Final Overflow Detector")
    print("=" * 60)
    
    all_correct = True
    
    for pdf_file, expected_pages in ground_truth.items():
        if Path(pdf_file).exists():
            detected_pages = test_pdf(pdf_file)
            
            # Compare with ground truth
            false_positives = [p for p in detected_pages if p not in expected_pages]
            false_negatives = [p for p in expected_pages if p not in detected_pages]
            
            status = "✅" if not false_positives and not false_negatives else "❌"
            
            print(f"\n{pdf_file}: {status}")
            print(f"  Expected: {expected_pages}")
            print(f"  Detected: {detected_pages}")
            
            if false_positives:
                print(f"  False positives: {false_positives}")
                all_correct = False
            if false_negatives:
                print(f"  False negatives: {false_negatives}")
                all_correct = False
    
    print("\n" + "=" * 60)
    print(f"Overall result: {'✅ All tests passed!' if all_correct else '❌ Some tests failed'}")

if __name__ == "__main__":
    main()