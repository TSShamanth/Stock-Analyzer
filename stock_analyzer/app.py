"""
Nifty 500 Stock Screener - Backend
Strategy: 44 SMA + RSI on 15-min charts
Author: Built for personal trading use
"""

from flask import Flask, jsonify, send_from_directory, request
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import json
import os
import threading
import time
from datetime import datetime

app = Flask(__name__, static_folder="ui")

# ─────────────────────────────────────────────
# NIFTY 500 Stock Symbols (NSE)
# ─────────────────────────────────────────────
NIFTY_500 = ['360ONE', '3MINDIA', 'ABB', 'ACC', 'ACMESOLAR', 'AIAENG', 'APLAPOLLO', 'AUBANK', 'AWL', 'AADHARHFC', 'AARTIIND', 'AAVAS', 'ABBOTINDIA', 'ACE', 'ACUTAAS', 'ADANIENSOL', 'ADANIENT', 'ADANIGREEN', 'ADANIPORTS', 'ADANIPOWER', 'ATGL', 'ABCAPITAL', 'ABFRL', 'ABLBL', 'ABREL', 'ABSLAMC', 'CPPLUS', 'AEGISLOG', 'AEGISVOPAK', 'AFCONS', 'AFFLE', 'AJANTPHARM', 'ALKEM', 'ABDL', 'ARE&M', 'AMBER', 'AMBUJACEM', 'ANANDRATHI', 'ANANTRAJ', 'ANGELONE', 'ANTHEM', 'ANURAS', 'APARINDS', 'APOLLOHOSP', 'APOLLOTYRE', 'APTUS', 'ASAHIINDIA', 'ASHOKLEY', 'ASIANPAINT', 'ASTERDM', 'ASTRAL', 'ATHERENERG', 'ATUL', 'AUROPHARMA', 'AIIL', 'DMART', 'AXISBANK', 'BEML', 'BLS', 'BSE', 'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BAJAJHLDNG', 'BAJAJHFL', 'BALKRISIND', 'BALRAMCHIN', 'BANDHANBNK', 'BANKBARODA', 'BANKINDIA', 'MAHABANK', 'BATAINDIA', 'BAYERCROP', 'BELRISE', 'BERGEPAINT', 'BDL', 'BEL', 'BHARATFORG', 'BHEL', 'BPCL', 'BHARTIARTL', 'BHARTIHEXA', 'BIKAJI', 'GROWW', 'BIOCON', 'BSOFT', 'BLUEDART', 'BLUEJET', 'BLUESTARCO', 'BBTC', 'BOSCHLTD', 'FIRSTCRY', 'BRIGADE', 'BRITANNIA', 'MAPMYINDIA', 'CCL', 'CESC', 'CGPOWER', 'CIEINDIA', 'CRISIL', 'CANFINHOME', 'CANBK', 'CANHLIFE', 'CAPLIPOINT', 'CGCL', 'CARBORUNIV', 'CARTRADE', 'CASTROLIND', 'CEATLTD', 'CEMPRO', 'CENTRALBK', 'CDSL', 'CHALET', 'CHAMBLFERT', 'CHENNPETRO', 'CHOICEIN', 'CHOLAHLDNG', 'CHOLAFIN', 'CIPLA', 'CUB', 'CLEAN', 'COALINDIA', 'COCHINSHIP', 'COFORGE', 'COHANCE', 'COLPAL', 'CAMS', 'CONCORDBIO', 'CONCOR', 'COROMANDEL', 'CRAFTSMAN', 'CREDITACC', 'CROMPTON', 'CUMMINSIND', 'CYIENT', 'DCMSHRIRAM', 'DLF', 'DOMS', 'DABUR', 'DALBHARAT', 'DATAPATTNS', 'DEEPAKFERT', 'DEEPAKNTR', 'DELHIVERY', 'DEVYANI', 'DIVISLAB', 'DIXON', 'LALPATHLAB', 'DRREDDY', 'EIDPARRY', 'EIHOTEL', 'EICHERMOT', 'ELECON', 'ELGIEQUIP', 'EMAMILTD', 'EMCURE', 'EMMVEE', 'ENDURANCE', 'ENGINERSIN', 'ERIS', 'ESCORTS', 'ETERNAL', 'EXIDEIND', 'NYKAA', 'FEDERALBNK', 'FACT', 'FINCABLES', 'FSL', 'FIVESTAR', 'FORCEMOT', 'FORTIS', 'GAIL', 'GVT&D', 'GMRAIRPORT', 'GABRIEL', 'GALLANTT', 'GRSE', 'GICRE', 'GILLETTE', 'GLAND', 'GLAXO', 'GLENMARK', 'MEDANTA', 'GODIGIT', 'GPIL', 'GODFRYPHLP', 'GODREJCP', 'GODREJIND', 'GODREJPROP', 'GRANULES', 'GRAPHITE', 'GRASIM', 'GRAVITA', 'GESHIP', 'FLUOROCHEM', 'GMDCLTD', 'HEG', 'HBLENGINE', 'HCLTECH', 'HDBFS', 'HDFCAMC', 'HDFCBANK', 'HDFCLIFE', 'HFCL', 'HAVELLS', 'HEROMOTOCO', 'HEXT', 'HSCL', 'HINDALCO', 'HAL', 'HINDCOPPER', 'HINDPETRO', 'HINDUNILVR', 'HINDZINC', 'POWERINDIA', 'HOMEFIRST', 'HONASA', 'HONAUT', 'HUDCO', 'HYUNDAI', 'ICICIBANK', 'ICICIGI', 'ICICIAMC', 'ICICIPRULI', 'IDBI', 'IDFCFIRSTB', 'IFCI', 'IIFL', 'IRB', 'IRCON', 'ITCHOTELS', 'ITC', 'ITI', 'INDGN', 'INDIACEM', 'INDIAMART', 'INDIANB', 'IEX', 'INDHOTEL', 'IOC', 'IOB', 'IRCTC', 'IRFC', 'IREDA', 'IGL', 'INDUSTOWER', 'INDUSINDBK', 'NAUKRI', 'INFY', 'INOXWIND', 'INTELLECT', 'INDIGO', 'IGIL', 'IKS', 'IPCALAB', 'JBCHEPHARM', 'JKCEMENT', 'JBMA', 'JKTYRE', 'JMFINANCIL', 'JSWCEMENT', 'JSWDULUX', 'JSWENERGY', 'JSWINFRA', 'JSWSTEEL', 'JAINREC', 'JPPOWER', 'J&KBANK', 'JINDALSAW', 'JSL', 'JINDALSTEL', 'JIOFIN', 'JUBLFOOD', 'JUBLINGREA', 'JUBLPHARMA', 'JWL', 'JYOTICNC', 'KPRMILL', 'KEI', 'KPITTECH', 'KAJARIACER', 'KPIL', 'KALYANKJIL', 'KARURVYSYA', 'KAYNES', 'KEC', 'KFINTECH', 'KIRLOSENG', 'KOTAKBANK', 'KIMS', 'LTF', 'LTTS', 'LGEINDIA', 'LICHSGFIN', 'LTFOODS', 'LTM', 'LT', 'LATENTVIEW', 'LAURUSLABS', 'THELEELA', 'LEMONTREE', 'LENSKART', 'LICI', 'LINDEINDIA', 'LLOYDSME', 'LODHA', 'LUPIN', 'MMTC', 'MRF', 'MGL', 'M&MFIN', 'M&M', 'MANAPPURAM', 'MRPL', 'MANKIND', 'MARICO', 'MARUTI', 'MFSL', 'MAXHEALTH', 'MAZDOCK', 'MEESHO', 'MINDACORP', 'MSUMI', 'MOTILALOFS', 'MPHASIS', 'MCX', 'MUTHOOTFIN', 'NATCOPHARM', 'NBCC', 'NCC', 'NHPC', 'NLCINDIA', 'NMDC', 'NSLNISP', 'NTPCGREEN', 'NTPC', 'NH', 'NATIONALUM', 'NAVA', 'NAVINFLUOR', 'NESTLEIND', 'NETWEB', 'NEULANDLAB', 'NEWGEN', 'NAM-INDIA', 'NIVABUPA', 'NUVAMA', 'NUVOCO', 'OBEROIRLTY', 'ONGC', 'OIL', 'OLAELEC', 'OLECTRA', 'PAYTM', 'ONESOURCE', 'OFSS', 'POLICYBZR', 'PCBL', 'PGEL', 'PIIND', 'PNBHOUSING', 'PTCIL', 'PVRINOX', 'PAGEIND', 'PARADEEP', 'PATANJALI', 'PERSISTENT', 'PETRONET', 'PFIZER', 'PHOENIXLTD', 'PWL', 'PIDILITIND', 'PINELABS', 'PIRAMALFIN', 'PPLPHARMA', 'POLYMED', 'POLYCAB', 'POONAWALLA', 'PFC', 'POWERGRID', 'PREMIERENE', 'PRESTIGE', 'PNB', 'RRKABEL', 'RBLBANK', 'RECLTD', 'RHIM', 'RITES', 'RADICO', 'RVNL', 'RAILTEL', 'RAINBOW', 'RKFORGE', 'REDINGTON', 'RELIANCE', 'RPOWER', 'SBFC', 'SBICARD', 'SBILIFE', 'SJVN', 'SRF', 'SAGILITY', 'SAILIFE', 'SAMMAANCAP', 'MOTHERSON', 'SAPPHIRE', 'SARDAEN', 'SAREGAMA', 'SCHAEFFLER', 'SCHNEIDER', 'SCI', 'SHREECEM', 'SHRIRAMFIN', 'SHYAMMETL', 'ENRIN', 'SIEMENS', 'SIGNATURE', 'SOBHA', 'SOLARINDS', 'SONACOMS', 'SONATSOFTW', 'STARHEALTH', 'SBIN', 'SAIL', 'SUMICHEM', 'SUNPHARMA', 'SUNTV', 'SUNDARMFIN', 'SUPREMEIND', 'SPLPETRO', 'SUZLON', 'SWANCORP', 'SWIGGY', 'SYNGENE', 'SYRMA', 'TBOTEK', 'TVSMOTOR', 'TATACAP', 'TATACHEM', 'TATACOMM', 'TCS', 'TATACONSUM', 'TATAELXSI', 'TATAINVEST', 'TMCV', 'TMPV', 'TATAPOWER', 'TATASTEEL', 'TATATECH', 'TTML', 'TECHM', 'TECHNOE', 'TEGA', 'TEJASNET', 'TENNIND', 'NIACL', 'RAMCOCEM', 'THERMAX', 'TIMKEN', 'TITAGARH', 'TITAN', 'TORNTPHARM', 'TORNTPOWER', 'TARIL', 'TRAVELFOOD', 'TRENT', 'TRIDENT', 'TRITURBINE', 'TIINDIA', 'UCOBANK', 'UNOMINDA', 'UPL', 'UTIAMC', 'ULTRACEMCO', 'UNIONBANK', 'UBL', 'UNITDSPR', 'URBANCO', 'USHAMART', 'VTL', 'VBL', 'VEDL', 'VIJAYA', 'VMM', 'IDEA', 'VOLTAS', 'WAAREEENER', 'WELCORP', 'WELSPUNLIV', 'WHIRLPOOL', 'WIPRO', 'WOCKPHARMA', 'YESBANK', 'ZFCVINDIA', 'ZEEL', 'ZENTEC', 'ZENSARTECH', 'ZYDUSLIFE', 'ZYDUSWELL', 'ECLERX']

