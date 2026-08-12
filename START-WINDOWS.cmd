@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-Windows.ps1"
set "NPB_EXIT=%ERRORLEVEL%"
echo.
if not "%NPB_EXIT%"=="0" echo Newbie Project Builder ended with error code %NPB_EXIT%.
echo You may close this window after reading the message above.
pause
exit /b %NPB_EXIT%
