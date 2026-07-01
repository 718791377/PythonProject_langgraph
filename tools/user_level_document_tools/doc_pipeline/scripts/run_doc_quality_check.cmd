@echo off
setlocal
set SCRIPT_DIR=%~dp0
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_doc_quality_check.ps1" %*
exit /b %ERRORLEVEL%