# ─────────────────────────────────────────────
# Global state
# ─────────────────────────────────────────────
scan_state = {
    "running": False,
    "progress": 0,
    "total": 0,
    "current_stock": "",
    "results": [],
    "last_scan": None,
    "errors": []
}

def calc_sma(series, period):
    return series.rolling(window=period).mean()

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = -delta.clip(upper=0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_stock(symbol):
    """Fetch 15-min data and apply strategy for one stock."""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period="5d", interval="15m")

        if df is None or len(df) < 50:
            return None

        df = df.dropna()
        df["SMA44"] = calc_sma(df["Close"], 44)
        
        # Using pandas_ta for Wilder's Smoothing RSI (Matches TradingView)
        df["RSI"] = ta.rsi(df["Close"], length=14)

        if df["RSI"].isnull().all():
            return None

        # Latest candle
        last = df.iloc[-1]
        
        close = round(last["Close"], 2)
        sma44 = round(last["SMA44"], 2)
        rsi   = round(last["RSI"], 2)

        is_green = last["Close"] > last["Open"]
        is_red   = last["Close"] < last["Open"]

        # Trend: Check slope of SMA (current vs 5 candles ago)
        sma_now = df["SMA44"].iloc[-1]
        sma_prev = df["SMA44"].iloc[-6] if len(df) >= 6 else df["SMA44"].iloc[0]
        stock_trend = "UPWARD" if sma_now > sma_prev else "DOWNWARD"

        # ── Strategy Logic (Simplified) ──────────
        signal = "NEUTRAL"
        reasons = []

        # SMA Interaction (Wick touch + Close recovery)
        # BUY: Low touches/crosses SMA, Close stays above
        is_sma_support = last["Low"] <= (sma44 * 1.001) and last["Close"] > sma44
        # SHORT: High touches/crosses SMA, Close stays below
        is_sma_resistance = last["High"] >= (sma44 * 0.999) and last["Close"] < sma44

        # BUY conditions: Stock Trend Up + Green Candle + SMA Support
        if (stock_trend == "UPWARD" and 
            is_green and 
            is_sma_support): 
            
            signal = "BUY"
            reasons.append("Stock Trend UP + Green Candle + SMA Support")

        # SHORT conditions: Stock Trend Down + Red Candle + SMA Resistance
        elif (stock_trend == "DOWNWARD" and 
              is_red and 
              is_sma_resistance):
            
            signal = "SHORT"
            reasons.append("Stock Trend DOWN + Red Candle + SMA Resistance")

        # Distance from SMA
        sma_dist_pct = round(((close - sma44) / sma44) * 100, 2)

        return {
            "symbol": symbol,
            "close": close,
            "sma44": sma44,
            "rsi": round(rsi, 1),
            "trend": stock_trend,
            "candle": "GREEN" if is_green else ("RED" if is_red else "DOJI"),
            "signal": signal,
            "reasons": reasons,
            "sma_dist_pct": sma_dist_pct,
            "volume": int(last["Volume"]),
        }

    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def run_scan(symbols):
    """Run full scan in background thread."""
    global scan_state
    scan_state["running"] = True
    scan_state["progress"] = 0
    scan_state["total"] = len(symbols)
    scan_state["results"] = []
    scan_state["errors"] = []

    results = []

    for i, sym in enumerate(symbols):
        scan_state["current_stock"] = sym
        scan_state["progress"] = i + 1

        res = analyze_stock(sym)
        if res:
            if "error" in res:
                scan_state["errors"].append(res)
            elif res["signal"] in ("BUY", "SHORT"):
                results.append(res)

        time.sleep(0.3)  # polite rate limiting
        if res:
            if "error" in res:
                scan_state["errors"].append(res)
            elif res["signal"] in ("BUY", "SHORT"):
                results.append(res)

        time.sleep(0.3)  # polite rate limiting

    # Sort: BUY first, then SHORT, by RSI distance from extremes
    results.sort(key=lambda x: (
        0 if x["signal"] == "BUY" else 1,
        x["rsi"] if x["signal"] == "BUY" else -x["rsi"]
    ))

    scan_state["results"] = results
    scan_state["running"] = False
    scan_state["last_scan"] = datetime.now().strftime("%d %b %Y, %I:%M %p")


