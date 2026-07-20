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

if "%MONITOR_HOST%"=="" set "MONITOR_HOST=127.0.0.1"
if "%MONITOR_PORT%"=="" set "MONITOR_PORT=8080"
if "%MONITOR_BROWSER_URL%"=="" (
    set "MONITOR_BROWSER_URL=http://127.0.0.1:%MONITOR_PORT%/monitor"
)

uv run python -m api.monitoring.startup_launcher --browser-preflight-only
set "BROWSER_PREFLIGHT_EXIT_CODE=%ERRORLEVEL%"
if not "%BROWSER_PREFLIGHT_EXIT_CODE%"=="0" (
    pause
    exit /b %BROWSER_PREFLIGHT_EXIT_CODE%
)

echo Starting legal sentiment monitor at %MONITOR_BROWSER_URL%
start "" "%MONITOR_BROWSER_URL%"

uv run uvicorn api.main:app --host %MONITOR_HOST% --port %MONITOR_PORT%

pause
