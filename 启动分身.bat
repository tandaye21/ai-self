@echo off
cd /d D:\ai_self
title AI 分身

echo.
echo   AI 分身 - 正在启动
echo   ============================
echo.
echo   模型加载需要 1-2 分钟，请耐心等待...
echo   启动后自动打开浏览器 http://127.0.0.1:7860
echo.
echo   关闭此窗口 = 关闭 AI 分身
echo   ============================
echo.

"D:\Anaconda\envs\ai_self\python.exe" "D:\ai_self\chat_interface\app.py"

pause
