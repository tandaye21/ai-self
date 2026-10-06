@echo off
title AI Self - Training

set PYTHON_PATH=D:\Anaconda\envs\ai_self\python.exe

echo ================================
echo   AI Self - Training
echo ================================
echo.
echo Step 1: Extracting data from chat logs...
"%PYTHON_PATH%" "D:\ai_self\scripts\prepare_data_from_logs.py"
echo.
echo IMPORTANT: Close start.bat before training!
echo Press any key to continue when start.bat is closed...
pause
echo.
echo Step 2: Running LoRA fine-tuning (this may take 3-5 minutes)...
"%PYTHON_PATH%" "D:\ai_self\scripts\train_lora.py"
echo.
echo Done! Restart start.bat to use the new model.
pause
