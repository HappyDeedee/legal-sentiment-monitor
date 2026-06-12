@echo off
setlocal

cd /d "%~dp0"

if "%MONITOR_HOST%"=="" set "MONITOR_HOST=0.0.0.0"
if "%MONITOR_PORT%"=="" set "MONITOR_PORT=8080"

echo Starting legal sentiment monitor service on %MONITOR_HOST%:%MONITOR_PORT%
echo Monitor page: http://%MONITOR_HOST%:%MONITOR_PORT%/monitor

uv run uvicorn api.main:app --host %MONITOR_HOST% --port %MONITOR_PORT%
