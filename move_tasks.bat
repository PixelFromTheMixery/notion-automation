@echo off
REM Set environment variable
set api_key=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

REM Setting directory to script
cd /d %~dp0

REM Get current date in YYYY-MM-DD format
for /f "tokens=2-4 delims=/.- " %%a in ('date /t') do (
    set year=%%c
    set month=%%b
    set day=%%a
)

REM Create folder test
mkdir test

REM Check Month Directory
if not exist logs\%year%\%month%\ mkdir logs\%year%\%month%

REM Set log path
set log_path=.\logs\%year%\%month%\%day%.log
echo Currently in %cd% >> %log_path%

REM Echo the environment variable
echo The API key is: %api_key%

REM Add a timestamp to the log
echo [%date% %time%] Starting script >> %log_path%

REM Activate the virtual environment
call ".\venv\Scripts\activate.bat"

REM Add a timestamp before pip install
echo [%date% %time%] Installing dependencies >>  %log_path%
python -m pip install -r "reqs.txt" >>  %log_path% 2>&1

REM Add a timestamp before running the Python script
echo [%date% %time%] Running Python script at: "%~dp0src\main.py"  >>  %log_path%

REM Run the Python script and redirect output to console
python "%~dp0src\main.py" >> %log_path% 2>&1
deactivate

REM Add a completion timestamp
echo [%date% %time%] Script finished >>  %log_path%

REM Close
echo [%date% %time%] Closing >>  %log_path%
exit /b

echo [%date% %time%] Should have closed >>  %log_path%