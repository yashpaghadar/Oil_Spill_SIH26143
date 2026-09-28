@echo off
title OILED - Case & Scenario Generator
echo ========================================================
echo   Regenerating All Demonstration Cases ^& Dashboards
echo ========================================================
echo.
call "%~dp0.venv\Scripts\activate.bat"
python -m oiled.cli generate --cases-root "%~dp0oiled\cases"
echo.
echo ========================================================
echo   Cases regenerated successfully!
echo   Inspect at oiled\docs\index.html or cases\case-001\
echo ========================================================
pause
