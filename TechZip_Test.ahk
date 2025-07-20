; TechZip Test Script
; Simple test to verify AutoHotkey is working

#NoEnv
#SingleInstance Force
SendMode Input

; Show a message box when script starts
MsgBox, 0, TechZip Test, AutoHotkey script is running!`n`nPress Ctrl+Shift+I to test hotkey`nPress Ctrl+Shift+Q to quit, 5

; Test hotkey
^+i::
    MsgBox, 0, Hotkey Test, Ctrl+Shift+I was pressed!`n`nNow launching TechZip...
    
    ; Try to launch the app
    appPath := "C:\Users\tky99\DEV\technical-fountain-series-support-tool"
    
    ; Check which PowerShell to use
    pwsh7Path := "C:\Program Files\PowerShell\7\pwsh.exe"
    IfNotExist, %pwsh7Path%
    {
        pwsh7Path := "powershell.exe"
    }
    
    ; Show what we're about to run
    runCommand := pwsh7Path . " -NoExit -WorkingDirectory """ . appPath . """ -Command ""& .\run_windows.ps1"""
    MsgBox, 0, Debug Info, About to run:`n%runCommand%
    
    ; Run the command
    Run, %runCommand%
return

; Quit hotkey
^+q::
    MsgBox, 0, Exiting, Exiting TechZip hotkey script, 2
    ExitApp
return