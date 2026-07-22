@echo off
setlocal

cd /d "%~dp0"

set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%POWERSHELL_EXE%" (
    echo ERROR: Windows PowerShell was not found.
    pause
    exit /b 1
)

"%POWERSHELL_EXE%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\windows_oneclick_bootstrap.ps1" -Mode Detached
set "STARTUP_EXIT_CODE=%ERRORLEVEL%"

pause
exit /b %STARTUP_EXIT_CODE%
