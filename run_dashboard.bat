@echo off
title OILED - Tactical Dashboard Server
echo ========================================================
echo   OILED: Satellite Oil Spill Detection ^& Attribution
echo   Smart India Hackathon 2026 - SIH26143 (NTRO)
echo ========================================================
echo.
echo Launching your browser to the Tactical Map Dashboard...
start "" "http://127.0.0.1:8765/index.html"
echo Serving dashboard at http://127.0.0.1:8765/
echo (Press Ctrl+C in this window anytime to stop the server)
echo.
call "%~dp0.venv\Scripts\activate.bat"
python -m oiled.cli serve --dir "%~dp0oiled\docs" --port 8765
pause
