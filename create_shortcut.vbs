' Create Desktop Shortcut for TechZip
Set WshShell = CreateObject("WScript.Shell")
Set oShortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\TechZip.lnk")

' Set shortcut properties
oShortcut.TargetPath = "C:\Users\tky99\DEV\technical-fountain-series-support-tool\run_techzip.bat"
oShortcut.WorkingDirectory = "C:\Users\tky99\DEV\technical-fountain-series-support-tool"
oShortcut.IconLocation = "powershell.exe"
oShortcut.Description = "技術の泉シリーズ制作支援ツール"
oShortcut.Hotkey = "CTRL+SHIFT+I"

' Save the shortcut
oShortcut.Save

' Show success message
MsgBox "Desktop shortcut created!" & vbCrLf & vbCrLf & _
       "You can now:" & vbCrLf & _
       "1. Double-click the TechZip icon on desktop" & vbCrLf & _
       "2. Press Ctrl+Shift+I (when desktop is active)", _
       vbInformation, "TechZip Shortcut Created"