@echo off
cd /d "%~dp0"
py -3 lan_server_funnel.py
if errorlevel 1 (
  echo.
  echo Startup failed. Read the error above, then press any key to close.
  pause >nul
)