# ─────────────────────────────────────────────
# API Routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("ui", "index.html")

@app.route("/api/scan/start", methods=["POST"])
def start_scan():
    if scan_state["running"]:
        return jsonify({"error": "Scan already running"}), 400

    data = request.get_json(silent=True) or {}
    custom = data.get("symbols", [])
    symbols = custom if custom else NIFTY_500

    thread = threading.Thread(target=run_scan, args=(symbols,), daemon=True)
    thread.start()
    return jsonify({"status": "started", "total": len(symbols)})

@app.route("/api/scan/status")
def scan_status():
    return jsonify(scan_state)

@app.route("/api/scan/results")
def scan_results():
    return jsonify({
        "results": scan_state["results"],
        "last_scan": scan_state["last_scan"],
        "total_signals": len(scan_state["results"])
    })

@app.route("/api/export/csv")
def export_csv():
    from flask import Response
    results = scan_state["results"]
    if not results:
        return jsonify({"error": "No results"}), 400

    rows = ["Symbol,Signal,Close,44SMA,RSI,Trend,Candle,SMA Distance %,Reason"]
    for r in results:
        reason_str = " | ".join(r.get("reasons", []))
        rows.append(
            f"{r['symbol']},{r['signal']},{r['close']},{r['sma44']},{r['rsi']},"
            f"{r['trend']},{r['candle']},{r['sma_dist_pct']}%,\"{reason_str}\""
        )

    csv_content = "\n".join(rows)
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=watchlist.csv"}
    )

