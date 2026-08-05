import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="AI Trading Guide", page_icon="📈", layout="wide")

st.title("🤖 AI Trading Guide - Binance")
st.markdown("**BTCUSDT & XAUUSDT** | Live Signals")

st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Asset", ["BTCUSDT", "XAUUSDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "4h"])

@st.cache_data(ttl=60)
def get_binance_data(symbol, interval, limit=120):
    url = "https://api.binance.com/api/v3/klines"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    for attempt in range(5):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 30:
                    df = pd.DataFrame(data, columns=[
                        'open_time', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base', 'taker_buy_quote', 'ignore'
                    ])
                    df['time'] = pd.to_datetime(df['open_time'], unit='ms')
                    df['close'] = pd.to_numeric(df['close'])
                    return df[['time', 'open', 'high', 'low', 'close', 'volume']]
            time.sleep(2)
        except:
            time.sleep(2)
            continue
    return None

df = get_binance_data(symbol, timeframe)

if df is None or len(df) < 30:
    st.error("Binance se data nahi mil paaya. Thodi der baad try karo ya timeframe change karo.")
    st.stop()

df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()

latest = df.iloc[-1]
prev = df.iloc[-2]

signal = "HOLD"
confidence = 50

if latest['ema9'] > latest['ema21'] and prev['ema9'] <= prev['ema21']:
    signal = "BUY"
    confidence = 75
elif latest['ema9'] < latest['ema21'] and prev['ema9'] >= prev['ema21']:
    signal = "SELL"
    confidence = 75

st.subheader(f"Current Price: ${latest['close']:.2f}")

if signal == "BUY":
    st.success(f"🟢 BUY Signal | Confidence: {confidence}%")
elif signal == "SELL":
    st.error(f"🔴 SELL Signal | Confidence: {confidence}%")
else:
    st.warning("🟡 HOLD")

st.subheader("Price & EMA Chart")
st.line_chart(df.set_index('time')[['close', 'ema9', 'ema21']])

st.caption("Data Source: Binance | Educational Purpose Only")
