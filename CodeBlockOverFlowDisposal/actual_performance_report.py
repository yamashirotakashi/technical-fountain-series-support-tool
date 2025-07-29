#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Actual Performance Report - 修正版検出器の実際の性能レポート
"""

def generate_actual_performance_report():
    """修正版検出器の実際の性能レポートを生成（テスト結果ベース）"""
    
    # Ground Truth (元のGround Truth)
    original_ground_truth = {
        'sample.pdf': [48],
        'sample2.pdf': [128, 129],
        'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 78, 80, 106, 115, 122, 124],
        'sample4.pdf': [27, 30, 38, 73, 75, 76],
        'sample5.pdf': [128, 129]
    }
    
    # Fixed Maximum OCR Detector の実際の結果（テスト実行から取得）
    actual_fixed_detector_results = {
        'sample.pdf': [],  # 0ページ検出
        'sample2.pdf': [],  # 0ページ検出
        'sample3.pdf': [13, 35, 36, 39, 42, 44, 45, 47, 49, 62, 70, 75, 78, 79, 115, 121, 122, 124, 125],  # 19ページ検出
        'sample4.pdf': [27, 30, 73, 76],  # 4ページ検出
        'sample5.pdf': []   # 0ページ検出
    }
    
    print("Fixed Maximum OCR Detector - 実際の性能レポート")
    print("=" * 90)
    
    def calculate_metrics(results_dict, ground_truth_dict):
        """性能メトリクスを計算"""
        total_expected = sum(len(pages) for pages in ground_truth_dict.values())
        total_detected = sum(len(pages) for pages in results_dict.values())
        
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for pdf_file, expected in ground_truth_dict.items():
            detected = results_dict.get(pdf_file, [])
            
            tp = len([p for p in detected if p in expected])
            fp = len([p for p in detected if p not in expected])
            fn = len([p for p in expected if p not in detected])
            
            true_positives += tp
            false_positives += fp
            false_negatives += fn
        
        recall = true_positives / total_expected if total_expected > 0 else 0
        precision = true_positives / total_detected if total_detected > 0 else 1.0
        
        return {
            'total_expected': total_expected,
            'total_detected': total_detected,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'recall': recall,
            'precision': precision
        }
    
    # 新検出器の性能
    new_metrics = calculate_metrics(actual_fixed_detector_results, original_ground_truth)
    
    print(f"\n📊 修正版検出器の実際の性能:")
    print("-" * 70)
    print(f"総検出ページ数: {new_metrics['total_detected']}")
    print(f"期待ページ数: {new_metrics['total_expected']}")
    print(f"正検出: {new_metrics['true_positives']}")
    print(f"誤検出: {new_metrics['false_positives']}")
    print(f"見逃し: {new_metrics['false_negatives']}")
    print(f"Recall: {new_metrics['recall']:.1%}")
    print(f"Precision: {new_metrics['precision']:.1%}")
    
    print(f"\n🎯 目標達成状況:")
    print("-" * 50)
    print(f"Phase 1目標（78%）: {'✅ 達成' if new_metrics['recall'] >= 0.78 else '❌ 未達成'}")
    print(f"最終目標（85%）  : {'✅ 達成' if new_metrics['recall'] >= 0.85 else '❌ 未達成'}")
    print(f"現在のRecall    : {new_metrics['recall']:.1%}")
    
    if new_metrics['recall'] >= 0.85:
        print(f"🎉 最終目標達成！Phase 2は不要です。")
    elif new_metrics['recall'] >= 0.78:
        needed_additional = int(28 * (0.85 - new_metrics['recall']))
        print(f"⚠️  Phase 1目標達成、残り{needed_additional}ページでPhase 2不要")
    else:
        needed_additional = int(28 * (0.78 - new_metrics['recall']))
        print(f"❌ Phase 1目標未達成、{needed_additional}ページの追加改善が必要")
    
    print(f"\n📈 詳細分析:")
    print("-" * 50)
    
    # PDF別詳細
    for pdf_file, expected in original_ground_truth.items():
        detected = actual_fixed_detector_results.get(pdf_file, [])
        
        tp = len([p for p in detected if p in expected])
        fp = len([p for p in detected if p not in expected])
        fn = len([p for p in expected if p not in detected])
        
        recall_file = tp / len(expected) if expected else 1.0
        precision_file = tp / len(detected) if detected else 1.0
        
        print(f"{pdf_file}:")
        print(f"  期待: {len(expected)}ページ, 検出: {len(detected)}ページ")
        print(f"  正検出: {tp}, 誤検出: {fp}, 見逃し: {fn}")
        print(f"  Recall: {recall_file:.1%}, Precision: {precision_file:.1%}")
        
        if fn > 0:
            missed_pages = [p for p in expected if p not in detected]
            print(f"  見逃しページ: {missed_pages}")
        
        if fp > 0:
            false_pages = [p for p in detected if p not in expected]
            print(f"  誤検知ページ: {false_pages}")
    
    print(f"\n🔍 問題分析:")
    print("-" * 50)
    print(f"主要な問題:")
    print(f"1. sample.pdf, sample2.pdf, sample5.pdf で検出失敗")
    print(f"2. sample3.pdf で誤検知が4ページ（75, 79, 121, 125）")
    print(f"3. sample3.pdf で見逃しが2ページ（80, 106）")
    print(f"4. sample4.pdf で見逃しが2ページ（38, 75）")
    
    print(f"\n💡 改善提案:")
    print("-" * 50)
    print(f"1. sample.pdf(p48), sample2/5.pdf(p128,129)の特殊パターン調査")
    print(f"2. 誤検知4ページの原因分析と追加フィルタリング")
    print(f"3. 見逃し4ページの検出条件の緩和")
    print(f"4. 適応的閾値の調整")
    
    print(f"\n💡 結論:")
    print("=" * 90)
    print(f"✅ 誤検知問題（540→4ページ）は解決済み")
    print(f"✅ Precision大幅改善（4.9%→{new_metrics['precision']:.1%}）")
    print(f"❌ Recall は {new_metrics['recall']:.1%} で目標78%未達成")
    print(f"❌ Phase 1目標達成には追加改善が必要")
    print("=" * 90)

if __name__ == "__main__":
    generate_actual_performance_report()