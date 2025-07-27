@echo off
echo === PyInstaller Test ===

echo Step 1: Activate venv
call venv\Scripts\activate.bat

echo Step 2: Check Python
python --version
where python

echo Step 3: Check pip
where pip

echo Step 4: Install PyInstaller
pip install pyinstaller

echo Step 5: Check PyInstaller
pyinstaller --version
where pyinstaller

echo Step 6: Simple build test
pyinstaller --onefile --windowed --name=TECHZIP1_5_test main.py

echo Step 7: Check result
if exist "dist\TECHZIP1_5_test.exe" (
    echo SUCCESS: dist\TECHZIP1_5_test.exe created
    dir "dist\TECHZIP1_5_test.exe"
) else (
    echo FAILED: No exe found
    if exist "dist" (
        echo dist folder contents:
        dir dist
    )
)

pause