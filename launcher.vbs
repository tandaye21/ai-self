' AI 分身 - 启动器
Set ws = CreateObject("WScript.Shell")
ws.CurrentDirectory = "D:\ai_self"
ws.Run "D:\Anaconda\envs\ai_self\python.exe D:\ai_self\chat_interface\app.py", 1, False
