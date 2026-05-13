#!/bin/bash
echo "=========================================="
echo "  Nifty 200 Stock Screener - Starting..."
echo "=========================================="
echo ""
echo "Installing/checking dependencies..."
pip install -r requirements.txt -q
echo ""
echo "Starting server at http://localhost:5000"
echo "Press Ctrl+C to stop."
echo ""

# Open browser after 2 seconds
(sleep 2 && open "http://localhost:5000" 2>/dev/null || xdg-open "http://localhost:5000" 2>/dev/null) &

python3 app.py
