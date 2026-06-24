@echo off
setlocal

cd /d "%~dp0"

if "%MONITOR_HOST%"=="" set "MONITOR_HOST=127.0.0.1"
if "%MONITOR_PORT%"=="" set "MONITOR_PORT=8080"
if "%MONITOR_BROWSER_URL%"=="" (
    set "MONITOR_BROWSER_URL=http://127.0.0.1:%MONITOR_PORT%/monitor"
)

echo Starting legal sentiment monitor at %MONITOR_BROWSER_URL%
start "" "%MONITOR_BROWSER_URL%"

uv run uvicorn api.main:app --host %MONITOR_HOST% --port %MONITOR_PORT%

pause
