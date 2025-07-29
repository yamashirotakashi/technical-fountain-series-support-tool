# -*- coding: utf-8 -*-
# PowerShell実行用スクリプト
# CodeBlock Overflow Checker - 独立版

# 現在のディレクトリをPythonパスに追加してアプリケーションを実行

$env:PYTHONPATH = $PWD
python main.py