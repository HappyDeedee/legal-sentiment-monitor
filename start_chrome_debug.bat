@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "PROFILE_DIR=%PROJECT_DIR%browser_data\manual_chrome_9222"
set "CHROME_EXE="

if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
  set "CHROME_EXE=C:\Program Files\Google\Chrome\Application\chrome.exe"
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
  set "CHROME_EXE=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
  set "CHROME_EXE=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
)

if "%CHROME_EXE%"=="" (
  echo Chrome was not found. Please install Google Chrome or edit this file with your Chrome path.
  pause
  exit /b 1
)

if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"

echo Starting Chrome with remote debugging on 127.0.0.1:9222...
start "" "%CHROME_EXE%" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%PROFILE_DIR%" ^
  --no-first-run ^
  --no-default-browser-check ^
  "https://www.douyin.com/"

echo Chrome started. Keep this Chrome window open while running MediaCrawler.
timeout /t 3 >nul
