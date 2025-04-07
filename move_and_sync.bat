@echo off
REM Setting directory to script
cd /d %~dp0


REM Get current date and set variables
for /f "tokens=2-4 delims=/.- " %%a in ('date /t') do (
    set year=%%c
    set month=%%b
    set day=%%a
)

REM Check Month Directory
if not exist logs\%year%\%month%\ md logs\%year%\%month%

REM Set log path
set log_path=.\logs\%year%\%month%\%day%.log
echo Currently in %cd%
echo Currently in %cd% >> %log_path%

REM Ensure Python exists
if not exist "%~dp0venv\Scripts\python.exe" (
    echo [%date% %time%] Python executable not found! Exiting...
    echo [%date% %time%] Python executable not found! Exiting... >> %log_path%
    exit /b 1
)

echo [%date% %time%] Starting script 
echo [%date% %time%] Starting script >> %log_path%

REM Run the Python script and redirect output to console
call "%~dp0venv\Scripts\python.exe" "%~dp0src\main.py" -notion -clockify >> %log_path% 2>&1

echo [%date% %time%] Script finished
echo [%date% %time%] Script finished >>  %log_path%

echo [%date% %time%] Closing
echo [%date% %time%] Closing >>  %log_path%
exit /b

echo [%date% %time%] Should have closed >>  %log_path%