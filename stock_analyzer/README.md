# 📈 Nifty 500 Stock Screener

Automates your daily stock analysis using your **44 SMA + RSI strategy** on 15-min charts.

---

## ⚡ Quick Start

### Step 1 — Install Python (if not installed)
Download from https://www.python.org/downloads/ (Python 3.9+)

### Step 2 — Install dependencies
Open terminal / command prompt in this folder and run:

```bash
pip install -r requirements.txt
```

### Step 3 — Run the app

**Windows:**
```
run.bat
```

**Mac / Linux:**
```bash
bash run.sh
```

Or directly:
```bash
python app.py
```

### Step 4 — Open your browser
Go to: **http://localhost:5000**

### Step 5 — Click "Run Analysis"
- Scans all 500 Nifty stocks using 15-min data
- Applies your 44 SMA + RSI strategy
- Shows BUY / SHORT signals with one-click TradingView links
- Export results as CSV watchlist

---

## 📊 Strategy Logic

| Condition | Signal |
|-----------|--------|
| Upward trend + Green candle takes support on 44 SMA | **BUY** |
| RSI ≤ 30 (oversold) | **BUY** |
| Downward trend + Red candle takes resistance below 44 SMA | **SHORT** |
| RSI ≥ 70 (overbought) | **SHORT** |

---

## ⏰ Schedule It Daily (Optional)

**Windows Task Scheduler:**
- Create a task to run `run.bat` every evening at 4:00 PM

**Mac/Linux Cron:**
```cron
0 16 * * 1-5 cd /path/to/stock_analyzer && python app.py
```

---

## ⚠️ Disclaimer
This tool is for educational and personal analysis only.
Not financial advice. Always do your own research before trading.

---

## 📦 Data Source
- **yfinance** (Yahoo Finance) — free, no API key needed
- 15-min candle data, up to 5 days history
- Slight delay (~15 min) — fine for end-of-day analysis
