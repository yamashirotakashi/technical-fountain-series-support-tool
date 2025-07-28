#!/usr/bin/env python3
"""
バッチ処理サマリーツール - 複数PDFのはみ出し検出結果を一覧表示
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict
import glob

from overflow_detector_ocr import OCRBasedOverflowDetector


def analyze_pdf_batch(pdf_patterns: List[str], 
                     min_confidence: int = 30,
                     margin_tolerance: int = 20, 
                     min_overflow: int = 1) -> Dict:
    """
    複数PDFのはみ出し検出を一括実行
    
    Args:
        pdf_patterns: PDFファイルパターンのリスト
        min_confidence: OCR信頼度閾値
        margin_tolerance: マージン許容範囲
        min_overflow: 最小はみ出し検出量
        
    Returns:
        結果辞書
    """
    # 検出器の初期化
    detector = OCRBasedOverflowDetector()
    detector.MIN_CONFIDENCE = min_confidence
    detector.MARGIN_TOLERANCE_PX = margin_tolerance
    detector.MIN_OVERFLOW_PX = min_overflow
    
    # PDFファイルを収集
    pdf_files = []
    for pattern in pdf_patterns:
        matches = glob.glob(pattern)
        pdf_files.extend([Path(f) for f in matches if f.lower().endswith('.pdf')])
    
    if not pdf_files:
        print("❌ PDFファイルが見つかりません")
        return {}
    
    # 重複除去とソート
    pdf_files = sorted(list(set(pdf_files)))
    
    print(f"📊 バッチ処理開始: {len(pdf_files)}個のPDFファイル")
    print(f"設定 - 信頼度: {min_confidence}, 許容: {margin_tolerance}px, 最小: {min_overflow}px")
    print("=" * 80)
    
    results = {
        'settings': {
            'min_confidence': min_confidence,
            'margin_tolerance': margin_tolerance,
            'min_overflow': min_overflow
        },
        'files': [],
        'summary': {
            'total_files': len(pdf_files),
            'files_with_overflow': 0,
            'total_overflow_pages': 0,
            'total_pages_processed': 0
        }
    }
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n🔍 [{i}/{len(pdf_files)}] {pdf_path.name}")
        
        try:
            # はみ出し検出実行
            overflow_pages = detector.detect_file(pdf_path)
            
            # 総ページ数を取得
            import fitz
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()
            
            file_result = {
                'file_name': pdf_path.name,
                'file_path': str(pdf_path),
                'total_pages': total_pages,
                'overflow_pages': overflow_pages,
                'overflow_count': len(overflow_pages),
                'success': True
            }
            
            results['files'].append(file_result)
            results['summary']['total_pages_processed'] += total_pages
            
            if overflow_pages:
                results['summary']['files_with_overflow'] += 1
                results['summary']['total_overflow_pages'] += len(overflow_pages)
                
                print(f"  ⚠️  はみ出し検出: {len(overflow_pages)}ページ (全{total_pages}ページ中)")
                if len(overflow_pages) <= 10:
                    print(f"     対象ページ: {', '.join(map(str, overflow_pages))}")
                else:
                    print(f"     対象ページ: {', '.join(map(str, overflow_pages[:10]))}... (他{len(overflow_pages)-10}ページ)")
            else:
                print(f"  ✅ はみ出しなし (全{total_pages}ページ)")
                
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            file_result = {
                'file_name': pdf_path.name,
                'file_path': str(pdf_path),
                'error': str(e),
                'success': False
            }
            results['files'].append(file_result)
    
    return results


def print_summary_report(results: Dict):
    """サマリーレポートを表示"""
    print("\n" + "=" * 80)
    print("📊 バッチ処理完了サマリー")
    print("=" * 80)
    
    summary = results['summary']
    settings = results['settings']
    
    print(f"処理設定:")
    print(f"  - OCR信頼度閾値: {settings['min_confidence']}")
    print(f"  - マージン許容: {settings['margin_tolerance']}px")
    print(f"  - 最小はみ出し: {settings['min_overflow']}px")
    
    print(f"\n全体統計:")
    print(f"  - 処理ファイル数: {summary['total_files']}個")
    print(f"  - 総ページ数: {summary['total_pages_processed']}ページ")
    print(f"  - はみ出し発生ファイル数: {summary['files_with_overflow']}個")
    print(f"  - はみ出し発生ページ数: {summary['total_overflow_pages']}ページ")
    
    if summary['total_files'] > 0:
        overflow_file_rate = summary['files_with_overflow'] / summary['total_files'] * 100
        print(f"  - ファイル単位はみ出し率: {overflow_file_rate:.1f}%")
        
        if summary['total_pages_processed'] > 0:
            overflow_page_rate = summary['total_overflow_pages'] / summary['total_pages_processed'] * 100
            print(f"  - ページ単位はみ出し率: {overflow_page_rate:.1f}%")
    
    print(f"\nファイル別詳細:")
    print(f"{'ファイル名':<30} {'総ページ':<8} {'はみ出し':<10} {'率':<8} {'ステータス'}")
    print("-" * 70)
    
    for file_result in results['files']:
        if not file_result['success']:
            print(f"{file_result['file_name']:<30} {'N/A':<8} {'ERROR':<10} {'N/A':<8} ❌")
            continue
            
        name = file_result['file_name'][:28] + ('...' if len(file_result['file_name']) > 28 else '')
        total = file_result['total_pages']
        overflow = file_result['overflow_count']
        rate = f"{overflow/total*100:.1f}%" if total > 0 else "N/A"
        status = "⚠️" if overflow > 0 else "✅"
        
        print(f"{name:<30} {total:<8} {overflow:<10} {rate:<8} {status}")


def save_csv_report(results: Dict, output_path: Path):
    """CSV形式でレポートを保存"""
    import csv
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # ヘッダー
        writer.writerow(['ファイル名', 'ファイルパス', '総ページ数', 'はみ出しページ数', 
                        'はみ出し率(%)', 'はみ出しページリスト', 'ステータス'])
        
        # データ行
        for file_result in results['files']:
            if not file_result['success']:
                writer.writerow([
                    file_result['file_name'],
                    file_result['file_path'], 
                    'N/A', 'N/A', 'N/A',
                    f"エラー: {file_result['error']}",
                    'ERROR'
                ])
                continue
            
            overflow_pages_str = ','.join(map(str, file_result['overflow_pages']))
            overflow_rate = file_result['overflow_count'] / file_result['total_pages'] * 100 if file_result['total_pages'] > 0 else 0
            
            writer.writerow([
                file_result['file_name'],
                file_result['file_path'],
                file_result['total_pages'],
                file_result['overflow_count'],
                f"{overflow_rate:.1f}",
                overflow_pages_str,
                'はみ出しあり' if file_result['overflow_count'] > 0 else 'はみ出しなし'
            ])
    
    print(f"📄 CSVレポート保存: {output_path}")


def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="複数PDFのはみ出し検出バッチ処理"
    )
    parser.add_argument('patterns', nargs='+', 
                       help='PDFファイルパターン (例: *.pdf sample*.pdf)')
    parser.add_argument('--min-confidence', type=int, default=30,
                       help='OCR信頼度閾値 (デフォルト: 30)')
    parser.add_argument('--margin-tolerance', type=int, default=20,
                       help='マージン許容範囲px (デフォルト: 20)')
    parser.add_argument('--min-overflow', type=int, default=1,
                       help='最小はみ出し検出量px (デフォルト: 1)')
    parser.add_argument('--csv-output', type=str,
                       help='CSV出力ファイル名')
    
    args = parser.parse_args()
    
    # バッチ処理実行
    results = analyze_pdf_batch(
        args.patterns,
        args.min_confidence,
        args.margin_tolerance,
        args.min_overflow
    )
    
    if not results:
        sys.exit(1)
    
    # サマリー表示
    print_summary_report(results)
    
    # CSV出力
    if args.csv_output:
        csv_path = Path(args.csv_output)
        save_csv_report(results, csv_path)
    
    # 終了コード: はみ出しがあれば1、なければ0
    exit_code = 1 if results['summary']['files_with_overflow'] > 0 else 0
    sys.exit(exit_code)


if __name__ == "__main__":
    main()