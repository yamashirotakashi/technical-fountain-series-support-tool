@echo off
echo ========================================
echo TechZip Direct Launcher
echo ========================================
echo.

cd /d "C:\Users\tky99\DEV\technical-fountain-series-support-tool"

echo Checking for virtual environment...
if exist "venv_windows\Scripts\activate.bat" (
    echo Found venv_windows
    call venv_windows\Scripts\activate.bat
    echo Virtual environment activated
) else if exist "venv\Scripts\activate.bat" (
    echo Found venv
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo No virtual environment found
    echo Using system Python
)

echo.
echo Starting application...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo Error occurred. Error code: %errorlevel%
    echo.
    echo Checking Python installation...
    python --version
    
    echo.
    echo Checking if main.py exists...
    if exist main.py (
        echo main.py found
    ) else (
        echo ERROR: main.py not found!
    )
)

echo.
pause