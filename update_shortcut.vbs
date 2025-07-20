' Update Desktop Shortcut for TechZip
Set WshShell = CreateObject("WScript.Shell")
Set oShortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\TechZip.lnk")

' Set shortcut properties to use run_direct.bat instead
oShortcut.TargetPath = "C:\Users\tky99\DEV\technical-fountain-series-support-tool\run_direct.bat"
oShortcut.WorkingDirectory = "C:\Users\tky99\DEV\technical-fountain-series-support-tool"
oShortcut.IconLocation = "C:\Users\tky99\DEV\technical-fountain-series-support-tool\venv_windows\Scripts\python.exe"
oShortcut.Description = "技術の泉シリーズ制作支援ツール"
oShortcut.Hotkey = "CTRL+SHIFT+I"

' Save the shortcut
oShortcut.Save

' Show success message
MsgBox "Desktop shortcut updated!" & vbCrLf & vbCrLf & _
       "The shortcut now uses run_direct.bat" & vbCrLf & _
       "Double-click the TechZip icon to launch the app", _
       vbInformation, "TechZip Shortcut Updated"