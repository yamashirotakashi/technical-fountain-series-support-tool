@echo off
echo ========================================
echo   TechZip Single File EXE Build
echo ========================================
echo.

REM Check if pyinstaller is installed
echo Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist "dist\TechZip1.0.exe" del /q "dist\TechZip1.0.exe"
if exist "dist\TechZip1.0_portable.exe" del /q "dist\TechZip1.0_portable.exe"

REM Build single file EXE
echo Building single file EXE...
pyinstaller techzip_windows.spec --onefile

REM Check if build was successful
if exist "dist\TechZip1.0.exe" (
    echo.
    echo Build successful!
    echo Output: dist\TechZip1.0.exe
    echo.
    echo This is a portable single file executable.
    echo You can run it directly without any additional files.
) else (
    echo.
    echo Build failed!
)

echo.
pause