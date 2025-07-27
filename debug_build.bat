@echo off
echo Checking PyInstaller installation and build process...
echo.

call venv\Scripts\activate.bat

echo Python version:
python --version
echo.

echo PyInstaller version:
pyinstaller --version
echo.

echo Current directory contents:
dir
echo.

echo Running PyInstaller with verbose output:
pyinstaller techzip_windows.spec --clean --noconfirm --log-level=DEBUG

echo.
echo Checking if dist folder exists:
if exist "dist" (
    echo dist folder exists
    dir dist /s
) else (
    echo dist folder does not exist
)

pause