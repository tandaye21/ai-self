Set ws = WScript.CreateObject("WScript.Shell")
desktop = ws.SpecialFolders("Desktop")

Set sc1 = ws.CreateShortcut(desktop & "\分身.lnk")
sc1.TargetPath = "wscript.exe"
sc1.Arguments = "D:\ai_self\launcher.vbs"
sc1.WorkingDirectory = "D:\ai_self"
sc1.Description = "AI分身"
sc1.IconLocation = "D:\ai_self\icon.ico"
sc1.Save()

Set sc2 = ws.CreateShortcut(desktop & "\小宠.lnk")
sc2.TargetPath = "D:\Anaconda\envs\ai_self\python.exe"
sc2.Arguments = "D:\ai_self\chat_interface\desktop_pet.py"
sc2.WorkingDirectory = "D:\ai_self"
sc2.Description = "桌面小宠"
sc2.IconLocation = "D:\ai_self\icon.ico"
sc2.Save()
