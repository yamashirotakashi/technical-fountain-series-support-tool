@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo Technical Fountain Series Support Tool (Native)
python main.py
pause