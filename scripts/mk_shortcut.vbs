Set shell = CreateObject("WScript.Shell")
desktop = shell.SpecialFolders("Desktop")

' Main launcher
Set sc = shell.CreateShortcut(desktop & "\分身.lnk")
sc.TargetPath = "D:\ai_self\启动分身.bat"
sc.WorkingDirectory = "D:\ai_self"
sc.IconLocation = "D:\ai_self\icon.ico, 0"
sc.Save()

' Desktop pet
Set sc2 = shell.CreateShortcut(desktop & "\小宠.lnk")
sc2.TargetPath = "D:\Anaconda\envs\ai_self\python.exe"
sc2.Arguments = "D:\ai_self\chat_interface\desktop_pet.py"
sc2.WorkingDirectory = "D:\ai_self"
sc2.IconLocation = "D:\ai_self\icon.ico, 0"
sc2.Save()
