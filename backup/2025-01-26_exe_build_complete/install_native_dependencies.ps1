# Install dependencies for native Windows Python

Set-Location $PSScriptRoot

Write-Host "=== Installing TechZip Dependencies (Native) ===" -ForegroundColor Cyan
Write-Host "Target: System Python 3.13.5" -ForegroundColor Yellow
Write-Host ""

# Upgrade pip first
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip

# Install each dependency
Write-Host "`nInstalling dependencies..." -ForegroundColor Green
$dependencies = @(
    "PyQt5==5.15.10",
    "requests==2.31.0",
    "urllib3<2.0",
    "google-api-python-client==2.100.0",
    "google-auth-httplib2==0.1.1",
    "google-auth-oauthlib==1.1.0",
    "python-docx==1.1.0",
    "python-dotenv==1.0.0"
)

foreach ($dep in $dependencies) {
    Write-Host "Installing $dep..." -ForegroundColor Yellow
    python -m pip install $dep
}

# Verify installation
Write-Host "`n=== Verifying Installation ===" -ForegroundColor Cyan
python -c @"
import sys
print(f'Python: {sys.version}')
print(f'Executable: {sys.executable}')
print('\nChecking imports:')
try:
    import PyQt5
    print('✓ PyQt5')
    import requests
    print('✓ requests')
    from google.oauth2 import service_account
    print('✓ google.auth')
    import docx
    print('✓ python-docx')
    import dotenv
    print('✓ python-dotenv')
    print('\nAll dependencies installed successfully!')
except ImportError as e:
    print(f'✗ Error: {e}')
"@

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")