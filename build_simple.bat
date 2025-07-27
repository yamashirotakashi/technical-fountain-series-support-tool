@echo off
call venv\Scripts\activate.bat
pyinstaller techzip_windows.spec --clean --noconfirm
echo Build completed. Check dist\TECHZIP1.5\TECHZIP1.5.exe
pause