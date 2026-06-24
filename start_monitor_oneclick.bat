@echo off
setlocal

cd /d "%~dp0"

if "%MONITOR_HOST%"=="" set "MONITOR_HOST=0.0.0.0"
if "%MONITOR_PORT%"=="" set "MONITOR_PORT=8080"

echo Starting legal sentiment monitor one-click launcher on %MONITOR_HOST%:%MONITOR_PORT%
if not "%MONITOR_BROWSER_URL%"=="" (
    echo Browser override: %MONITOR_BROWSER_URL%
)

uv run python -m api.monitoring.startup_launcher --host %MONITOR_HOST% --port %MONITOR_PORT% --browser-url "%MONITOR_BROWSER_URL%"

pause
