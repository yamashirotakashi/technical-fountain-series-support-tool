# Fix encoding issues in all Python files systematically

Write-Host "=== Fixing All Python File Encodings ===`n" -ForegroundColor Cyan

# Function to convert file to UTF-8
function Convert-ToUTF8 {
    param(
        [string]$FilePath
    )
    
    try {
        # Try different encodings
        $encodings = @(
            [System.Text.Encoding]::Default,
            [System.Text.Encoding]::GetEncoding("shift_jis"),
            [System.Text.Encoding]::GetEncoding("iso-8859-1"),
            [System.Text.Encoding]::UTF8
        )
        
        $content = $null
        foreach ($encoding in $encodings) {
            try {
                $content = [System.IO.File]::ReadAllText($FilePath, $encoding)
                if ($content -and -not ($content -match '[\uFFFD]')) {
                    Write-Host "  ✓ Read with encoding: $($encoding.EncodingName)" -ForegroundColor Green
                    break
                }
            } catch {
                continue
            }
        }
        
        if ($content) {
            # Save as UTF-8 with BOM
            [System.IO.File]::WriteAllText($FilePath, $content, [System.Text.UTF8Encoding]::new($true))
            Write-Host "  ✓ Converted to UTF-8: $FilePath" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ✗ Failed to read: $FilePath" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  ✗ Error converting $FilePath : $_" -ForegroundColor Red
        return $false
    }
}

# Get all Python files
$pythonFiles = Get-ChildItem -Path . -Include *.py -Recurse | Where-Object { $_.FullName -notmatch 'venv|__pycache__|build|dist' }

Write-Host "Found $($pythonFiles.Count) Python files to check`n" -ForegroundColor Yellow

$converted = 0
$failed = 0

foreach ($file in $pythonFiles) {
    Write-Host "Processing: $($file.Name)" -ForegroundColor Cyan
    
    if (Convert-ToUTF8 -FilePath $file.FullName) {
        $converted++
    } else {
        $failed++
    }
    Write-Host ""
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Converted: $converted files" -ForegroundColor Green
Write-Host "Failed: $failed files" -ForegroundColor Red

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")