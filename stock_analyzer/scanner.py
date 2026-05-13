import yfinance as yf
import pandas as pd
import requests
import os
import time
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_nifty_500_symbols():
    """Fetch the latest Nifty 500 symbols from NSE."""
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    try:
        # NSE requires a User-Agent header or it will block the request
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        
        # Filter: Remove any symbols that are empty or contain 'DUMMY'
        symbols = df['Symbol'].dropna().tolist()
        clean_symbols = [s.strip() for s in symbols if "DUMMY" not in str(s).upper()]
        
        return clean_symbols
    except Exception as e:
        print(f"⚠️ Error fetching Nifty 500 list: {e}")
        return ["RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY"]

def calc_sma(series, period):
    return series.rolling(window=period).mean()

def calc_rsi(series, period=14):
    """Wilder's Smoothing RSI (Matches TradingView)"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def analyze_stock(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period="5d", interval="15m")
        if df is None or len(df) < 50: return None
        df = df.dropna()

        df["SMA44"] = calc_sma(df["Close"], 44)
        df["RSI"] = calc_rsi(df["Close"], period=14)
        
        if df["RSI"].isnull().all(): return None

        last = df.iloc[-1]
        close, sma44, rsi = round(last["Close"], 2), round(last["SMA44"], 2), round(last["RSI"], 2)
        is_green = last["Close"] > last["Open"]
        is_red = last["Close"] < last["Open"]

        sma_now = df["SMA44"].iloc[-1]
        sma_prev = df["SMA44"].iloc[-6] if len(df) >= 6 else df["SMA44"].iloc[0]
        stock_trend = "UPWARD" if sma_now > sma_prev else "DOWNWARD"

        is_sma_support = last["Low"] <= (sma44 * 1.001) and last["Close"] > sma44
        is_sma_resistance = last["High"] >= (sma44 * 0.999) and last["Close"] < sma44

        signal = "NEUTRAL"
        if stock_trend == "UPWARD" and is_green and is_sma_support:
            signal = "BUY"
        elif stock_trend == "DOWNWARD" and is_red and is_sma_resistance:
            signal = "SHORT"

        if signal != "NEUTRAL":
            return {
                "Symbol": symbol,
                "Signal": signal,
                "Close": close,
                "SMA44": sma44,
                "RSI": rsi,
                "Trend": stock_trend,
                "SMA_Dist": round(((close - sma44) / sma44) * 100, 2)
            }
    except:
        return None
    return None

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    response = requests.post(url, json=payload)
    print(f"Telegram Msg Status: {response.status_code}, Response: {response.text}")

def send_telegram_file(file_path):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as f:
        response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"document": f})
        print(f"Telegram File Status: {response.status_code}, Response: {response.text}")

def main():
    print("🚀 Starting Daily Scan (Nifty 500)...")
    symbols = get_nifty_500_symbols()
    print(f"📊 Found {len(symbols)} stocks to scan.")
    
    results = []
    for i, sym in enumerate(symbols):
        if i % 10 == 0: print(f"Processing {i}/{len(symbols)}...")
        res = analyze_stock(sym)
        if res:
            results.append(res)
        time.sleep(0.3) # Rate limiting

    if not results:
        send_telegram_msg("✅ Daily Scan Complete: No signals found today.")
        return

    # Create CSV
    df_results = pd.DataFrame(results)
    file_name = f"watchlist_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df_results.to_csv(file_name, index=False)

    # Format Text Message
    msg = f"🎯 *Trade Signals Found ({datetime.now().strftime('%d %b')})*\n\n"
    for r in results:
        icon = "🟢" if r['Signal'] == "BUY" else "🔴"
        msg += f"{icon} *{r['Symbol']}* - {r['Signal']}\n"
        msg += f"   Price: ₹{r['Close']} | RSI: {r['RSI']}\n"
        msg += f"   [Chart](https://www.tradingview.com/chart/?symbol=NSE:{r['Symbol']}&interval=15)\n\n"

    send_telegram_msg(msg)
    send_telegram_file(file_name)
    print("✅ Results sent to Telegram!")

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Error: Telegram credentials not found in environment variables.")
    else:
        main()
