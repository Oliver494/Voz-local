@echo off
setlocal
cd /d "%~dp0"
echo Voz Local - Install and start / Instalar e iniciar
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install-windows.ps1"
set "VOZ_EXIT=%ERRORLEVEL%"
if not "%VOZ_EXIT%"=="0" (
  echo.
  echo Installation failed. Read the message above. / Revisa el error anterior.
)
pause
exit /b %VOZ_EXIT%
