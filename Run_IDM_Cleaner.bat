@echo off
title IDM Cleaner & Resetter
color 0A

:: ─── Check for Administrator privileges ───────────────────────────────────
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [!] Not running as Administrator.
    echo     Requesting elevated privileges...
    echo.
    :: Re-launch this batch file as Administrator
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ==================================================
echo    IDM Cleaner ^& Resetter
echo ==================================================
echo.

:: ─── Locate Python ────────────────────────────────────────────────────────
set "PYTHON="

:: Try 'python' command first
python --version >nul 2>&1
if %errorLevel% EQU 0 (
    set "PYTHON=python"
    goto :found_python
)

:: Try 'python3' command
python3 --version >nul 2>&1
if %errorLevel% EQU 0 (
    set "PYTHON=python3"
    goto :found_python
)

:: Try common install paths
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%P (
        set "PYTHON=%%P"
        goto :found_python
    )
)

echo [X] Python not found on this system.
echo     Please install Python from https://www.python.org/downloads/
echo     and make sure to check "Add Python to PATH" during setup.
echo.
pause
exit /b 1

:found_python
echo [✓] Python found: %PYTHON%
echo.

:: ─── Locate the Python script ─────────────────────────────────────────────
set "SCRIPT=%~dp0idm_cleaner.py"

if not exist "%SCRIPT%" (
    echo [X] Script not found: %SCRIPT%
    echo     Make sure idm_cleaner.py is in the same folder as this .bat file.
    echo.
    pause
    exit /b 1
)

echo [✓] Script found: %SCRIPT%
echo.
echo --------------------------------------------------
echo  Starting IDM cleanup...
echo --------------------------------------------------
echo.

:: ─── Run the Python script ────────────────────────────────────────────────
%PYTHON% "%SCRIPT%"

echo.
echo --------------------------------------------------
echo  Cleanup complete!
echo  Please restart your PC for all changes to apply.
echo --------------------------------------------------
echo.
pause
