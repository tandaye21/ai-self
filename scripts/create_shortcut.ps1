$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')

# 删除旧的
$old = "$desktop\分身.lnk"
if (Test-Path $old) { Remove-Item $old }

# 创建新的，用英文名避免乱码
$sc = $ws.CreateShortcut("$desktop\AI-Self.lnk")
$sc.TargetPath = 'D:\ai_self\启动分身.bat'
$sc.WorkingDirectory = 'D:\ai_self'
$sc.Description = 'AI 分身 - 桌面小宠'
$sc.IconLocation = 'D:\ai_self\icon.ico'
$sc.Save()
Write-Host 'OK'
