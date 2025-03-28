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
echo Currently in %~dp0


echo [%date% %time%] Creating venv
if not exist venv\ python -m venv venv
echo [%date% %time%] Activating venv
call ".\venv\Scripts\activate.bat"
echo [%date% %time%] Installing dependencies
call python.exe -m pip install --upgrade pip
call python -m pip install -r "reqs.txt"

echo [%date% %time%] Starting script
call python "%~dp0src\main.py" --s mover,clockify >> %log_path%

echo [%date% %time%] Script finished

echo [%date% %time%] Closing
exit /b

echo [%date% %time%] Should have closed >>  %log_path%
