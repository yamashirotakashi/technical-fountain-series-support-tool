@echo off
echo ========================================
echo   TechZip EXE Build (Simple)
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
if exist "dist\TechZip1.0" rmdir /s /q "dist\TechZip1.0"

REM Build EXE
echo Building EXE...
pyinstaller techzip_windows.spec

REM Check if build was successful
if exist "dist\TechZip1.0\TechZip1.0.exe" (
    echo.
    echo Build successful!
    echo Output: dist\TechZip1.0\TechZip1.0.exe
    
    REM Copy README
    if exist README.md (
        copy README.md "dist\TechZip1.0\" >nul
    )
    
    REM Create startup batch
    echo @echo off > "dist\TechZip1.0\TechZip_Start.bat"
    echo echo TechZip - Technical Fountain Series Production Support Tool >> "dist\TechZip1.0\TechZip_Start.bat"
    echo echo. >> "dist\TechZip1.0\TechZip_Start.bat"
    echo start "" "%%~dp0TechZip1.0.exe" >> "dist\TechZip1.0\TechZip_Start.bat"
    
    echo.
    echo Files created:
    echo - dist\TechZip1.0\TechZip1.0.exe
    echo - dist\TechZip1.0\TechZip_Start.bat
) else (
    echo.
    echo Build failed!
)

echo.
pause