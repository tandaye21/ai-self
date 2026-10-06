On Error Resume Next
Set fso = CreateObject("Scripting.FileSystemObject")
Set log = fso.CreateTextFile("D:\ai_self\shortcut_log.txt", True)

Set shell = CreateObject("WScript.Shell")
desktop = shell.SpecialFolders("Desktop")
log.WriteLine "Desktop: " & desktop

Set sc = shell.CreateShortcut(desktop & "\分身.lnk")
log.WriteLine "Shortcut created"
sc.TargetPath = "D:\ai_self\启动分身.bat"
sc.WorkingDirectory = "D:\ai_self"
sc.IconLocation = "D:\ai_self\icon.ico, 0"
sc.Save()
log.WriteLine "Saved"

log.Close()
