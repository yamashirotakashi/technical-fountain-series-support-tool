; TechZip - 技術の泉シリーズ制作支援ツール
; AutoHotkey v1 スクリプト（互換性のため）
; Ctrl+Shift+I でPowerShell 7を起動してアプリを実行

#SingleInstance Force
#NoTrayIcon

; Ctrl+Shift+I ホットキー設定
^+i::
    ; アプリのパス
    appPath := "C:\Users\tky99\DEV\technical-fountain-series-support-tool"
    
    ; PowerShell 7のパスを確認（通常のインストール場所）
    pwsh7Path := "C:\Program Files\PowerShell\7\pwsh.exe"
    
    ; PowerShell 7が存在しない場合は通常のPowerShellを使用
    IfNotExist, %pwsh7Path%
    {
        pwsh7Path := "powershell.exe"
    }
    
    ; 実行コマンドを構築
    runCommand := pwsh7Path . " -NoExit -WorkingDirectory """ . appPath . """ -Command ""& .\run_windows.ps1"""
    
    ; PowerShellを起動してアプリを実行
    try {
        Run, %runCommand%
        
        ; 通知を表示（オプション）
        TrayTip, TechZip, 技術の泉シリーズ制作支援ツールを起動しています..., 1
    } catch e {
        MsgBox, 16, TechZip起動エラー, エラーが発生しました: %e%
    }
return