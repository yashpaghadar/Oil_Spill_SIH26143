@echo off
title OILED - Test Suite
echo ========================================================
echo   Running OILED Automated Test Suite (PyTest)
echo ========================================================
echo.
call "%~dp0.venv\Scripts\activate.bat"
python -m pytest "%~dp0oiled\tests" -v
echo.
echo ========================================================
echo   Test run finished.
echo ========================================================
pause
