@echo off
title AI Self - 分身

set PYTHON_PATH=D:\Anaconda\envs\ai_self\python.exe

echo ================================
echo   AI Self - Starting...
echo ================================
echo.

if not exist "D:\ai_self\model\Qwen\Qwen2___5-7B-Instruct\config.json" (
    echo ERROR: Model file not found!
    pause
    exit /b
)

echo Model found. Starting web interface...
echo.
echo Open http://127.0.0.1:7860 after startup
echo Waiting for model to load (about 1-2 minutes)...
echo.
echo IMPORTANT: Keep this window open while using
echo.
"%PYTHON_PATH%" "D:\ai_self\chat_interface\app.py"
