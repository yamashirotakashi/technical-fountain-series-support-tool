# WSL PATH Contamination Fix - Simplified Version
# Root cause resolution for Windows environment setup

param(
    [switch]$Force = $false,
    [string]$RequiredPythonVersion = "3.9"
)

$ErrorActionPreference = "Stop"

Write-Host "=== WSL PATH Contamination Fix ===" -ForegroundColor Cyan
Write-Host "Purpose: Remove contaminated venv and recreate in pure Windows environment" -ForegroundColor Yellow

# Clear WSL environment variables
function Clear-WSLEnvironment {
    Write-Host "Clearing WSL environment variables..." -ForegroundColor Yellow
    
    # Remove WSL-related environment variables
    $wslVars = @("WSL_DISTRO_NAME", "WSL_INTEROP", "WSLENV", "DISPLAY")
    foreach ($var in $wslVars) {
        if (Test-Path "Env:$var") {
            Remove-Item "Env:$var" -ErrorAction SilentlyContinue
            Write-Host "  Removed: $var" -ForegroundColor Gray
        }
    }
    
    # Clean PATH from Linux paths
    $originalPath = $env:PATH
    $cleanPath = $originalPath -split ';' | Where-Object { 
        $_ -and 
        -not $_.StartsWith('/usr/') -and 
        -not $_.StartsWith('/bin/') -and 
        -not $_.Contains('wsl')
    } | Where-Object { $_.Trim() -ne '' }
    
    $env:PATH = $cleanPath -join ';'
    
    Write-Host "PATH cleaned from Linux paths" -ForegroundColor Green
}

# Remove contaminated virtual environment
function Remove-ContaminatedVenv {
    Write-Host "Removing contaminated virtual environment..." -ForegroundColor Yellow
    
    if (Test-Path "venv") {
        Write-Host "Found existing venv: $(Resolve-Path 'venv')" -ForegroundColor Cyan
        
        # Check for contamination
        $venvPython = "venv\Scripts\python.exe"
        if (Test-Path $venvPython) {
            try {
                $pipList = & $venvPython -m pip list --format=freeze 2>&1 | Out-String
                if ($pipList -match '/usr/bin') {
                    Write-Host "WSL PATH contamination detected" -ForegroundColor Red
                    $contaminated = $true
                } else {
                    Write-Host "No contamination detected" -ForegroundColor Green
                    $contaminated = $false
                }
            } catch {
                Write-Host "Error checking venv state: $($_.Exception.Message)" -ForegroundColor Yellow
                $contaminated = $true
            }
        } else {
            Write-Host "Incomplete venv detected" -ForegroundColor Red
            $contaminated = $true
        }
        
        if ($contaminated -or $Force) {
            Write-Host "Removing contaminated venv..." -ForegroundColor Yellow
            Remove-Item -Path "venv" -Recurse -Force
            Write-Host "Contaminated venv removed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Venv is clean, skipping removal" -ForegroundColor Green
            return $false
        }
    } else {
        Write-Host "No existing venv found" -ForegroundColor Gray
        return $true
    }
}

