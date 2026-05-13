@echo off
echo ==========================================
echo   Nifty 200 Stock Screener - Starting...
echo ==========================================
echo.
echo Installing/checking dependencies...
pip install -r requirements.txt -q
echo.
echo Starting server at http://localhost:5000
echo Press Ctrl+C to stop.
echo.
start "" http://localhost:5000
python app.py
pause
