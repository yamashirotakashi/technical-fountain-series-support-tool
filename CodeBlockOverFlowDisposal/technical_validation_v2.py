#!/usr/bin/env python3
"""
技術検証プロトタイプ v2
sample2.pdfの60ページにある白背景・罫線囲みのコードブロックを検証
"""

import pdfplumber
import fitz  # PyMuPDF
import sys
from pathlib import Path


def analyze_page_60_plumber(pdf_path):
    """pdfplumberでページ60を解析"""
    print("=== pdfplumberでページ60の解析 ===")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) >= 60:
                page = pdf.pages[59]  # 0-indexed
                
                # 矩形（罫線）を確認
                print(f"\n矩形情報:")
                if hasattr(page, 'rects'):
                    rects = page.rects or []
                    print(f"矩形数: {len(rects)}")
                    
                    # 白背景の矩形を探す
                    for i, rect in enumerate(rects[:5]):  # 最初の5個
                        print(f"  矩形{i}: {rect}")
                
                # 線を確認
                print(f"\n線情報:")
                if hasattr(page, 'lines'):
                    lines = page.lines or []
                    print(f"線の数: {len(lines)}")
                    
                    # 水平・垂直線を分類
                    h_lines = [l for l in lines if abs(l['y0'] - l['y1']) < 0.1]
                    v_lines = [l for l in lines if abs(l['x0'] - l['x1']) < 0.1]
                    print(f"  水平線: {len(h_lines)}")
                    print(f"  垂直線: {len(v_lines)}")
                
                # テキストを確認
                chars = page.chars
                print(f"\nテキスト情報:")
                print(f"文字数: {len(chars) if chars else 0}")
                
                # ページ全体のbbox
                bbox = page.bbox
                print(f"ページサイズ: {bbox}")
                
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()


def analyze_page_60_fitz(pdf_path):
    """PyMuPDFでページ60を解析"""
    print("\n=== PyMuPDFでページ60の解析 ===")
    
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count >= 60:
            page = doc[59]  # 0-indexed
            
            # 図形を取得
            drawings = page.get_drawings()
            print(f"\n図形情報:")
            print(f"図形数: {len(drawings)}")
            
            # 罫線（stroke）を探す
            strokes = [d for d in drawings if d['type'] == 's']
            print(f"線の数: {len(strokes)}")
            
            # 塗りつぶし図形を探す
            fills = [d for d in drawings if d['type'] == 'f']
            print(f"塗りつぶし図形数: {len(fills)}")
            
            # 罫線で囲まれた領域を推定
            if strokes:
                print("\n罫線の詳細（最初の10個）:")
                for i, stroke in enumerate(strokes[:10]):
                    print(f"  線{i}: {stroke['rect']}, 色: {stroke.get('stroke')}")
            
            # テキストブロックを取得
            text_dict = page.get_text("dict")
            print(f"\nテキストブロック数: {len(text_dict['blocks'])}")
            
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'doc' in locals():
            doc.close()


def find_bordered_regions(page_plumber):
    """罫線で囲まれた領域を検出する試み"""
    print("\n=== 罫線で囲まれた領域の検出 ===")
    
    lines = page_plumber.lines or []
    
    # 水平線と垂直線を分類
    h_lines = sorted([l for l in lines if abs(l['y0'] - l['y1']) < 0.1], 
                     key=lambda l: l['y0'])
    v_lines = sorted([l for l in lines if abs(l['x0'] - l['x1']) < 0.1], 
                     key=lambda l: l['x0'])
    
    print(f"水平線: {len(h_lines)}")
    print(f"垂直線: {len(v_lines)}")
    
    # 矩形を形成する可能性のある線の組み合わせを探す
    potential_boxes = []
    
    # 簡易的な矩形検出（隣接する水平線と垂直線のペア）
    for i in range(len(h_lines) - 1):
        for j in range(len(v_lines) - 1):
            # 4つの角が存在するか確認
            top = h_lines[i]
            bottom = h_lines[i + 1]
            left = v_lines[j]
            right = v_lines[j + 1]
            
            # 矩形を形成しているか確認
            if (abs(top['x0'] - left['x0']) < 5 and 
                abs(top['x1'] - right['x0']) < 5 and
                abs(bottom['x0'] - left['x0']) < 5 and
                abs(bottom['x1'] - right['x0']) < 5):
                
                box = {
                    'x0': left['x0'],
                    'y0': top['y0'],
                    'x1': right['x0'],
                    'y1': bottom['y0']
                }
                potential_boxes.append(box)
    
    print(f"\n検出された潜在的な矩形: {len(potential_boxes)}")
    for i, box in enumerate(potential_boxes[:5]):
        print(f"  矩形{i}: {box}")


def main():
    # sample2.pdfを解析
    pdf_path = Path(__file__).parent / "sample2.pdf"
    
    if not pdf_path.exists():
        print(f"エラー: sample2.pdfが見つかりません")
        return
    
    print("=== sample2.pdf ページ60の解析 ===")
    print("=" * 50)
    
    # pdfplumberで解析
    analyze_page_60_plumber(pdf_path)
    
    # PyMuPDFで解析
    analyze_page_60_fitz(pdf_path)
    
    # 罫線で囲まれた領域を検出
    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) >= 60:
            page = pdf.pages[59]
            find_bordered_regions(page)


if __name__ == "__main__":
    main()