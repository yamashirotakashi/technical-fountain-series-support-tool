#!/usr/bin/env python3
"""
視覚的検証ツール - OCR検出結果を画像上に可視化
はみ出し検出の精度検証とfalse positive分析用
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
import pytesseract

from overflow_detector_ocr import OCRBasedOverflowDetector


class VisualOverflowValidator:
    """視覚的はみ出し検証ツール"""
    
    def __init__(self):
        self.detector = OCRBasedOverflowDetector()
        
    def visualize_detection_results(self, pdf_path: Path, page_number: int, 
                                  output_dir: Path = None) -> Tuple[Dict, str]:
        """
        指定ページの検出結果を可視化
        
        Args:
            pdf_path: PDFファイルパス
            page_number: ページ番号（1開始）
            output_dir: 出力ディレクトリ
            
        Returns:
            (detection_results, output_image_path)
        """
        if output_dir is None:
            output_dir = Path("visual_validation")
        output_dir.mkdir(exist_ok=True)
        
        # PDFからページ画像を取得
        doc = fitz.open(pdf_path)
        page = doc[page_number - 1]  # 0開始に変換
        
        # 画像として出力
        mat = fitz.Matrix(self.detector.DPI / 72, self.detector.DPI / 72)
        pix = page.get_pixmap(matrix=mat)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 右ページかどうかの判定
        is_right_page = page_number % 2 == 1
        
        # マージン情報を取得
        img_width, img_height = image.size
        mm_to_px = self.detector.DPI / 25.4
        
        if is_right_page:
            left_margin_px = int(self.detector.RIGHT_PAGE_LEFT_MARGIN_MM * mm_to_px)
            right_margin_px = int(self.detector.RIGHT_PAGE_RIGHT_MARGIN_MM * mm_to_px)
        else:
            left_margin_px = int(self.detector.LEFT_PAGE_LEFT_MARGIN_MM * mm_to_px)
            right_margin_px = int(self.detector.LEFT_PAGE_RIGHT_MARGIN_MM * mm_to_px)
        
        text_right_edge = img_width - right_margin_px
        
        # OCRでテキスト情報を取得
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, 
                                        lang='jpn+eng')
        
        # 描画用のコピーを作成
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        
        # デフォルトフォントを使用
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        detection_results = {
            'page_number': page_number,
            'is_right_page': is_right_page,
            'margins': {
                'left': left_margin_px,
                'right': right_margin_px,
                'text_right_edge': text_right_edge
            },
            'detections': [],
            'all_text_boxes': []
        }
        
        # マージン線を描画（薄い青）
        draw.line([(left_margin_px, 0), (left_margin_px, img_height)], 
                 fill=(100, 150, 255), width=2)
        draw.line([(text_right_edge, 0), (text_right_edge, img_height)], 
                 fill=(100, 150, 255), width=2)
        
        # 許容範囲の線を描画（薄い緑）
        overflow_threshold = text_right_edge + self.detector.MARGIN_TOLERANCE_PX
        draw.line([(overflow_threshold, 0), (overflow_threshold, img_height)], 
                 fill=(100, 255, 100), width=1)
        
        # 各テキスト要素を処理
        n_boxes = len(data['text'])
        overflow_count = 0
        
        for i in range(n_boxes):
            if data['text'][i].strip():
                text_left = data['left'][i]
                text_top = data['top'][i]
                text_width = data['width'][i]
                text_height = data['height'][i]
                text_right = text_left + text_width
                confidence = int(data['conf'][i])
                text_content = data['text'][i]
                
                # テキストボックス情報を記録
                box_info = {
                    'text': text_content,
                    'left': text_left,
                    'top': text_top,
                    'right': text_right,
                    'confidence': confidence,
                    'is_overflow': False
                }
                
                # テキストボックスを描画（薄いグレー）
                draw.rectangle([text_left, text_top, text_right, text_top + text_height], 
                              outline=(200, 200, 200), width=1)
                
                # 本文エリア内かつ信頼度が高いテキストをチェック
                if (text_left >= left_margin_px - self.detector.LEFT_MARGIN_TOLERANCE_PX and 
                    confidence >= self.detector.MIN_CONFIDENCE):
                    
                    if text_right > overflow_threshold:
                        overflow_amount = text_right - text_right_edge
                        
                        if overflow_amount >= self.detector.MIN_OVERFLOW_PX:
                            # はみ出し検出（赤色で強調）
                            draw.rectangle([text_left, text_top, text_right, text_top + text_height], 
                                         outline=(255, 0, 0), width=3)
                            
                            # はみ出し量をテキストで表示
                            label = f"+{overflow_amount:.0f}px"
                            draw.text((text_right + 5, text_top), label, 
                                    fill=(255, 0, 0), font=font)
                            
                            box_info['is_overflow'] = True
                            box_info['overflow_amount'] = overflow_amount
                            
                            detection_results['detections'].append({
                                'text': text_content[:30] + ('...' if len(text_content) > 30 else ''),
                                'position': (text_left, text_top, text_right, text_top + text_height),
                                'overflow_amount': overflow_amount,
                                'confidence': confidence
                            })
                            overflow_count += 1
                
                detection_results['all_text_boxes'].append(box_info)
        
        # 結果サマリーを画像上部に描画
        summary_text = f"ページ{page_number} ({'右' if is_right_page else '左'}ページ) - はみ出し検出: {overflow_count}件"
        draw.text((10, 10), summary_text, fill=(0, 0, 0), font=font)
        
        # マージン情報を表示
        margin_text = f"左マージン: {left_margin_px}px, 本文右端: {text_right_edge}px, 許容: {overflow_threshold}px"
        draw.text((10, 30), margin_text, fill=(0, 0, 0), font=font)
        
        # 画像を保存
        output_filename = f"{pdf_path.stem}_page{page_number:03d}_validation.png"
        output_path = output_dir / output_filename
        draw_image.save(output_path, "PNG")
        
        doc.close()
        
        return detection_results, str(output_path)
    
    def batch_validate_pages(self, pdf_path: Path, page_numbers: List[int] = None,
                           output_dir: Path = None) -> Dict:
        """
        複数ページの一括検証
        
        Args:
            pdf_path: PDFファイルパス
            page_numbers: 検証対象ページ番号リスト（Noneなら全ページ）
            output_dir: 出力ディレクトリ
            
        Returns:
            検証結果辞書
        """
        if output_dir is None:
            output_dir = Path("visual_validation")
        output_dir.mkdir(exist_ok=True)
        
        # ページ数を取得
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        
        if page_numbers is None:
            page_numbers = list(range(1, min(6, total_pages + 1)))  # 最初の5ページ
        
        batch_results = {
            'pdf_file': str(pdf_path),
            'total_pages': total_pages,
            'validated_pages': [],
            'summary': {
                'total_detections': 0,
                'pages_with_overflow': 0
            }
        }
        
        print(f"📊 視覚的検証開始: {pdf_path.name}")
        print(f"対象ページ: {page_numbers}")
        print("=" * 60)
        
        for page_num in page_numbers:
            if page_num > total_pages:
                continue
                
            print(f"\n🔍 ページ {page_num} を検証中...")
            
            try:
                results, image_path = self.visualize_detection_results(
                    pdf_path, page_num, output_dir
                )
                
                batch_results['validated_pages'].append({
                    'page_number': page_num,
                    'results': results,
                    'output_image': image_path
                })
                
                detections = len(results['detections'])
                batch_results['summary']['total_detections'] += detections
                
                if detections > 0:
                    batch_results['summary']['pages_with_overflow'] += 1
                
                print(f"  ✅ 完了 - はみ出し検出: {detections}件")
                
                if detections > 0:
                    print("  📋 検出詳細:")
                    for det in results['detections'][:3]:  # 最初の3件のみ表示
                        print(f"    - '{det['text']}' (+{det['overflow_amount']:.0f}px)")
                    if len(results['detections']) > 3:
                        print(f"    - ...他{len(results['detections']) - 3}件")
                
                print(f"  🖼️ 画像保存: {Path(image_path).name}")
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")
                batch_results['validated_pages'].append({
                    'page_number': page_num,
                    'error': str(e)
                })
        
        # サマリーレポートを生成
        self._generate_summary_report(batch_results, output_dir)
        
        print("\n" + "=" * 60)
        print("📊 検証完了サマリー")
        print(f"総検出数: {batch_results['summary']['total_detections']}件")
        print(f"はみ出しページ数: {batch_results['summary']['pages_with_overflow']}ページ")
        print(f"出力ディレクトリ: {output_dir}")
        
        return batch_results
    
    def _generate_summary_report(self, results: Dict, output_dir: Path):
        """サマリーレポートHTMLを生成"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>はみ出し検出 視覚的検証レポート</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .page-result {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .overflow {{ background-color: #ffe6e6; }}
        .clean {{ background-color: #e6ffe6; }}
        .detection {{ margin: 5px 0; padding: 5px; background-color: #fff; border-left: 3px solid #ff0000; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #ccc; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 はみ出し検出 視覚的検証レポート</h1>
        <p><strong>PDF:</strong> {results['pdf_file']}</p>
        <p><strong>総検出数:</strong> {results['summary']['total_detections']}件</p>
        <p><strong>はみ出しページ数:</strong> {results['summary']['pages_with_overflow']}ページ</p>
    </div>
"""
        
        for page_result in results['validated_pages']:
            if 'error' in page_result:
                html_content += f"""
    <div class="page-result">
        <h3>ページ {page_result['page_number']} - エラー</h3>
        <p>{page_result['error']}</p>
    </div>
"""
                continue
            
            page_data = page_result['results']
            detections = len(page_data['detections'])
            css_class = "overflow" if detections > 0 else "clean"
            
            html_content += f"""
    <div class="page-result {css_class}">
        <h3>ページ {page_data['page_number']} ({'右' if page_data['is_right_page'] else '左'}ページ) - {detections}件検出</h3>
"""
            
            if detections > 0:
                html_content += "<div><strong>検出詳細:</strong></div>"
                for det in page_data['detections']:
                    html_content += f"""
        <div class="detection">
            <strong>テキスト:</strong> {det['text']}<br>
            <strong>はみ出し量:</strong> +{det['overflow_amount']:.1f}px<br>
            <strong>信頼度:</strong> {det['confidence']}%
        </div>
"""
            
            if 'output_image' in page_result:
                image_name = Path(page_result['output_image']).name
                html_content += f"""
        <div>
            <h4>視覚的検証結果:</h4>
            <img src="{image_name}" alt="Page {page_data['page_number']} validation">
        </div>
"""
            
            html_content += "    </div>\n"
        
        html_content += """
</body>
</html>
"""
        
        report_path = output_dir / "validation_report.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 HTMLレポート: {report_path}")


def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="OCRはみ出し検出の視覚的検証ツール"
    )
    parser.add_argument('pdf_file', help='検証対象のPDFファイル')
    parser.add_argument('-p', '--pages', type=str, 
                       help='検証対象ページ (例: 1,3,5 または 1-5)')
    parser.add_argument('-o', '--output-dir', type=str, default='visual_validation',
                       help='出力ディレクトリ (デフォルト: visual_validation)')
    parser.add_argument('--min-confidence', type=int, default=30,
                       help='OCR信頼度閾値')
    parser.add_argument('--margin-tolerance', type=int, default=20,
                       help='マージン許容範囲（px）')
    parser.add_argument('--min-overflow', type=int, default=15,
                       help='最小はみ出し検出量（px）')
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf_file)
    output_dir = Path(args.output_dir)
    
    if not pdf_path.exists():
        print(f"エラー: PDFファイルが見つかりません: {pdf_path}")
        sys.exit(1)
    
    # 検証ツールを初期化
    validator = VisualOverflowValidator()
    
    # パラメータを設定
    validator.detector.MIN_CONFIDENCE = args.min_confidence
    validator.detector.MARGIN_TOLERANCE_PX = args.margin_tolerance  
    validator.detector.MIN_OVERFLOW_PX = args.min_overflow
    
    # ページ番号を解析
    page_numbers = None
    if args.pages:
        try:
            if '-' in args.pages:
                start, end = map(int, args.pages.split('-'))
                page_numbers = list(range(start, end + 1))
            else:
                page_numbers = [int(p.strip()) for p in args.pages.split(',')]
        except ValueError:
            print(f"エラー: ページ指定が不正です: {args.pages}")
            sys.exit(1)
    
    # 一括検証を実行
    results = validator.batch_validate_pages(pdf_path, page_numbers, output_dir)
    
    sys.exit(0)


if __name__ == "__main__":
    main()