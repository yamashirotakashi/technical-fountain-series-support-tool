; TechZip - 技術の泉シリーズ制作支援ツール
; AutoHotkey v1 スクリプト（スタートアップ用）
; Ctrl+Shift+I でPowerShell 7を起動してアプリを実行

#NoEnv  ; パフォーマンス向上のため推奨
#SingleInstance Force  ; 重複起動を防ぐ
SendMode Input  ; 推奨される新しいSendMode

; ホットキー: Ctrl+Shift+I
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
    
    ; 実行コマンドを構築 - run_direct.batを使用
    runCommand := appPath . "\run_direct.bat"
    
    ; バッチファイルを直接実行
    Run, %runCommand%, %appPath%
    
    ; 通知（オプション）
    TrayTip, TechZip, 技術の泉シリーズ制作支援ツールを起動しています..., 3, 1
return

; 右クリックメニューに終了オプションを追加
Menu, Tray, Add, 終了, ExitScript
Menu, Tray, Default, 終了

ExitScript:
ExitApp