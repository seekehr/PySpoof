@echo off
:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting admin privileges...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

:: Change to the directory of the batch script
cd /d %~dp0

:: Check if virtual environment exists
if not exist .\venv\Scripts\activate (
    echo Virtual environment not found, creating one...
    python -m venv venv
)

:: Activate the virtual environment
call .\venv\Scripts\activate

:: Install required packages
echo Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt

:: Run your Python application
echo Running the application...
python app.py

:: Pause to keep the window open
pause
