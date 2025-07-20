# AutoHotkey Download Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AutoHotkey Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "Opening AutoHotkey download page..." -ForegroundColor Yellow
    Write-Host ""
    
    # Open download page
    Start-Process "https://www.autohotkey.com/download/ahk-v2.exe"
    
    Write-Host "Download instructions:" -ForegroundColor Green
    Write-Host "1. Download will start automatically" -ForegroundColor White
    Write-Host "2. Run the installer" -ForegroundColor White
    Write-Host "3. Choose 'Express Installation'" -ForegroundColor White
    Write-Host "4. After installation, run install_startup.bat again" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: AutoHotkey v2 is recommended" -ForegroundColor Yellow
} else {
    Write-Host "Downloading AutoHotkey v2..." -ForegroundColor Green
    $url = "https://www.autohotkey.com/download/ahk-v2.exe"
    $output = "$env:TEMP\AutoHotkey_Setup.exe"
    
    try {
        Invoke-WebRequest -Uri $url -OutFile $output
        Write-Host "Download complete!" -ForegroundColor Green
        Write-Host "Starting installer..." -ForegroundColor Yellow
        Start-Process -FilePath $output -Wait
        Write-Host "Installation complete!" -ForegroundColor Green
    } catch {
        Write-Host "Download failed. Opening browser..." -ForegroundColor Red
        Start-Process $url
    }
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")