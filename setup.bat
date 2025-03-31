if not exist venv (
    echo Creating venv
    python -m venv venv
    ) else (
    echo Recreating venv
    call rmdir /s /q venv
    call python -m venv venv
    )

echo Activating venv
call ".\venv\Scripts\activate.bat"

echo Installing dependencies
call python.exe -m pip install --upgrade pip
call python -m pip install -r "reqs.txt"

echo Starting script
call python "%~dp0src\main.py" --s mover,clockify

echo Script finished

echo Closing
exit /b to ps1