@app.route("/api/stocks/list")
def stocks_list():
    return jsonify(NIFTY_500)

@app.route("/api/ticker")
def get_ticker_data():
    """Fetch real-time data for the top 15 stocks for the UI ticker."""
    major_symbols = [
        "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "BHARTIARTL", 
        "SBIN", "INFY", "LICI", "HINDUNILVR", "ITC", 
        "BAJFINANCE", "LT", "HCLTECH", "MARUTI", "SUNPHARMA"
    ]
    ticker_data = []
    try:
        # Fetching multiple at once is faster
        symbols_ns = [f"{s}.NS" for s in major_symbols]
        data = yf.download(symbols_ns, period="1d", interval="1m", group_by='ticker', progress=False)
        
        for sym in major_symbols:
            sym_ns = f"{sym}.NS"
            if sym_ns in data.columns.levels[0]:
                df = data[sym_ns].dropna()
                if not df.empty:
                    last_close = df["Close"].iloc[-1]
                    prev_close = df["Open"].iloc[0] # Using day open for change
                    change_pct = ((last_close - prev_close) / prev_close) * 100
                    
                    ticker_data.append([
                        sym,
                        f"{last_close:,.2f}",
                        f"{change_pct:+.2f}%",
                        "up" if change_pct >= 0 else "down"
                    ])
        return jsonify(ticker_data)
    except Exception as e:
        return jsonify([]) # Return empty on error to prevent UI crash

if __name__ == "__main__":
    os.makedirs("ui", exist_ok=True)
    print("🚀 Stock Screener running at http://localhost:5000")
    app.run(debug=False, port=5000)
