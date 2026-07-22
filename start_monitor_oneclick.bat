@echo off
setlocal

cd /d "%~dp0"

where uv >nul 2>nul
if errorlevel 1 (
    echo ERROR: Required command "uv" was not found.
    echo Install uv from https://docs.astral.sh/uv/ and run this launcher again.
    pause
    exit /b 1
)

if "%MONITOR_HOST%"=="" set "MONITOR_HOST=0.0.0.0"
if "%MONITOR_PORT%"=="" set "MONITOR_PORT=8080"
if "%MONITOR_BROWSER_COOKIE_SYNC_ENABLED%"=="" set "MONITOR_BROWSER_COOKIE_SYNC_ENABLED=true"
if "%MONITOR_ALLOW_LOCAL_LOGIN_WINDOW%"=="" set "MONITOR_ALLOW_LOCAL_LOGIN_WINDOW=true"
if "%MONITOR_LOGIN_QR_HEADLESS%"=="" set "MONITOR_LOGIN_QR_HEADLESS=false"

echo Starting legal sentiment monitor one-click launcher on %MONITOR_HOST%:%MONITOR_PORT%
if not "%MONITOR_BROWSER_URL%"=="" (
    echo Browser override: %MONITOR_BROWSER_URL%
)

uv run python -m api.monitoring.startup_launcher --host %MONITOR_HOST% --port %MONITOR_PORT% --browser-url "%MONITOR_BROWSER_URL%"
set "STARTUP_EXIT_CODE=%ERRORLEVEL%"

pause
exit /b %STARTUP_EXIT_CODE%
