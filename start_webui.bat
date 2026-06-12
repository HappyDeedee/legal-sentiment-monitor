@echo off
setlocal

cd /d "%~dp0"

echo Starting legal sentiment monitor at http://127.0.0.1:8080/monitor
start "" "http://127.0.0.1:8080/monitor"

uv run uvicorn api.main:app --host 127.0.0.1 --port 8080

pause
