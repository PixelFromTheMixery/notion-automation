@echo off
REM Set environment variable
set api_key=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
set log_path=C:\Users\Aya\Documents\Github\notion-automation\logfile.log

REM Echo the environment variable
echo The API key is: %api_key%

REM Add a timestamp to the log
echo [%date% %time%] Starting script >> %log_path%

REM Activate the virtual environment
call "C:\Users\Aya\Documents\Github\notion-automation\venv\Scripts\activate.bat"

REM Add a timestamp before pip install
echo [%date% %time%] Installing dependencies >>  %log_path%
python -m pip install -r "C:\Users\Aya\Documents\Github\notion-automation\reqs.txt" >>  %log_path% 2>&1

REM Add a timestamp before running the Python script
echo [%date% %time%] Running Python script >>  %log_path%

REM Run the Python script and redirect output to console
python "C:\Users\Aya\Documents\Github\notion-automation\src\main.py" >> %log_path% 2>&1
deactivate

REM Add a completion timestamp
echo [%date% %time%] Script finished >>  %log_path%

REM Close
echo [%date% %time%] Closing >>  %log_path%
exit /b

echo [%date% %time%] Should have closed >>  %log_path%