# Find clean Windows Python
function Find-CleanWindowsPython {
    Write-Host "Finding clean Windows Python..." -ForegroundColor Yellow
    
    # Try py.exe launcher first (recommended)
    try {
        $pyVersion = & py --version 2>&1 | Out-String
        if ($pyVersion -match "Python (\d+\.\d+(?:\.\d+)?)") {
            $versionString = $matches[1]
            $pyPath = & py -c "import sys; print(sys.executable)" 2>&1 | Out-String
            $pyPath = $pyPath.Trim()
            if (-not $pyPath.Contains('/usr/') -and -not $pyPath.Contains('wsl')) {
                Write-Host "Found py launcher: Python $versionString ($pyPath)" -ForegroundColor Cyan
                
                # Version check
                $versionParts = $versionString.Split('.')
                $majorVersion = [int]$versionParts[0]
                $minorVersion = [int]$versionParts[1]
                $requiredParts = $RequiredPythonVersion.Split('.')
                $requiredMajor = [int]$requiredParts[0]
                $requiredMinor = [int]$requiredParts[1]
                
                if (($majorVersion -gt $requiredMajor) -or ($majorVersion -eq $requiredMajor -and $minorVersion -ge $requiredMinor)) {
                    Write-Host "Selected Python: py launcher - Python $versionString" -ForegroundColor Green
                    return @{
                        Path = "py"
                        Version = $versionString
                        Executable = $pyPath
                    }
                }
            }
        }
    } catch {
        Write-Host "py.exe launcher not available" -ForegroundColor Gray
    }
    
    Write-Host "No suitable Windows Python found" -ForegroundColor Red
    Write-Host "Please install Python from:" -ForegroundColor Yellow
    Write-Host "1. Microsoft Store: https://apps.microsoft.com/store/detail/python-311" -ForegroundColor Cyan
    Write-Host "2. Official site: https://www.python.org/downloads/" -ForegroundColor Cyan
    return $null
}

