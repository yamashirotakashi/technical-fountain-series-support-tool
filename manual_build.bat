@echo off
echo Manual PyInstaller Build
echo.

REM Step by step manual approach
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller

echo Building TECHZIP1.5.exe...
python -m PyInstaller techzip_windows.spec --clean --noconfirm

echo Checking result...
if exist "dist\TECHZIP1.5\TECHZIP1.5.exe" (
    echo BUILD SUCCESS!
    echo File: %CD%\dist\TECHZIP1.5\TECHZIP1.5.exe
    dir "dist\TECHZIP1.5\TECHZIP1.5.exe"
) else (
    echo BUILD FAILED!
    echo Checking what was created...
    if exist "dist" (
        dir /s dist
    ) else (
        echo No dist folder created
    )
)

pause