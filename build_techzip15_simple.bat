@echo off
echo === TECHZIP1.5 Build Script ===
echo.

REM Check current environment
echo 1. Checking current Python environment...
where python
where pip
echo.

echo 2. Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo 3. Checking Python after activation...
where python
where pip
python --version
echo.

echo 4. Installing PyInstaller if needed...
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)
echo.

echo 5. Checking PyInstaller version...
pyinstaller --version
echo.

echo 6. Starting TECHZIP1.5.exe build...
echo Using Python: 
python -c "import sys; print(sys.executable)"
echo.

echo Running PyInstaller...
pyinstaller techzip_windows.spec --clean --noconfirm --log-level=INFO

echo.
echo === Build Result Check ===
if exist "dist\TECHZIP1.5\TECHZIP1.5.exe" (
    echo Build SUCCESS!
    echo Output location: %CD%\dist\TECHZIP1.5\TECHZIP1.5.exe
    dir "dist\TECHZIP1.5\TECHZIP1.5.exe"
) else (
    echo Build FAILED
    echo dist\TECHZIP1.5\TECHZIP1.5.exe not found
    echo.
    echo Checking directory structure:
    if exist "dist" (
        dir /s "dist"
    ) else (
        echo dist directory does not exist
    )
)

echo.
echo === Build Complete ===
pause