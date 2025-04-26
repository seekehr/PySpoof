@echo off
:: Check for admin privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting admin privileges...
    :: Quote and properly escape arguments for PowerShell
    if "%*"=="" (
        powershell -Command "Start-Process '%~f0' -Verb runAs"
    ) else (
        powershell -Command "Start-Process '%~f0' -ArgumentList '%*' -Verb runAs"
    )
    exit /b
)

:: Change to the directory of the batch script
cd /d %~dp0

:: Check if virtual environment exists
if not exist .\.venv\Scripts\activate (
    echo Virtual environment not found, creating one...
    python -m venv venv
)

:: Activate the virtual environment
call .\.venv\Scripts\activate

:: Install required packages only if they are missing or outdated
echo Checking installed packages...

:: Generate installed packages list
pip freeze > installed_packages.txt

:: Sort both requirements.txt and installed packages list, then compare
sort requirements.txt > sorted_requirements.txt
sort resources/installed_packages.txt > sorted_installed_packages.txt

fc sorted_requirements.txt sorted_installed_packages.txt > nul
if %errorlevel% neq 0 (
    echo Requirements have changed. Installing/upgrading packages...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo No changes in requirements. Skipping installation.
)

:: Clean up sorted files
del sorted_requirements.txt
del sorted_installed_packages.txt

:: Parse arguments
set output_arg=   :: Default value for output_arg (false)

:parse_args
if "%~1"=="" goto run_app
if /i "%~1"=="--o" (
    :: Set output_arg to true when -o flag is present (default behavior)
    set output_arg=true
    shift
    goto parse_args
)
if /i "%~1"=="--spoof" (
    set spoof_mode=--spoof
    shift
    goto parse_args
)
shift
goto parse_args

:run_app
:: Run your Python application with arguments
echo Running the application...
if "%output_arg%"=="true" (
    echo Output flag is set, running with output.
    :: Run Python app with output flag
    if defined spoof_mode (
        python app.py --o %spoof_mode%
    ) else (
        python app.py --o
    )
) else (
    echo Output flag is not set, running without output.
    :: Run Python app without output flag
    if defined spoof_mode (
        python app.py %spoof_mode%
    ) else (
        python app.py
    )
)

:: Pause to keep the window open
pause
