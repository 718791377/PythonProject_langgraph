@echo off
setlocal
set SCRIPT_DIR=%~dp0
set TEST_FILE=%SCRIPT_DIR%install-codex-user-level-team-mode.test.ps1

if not exist "%TEST_FILE%" (
  echo Test file not found: %TEST_FILE%
  exit /b 1
)

C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -Command "& { & '%TEST_FILE%' }"
exit /b %ERRORLEVEL%
