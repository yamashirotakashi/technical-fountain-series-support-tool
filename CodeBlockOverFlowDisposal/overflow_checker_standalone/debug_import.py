#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import debugging script
"""

import sys
import traceback
from pathlib import Path

# パス設定
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

print(f"Current directory: {current_dir}")
print("Python paths:")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}: {path}")

try:
    print("\n1. Importing utils.windows_utils...")
    from utils.windows_utils import setup_windows_environment
    print("✓ utils.windows_utils imported successfully")
    
    print("\n2. Importing core.pdf_processor...")
    from core.pdf_processor import PDFOverflowProcessor
    print("✓ core.pdf_processor imported successfully")
    
    print("\n3. Importing gui.result_dialog...")
    from gui.result_dialog import OverflowResultDialog
    print("✓ gui.result_dialog imported successfully")
    
    print("\n4. Importing gui.main_window...")
    from gui.main_window import OverflowCheckerMainWindow
    print("✓ gui.main_window imported successfully")
    
except Exception as e:
    print(f"\n❌ Error occurred: {e}")
    print("\nFull traceback:")
    traceback.print_exc()