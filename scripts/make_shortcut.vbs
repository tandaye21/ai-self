Set shell = CreateObject("WScript.Shell")
desktop = shell.ExpandEnvironmentStrings("%USERPROFILE%") & "\Desktop"
Set sc = shell.CreateShortcut(desktop & "\AI-Self.lnk")
sc.TargetPath = "D:\ai_self\启动分身.bat"
sc.WorkingDirectory = "D:\ai_self"
sc.IconLocation = "D:\ai_self\icon.ico"
sc.Save()
