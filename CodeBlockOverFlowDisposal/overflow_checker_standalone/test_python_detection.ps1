# Python検出のテストスクリプト
param(
    [string]$RequiredVersion = "3.9"  # 変数名を変更して競合回避
)

Write-Host "=== Python検出テスト ===" -ForegroundColor Cyan
Write-Host "要求バージョン: $RequiredVersion" -ForegroundColor Yellow

# 複数のPythonコマンドを試行
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    Write-Host "`n$cmd を確認中..." -ForegroundColor Yellow
    
    try {
        # バージョン取得
        $pythonVersion = (& $cmd --version 2>&1) | Out-String
        $pythonVersion = $pythonVersion.Trim()
        Write-Host "  出力: '$pythonVersion'" -ForegroundColor Gray
        
        # 正規表現でバージョン抽出
        if ($pythonVersion -match "Python (\d+\.\d+(?:\.\d+)?)") {
            $versionString = $matches[1]
            Write-Host "  抽出バージョン: '$versionString'" -ForegroundColor Cyan
            
            # 簡単な文字列比較
            Write-Host "  パラメータRequiredVersionの値: '$RequiredVersion'" -ForegroundColor Magenta
            
            $versionParts = $versionString.Split('.')
            $requiredParts = $RequiredVersion.Split('.')
            
            Write-Host "  検出部分: $($versionParts -join ', ')" -ForegroundColor Gray
            Write-Host "  要求部分: $($requiredParts -join ', ')" -ForegroundColor Gray
            
            if ($versionParts.Length -ge 2 -and $requiredParts.Length -ge 2) {
                $majorVersion = [int]$versionParts[0]
                $minorVersion = [int]$versionParts[1]
                $requiredMajor = [int]$requiredParts[0]
                $requiredMinor = [int]$requiredParts[1]
                
                Write-Host "  比較: $majorVersion.$minorVersion vs $requiredMajor.$requiredMinor" -ForegroundColor Gray
                
                if (($majorVersion -gt $requiredMajor) -or 
                    ($majorVersion -eq $requiredMajor -and $minorVersion -ge $requiredMinor)) {
                    Write-Host "  ✅ $cmd : Python $versionString は要件を満たします" -ForegroundColor Green
                } else {
                    Write-Host "  ❌ $cmd : Python $versionString は要件未満です" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "  ❌ バージョン情報が解析できません" -ForegroundColor Red
        }
    } catch {
        Write-Host "  ❌ $cmd の実行に失敗: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== テスト完了 ===" -ForegroundColor Cyan