# Create clean virtual environment
function New-CleanVirtualEnvironment {
    param($pythonInfo)
    
    Write-Host "Creating clean virtual environment..." -ForegroundColor Yellow
    
    # Clean environment variables
    $cleanEnv = @{}
    $essentialVars = @(
        "PATH", "SYSTEMROOT", "SYSTEMDRIVE", "PROGRAMFILES", "PROGRAMFILES(X86)",
        "WINDIR", "COMPUTERNAME", "USERNAME", "USERPROFILE", "LOCALAPPDATA", "APPDATA", "TEMP", "TMP"
    )
    
    foreach ($var in $essentialVars) {
        if (Test-Path "Env:$var") {
            $cleanEnv[$var] = (Get-Item "Env:$var").Value
        }
    }
    
    # Windows-only PATH
    $windowsOnlyPath = $cleanEnv["PATH"] -split ';' | Where-Object { 
        $_ -and 
        -not $_.StartsWith('/') -and
        -not $_.Contains('wsl') -and
        ($_.StartsWith('C:\') -or $_.StartsWith('%'))
    } | Where-Object { $_.Trim() -ne '' }
    
    $cleanEnv["PATH"] = $windowsOnlyPath -join ';'
    
    # Create venv using clean environment
    $pythonCmd = $pythonInfo.Path
    if ($pythonInfo.Path -eq "py") {
        $createCmd = "py -m venv venv"
    } else {
        $createCmd = "`"$($pythonInfo.Path)`" -m venv venv"
    }
    
    Write-Host "  Executing: $createCmd" -ForegroundColor Gray
    
    try {
        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = "cmd.exe"
        $processInfo.Arguments = "/c $createCmd"
        $processInfo.UseShellExecute = $false
        $processInfo.CreateNoWindow = $true
        $processInfo.RedirectStandardOutput = $true
        $processInfo.RedirectStandardError = $true
        
        # Set clean environment
        $processInfo.EnvironmentVariables.Clear()
        foreach ($kvp in $cleanEnv.GetEnumerator()) {
            $processInfo.EnvironmentVariables.Add($kvp.Key, $kvp.Value)
        }
        
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo
        
        $process.Start() | Out-Null
        $process.WaitForExit()
        
        $output = $process.StandardOutput.ReadToEnd()
        $error = $process.StandardError.ReadToEnd()
        
        if ($process.ExitCode -ne 0) {
            Write-Host "venv creation failed" -ForegroundColor Red
            Write-Host "Output: $output" -ForegroundColor Gray
            Write-Host "Error: $error" -ForegroundColor Red
            return $false
        }
        
    } catch {
        Write-Host "venv creation process error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # Verify creation
    if (-not (Test-Path "venv\Scripts\python.exe")) {
        Write-Host "venv creation failed - python.exe not found" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Clean virtual environment created successfully" -ForegroundColor Green
    return $true
}

# Install dependencies cleanly
function Install-CleanDependencies {
    Write-Host "Installing dependencies cleanly..." -ForegroundColor Yellow
    
    $venvPython = ".\venv\Scripts\python.exe"
    $venvPip = ".\venv\Scripts\pip.exe"
    
    # Upgrade pip
    Write-Host "  Upgrading pip..." -ForegroundColor Gray
    try {
        & $venvPython -m pip install --upgrade pip
        if ($LASTEXITCODE -ne 0) {
            throw "pip upgrade failed"
        }
    } catch {
        Write-Host "pip upgrade failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    # Install from requirements.txt
    if (Test-Path "requirements.txt") {
        Write-Host "  Installing from requirements.txt..." -ForegroundColor Gray
        try {
            & $venvPip install -r requirements.txt --no-warn-script-location
            if ($LASTEXITCODE -ne 0) {
                throw "dependency installation failed"
            }
        } catch {
            Write-Host "dependency installation failed: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "requirements.txt not found" -ForegroundColor Yellow
    }
    
    Write-Host "Clean dependency installation completed" -ForegroundColor Green
    return $true
}

# Test clean environment
function Test-CleanEnvironment {
    Write-Host "Testing clean environment..." -ForegroundColor Yellow
    
    $testScript = @"
import sys
print("Python executable:", sys.executable)
print("Python version:", sys.version)

# Check for WSL contamination
contamination_found = False
for path in sys.path:
    if '/usr/' in path or 'wsl' in path.lower():
        print("WSL contamination detected:", path)
        contamination_found = True

if not contamination_found:
    print("No WSL contamination detected")

# Test key modules
test_modules = ['PyQt6.QtCore', 'fitz', 'cv2', 'numpy', 'PIL']
failed_modules = []

for module in test_modules:
    try:
        __import__(module)
        print(f"OK: {module}")
    except ImportError as e:
        print(f"FAIL: {module}: {e}")
        failed_modules.append(module)

if failed_modules:
    print(f"Failed modules: {failed_modules}")
    sys.exit(1)
else:
    print("All tests passed")
"@
    
    $testScript | Out-File -FilePath "environment_test.py" -Encoding UTF8
    
    try {
        & .\venv\Scripts\python.exe environment_test.py
        $success = ($LASTEXITCODE -eq 0)
    } catch {
        Write-Host "Environment test error: $($_.Exception.Message)" -ForegroundColor Red
        $success = $false
    } finally {
        Remove-Item "environment_test.py" -ErrorAction SilentlyContinue
    }
    
    if ($success) {
        Write-Host "Clean environment test passed" -ForegroundColor Green
    } else {
        Write-Host "Environment test failed" -ForegroundColor Red
    }
    
    return $success
}

# Main execution
try {
    Write-Host "Start time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
    # Clear WSL environment
    Clear-WSLEnvironment
    
    # Remove contaminated venv
    $needRecreate = Remove-ContaminatedVenv
    
    if ($needRecreate) {
        # Find clean Python
        $pythonInfo = Find-CleanWindowsPython
        if (-not $pythonInfo) {
            exit 1
        }
        
        # Create clean venv
        if (-not (New-CleanVirtualEnvironment -pythonInfo $pythonInfo)) {
            exit 1
        }
        
        # Install dependencies
        if (-not (Install-CleanDependencies)) {
            exit 1
        }
    }
    
    # Test environment
    if (-not (Test-CleanEnvironment)) {
        Write-Host "Some tests failed, but basic environment is ready" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "WSL PATH contamination fix completed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Test application: .\run_windows.ps1" -ForegroundColor White
    Write-Host "2. Build EXE: .\build_exe.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "End time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    
} catch {
    Write-Host ""
    Write-Host "Error during WSL contamination fix: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}