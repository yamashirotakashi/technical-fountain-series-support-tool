@echo off
call venv\Scripts\activate.bat
pip install pyinstaller
pyinstaller techzip_windows.spec --clean --noconfirm
if exist "dist\TECHZIP1.5\TECHZIP1.5.exe" (
    echo BUILD SUCCESS: dist\TECHZIP1.5\TECHZIP1.5.exe
    dir "dist\TECHZIP1.5\TECHZIP1.5.exe"
) else (
    echo BUILD FAILED
)
pause