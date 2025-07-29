#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maximum OCR Results Summary - 結果を分析してGround Truthと比較
"""

def analyze_maximum_ocr_results():
    """Maximum OCR Detectorの結果を分析"""
    
    # Ground Truth (元のGround Truth)
    original_ground_truth = {
        'sample.pdf': [48],
        'sample2.pdf': [128, 129],
        'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124],
        'sample4.pdf': [27, 30, 38, 73, 75, 76],
        'sample5.pdf': [128, 129]
    }
    
    # Maximum OCR Detectorの結果（実際の出力から）
    maximum_ocr_results = {
        'sample.pdf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88],  # 全88ページが検出
        'sample2.pdf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130],  # 127/129ページが検出
        'sample3.pdf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129],  # 129/129ページが検出
        'sample4.pdf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93],  # 93/93ページが検出
        'sample5.pdf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130]  # 130/130ページが検出
    }
    
    print("Maximum OCR Detector - 結果分析")
    print("=" * 80)
    
    # 🚨 重大な問題を発見
    print("\n🚨 重大な問題発見:")
    print("=" * 60)
    print("Maximum OCR DetectorはほぼSUPER-WIDE検出を実行しています！")
    print("これは明らかに間違った実装です。")
    
    total_expected = sum(len(pages) for pages in original_ground_truth.values())
    total_detected = sum(len(pages) for pages in maximum_ocr_results.values())
    
    # 正検出の計算
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    
    print(f"\n📊 性能評価:")
    print("-" * 60)
    
    for pdf_file, expected in original_ground_truth.items():
        detected = maximum_ocr_results.get(pdf_file, [])
        
        tp = len([p for p in expected if p in detected])
        fp = len([p for p in detected if p not in expected])
        fn = len([p for p in expected if p not in detected])
        
        true_positives += tp
        false_positives += fp
        false_negatives += fn
        
        print(f"{pdf_file}:")
        print(f"  期待: {len(expected)}ページ")
        print(f"  検出: {len(detected)}ページ")
        print(f"  正検出: {tp}, 誤検出: {fp}, 見逃し: {fn}")
    
    recall = true_positives / total_expected if total_expected > 0 else 0
    precision = true_positives / total_detected if total_detected > 0 else 0
    
    print(f"\n🎯 総合性能:")
    print(f"  Recall: {recall:.1%} ({true_positives}/{total_expected})")
    print(f"  Precision: {precision:.1%} ({true_positives}/{total_detected})")
    print(f"  誤検知: {false_positives}ページ")
    print(f"  見逃し: {false_negatives}ページ")
    
    print(f"\n❌ 問題点:")
    print("  1. ほぼ全ページを「はみ出し」として検出")
    print("  2. 誤検知が異常に多い（{:,}ページ）".format(false_positives))
    print("  3. Precision（正解率）が異常に低い")
    print("  4. 明らかにアルゴリズムの根本的な誤り")
    
    print(f"\n🔧 必要な修正:")
    print("  1. 適応的マージン計算の修正")
    print("  2. 閾値設定の見直し")
    print("  3. ノイズフィルタリングの強化")
    print("  4. 目次ページ等の除外")
    print("  5. (cid:X)文字の除外処理")
    
    print(f"\n💡 次のアクション:")
    print("  1. Maximum OCR Detectorの緊急修正")
    print("  2. 既存のpure_algorithmic_detectorを基準とした改良")
    print("  3. フィルタリング機能の大幅強化")
    print("  4. 段階的な精度向上実装")
    
    print("=" * 80)

if __name__ == "__main__":
    analyze_maximum_ocr_results()