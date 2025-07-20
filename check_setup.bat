@echo off
echo ========================================
echo TechZip Setup Check
echo ========================================
echo.

cd /d "C:\Users\tky99\DEV\technical-fountain-series-support-tool"

echo [1] Current directory:
echo %CD%
echo.

echo [2] Python files:
dir *.py /b
echo.

echo [3] Virtual environments:
if exist "venv_windows" (
    echo Found: venv_windows
    dir venv_windows\Scripts\python.exe
) else (
    echo Not found: venv_windows
)

if exist "venv" (
    echo Found: venv
    dir venv\Scripts\python.exe
) else (
    echo Not found: venv
)
echo.

echo [4] Python version:
python --version
echo.

echo [5] Requirements file:
if exist "requirements.txt" (
    echo Found requirements.txt
) else (
    echo Not found: requirements.txt
)
echo.

echo [6] Setup instructions:
echo If virtual environment is missing, run:
echo    python -m venv venv_windows
echo    venv_windows\Scripts\activate
echo    pip install -r requirements.txt
echo.

pause