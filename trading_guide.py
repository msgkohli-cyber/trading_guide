import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="AI Trading Guide", page_icon="📈", layout="wide")

st.title("🤖 AI Trading Guide - Binance Futures")
st.markdown("**BTCUSDT & XAUUSDT Perpetual** | Live Signals")

st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Asset", ["BTCUSDT", "XAUUSDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "4h"])

@st.cache_data(ttl=60)
def fetch_futures_data(symbol, interval, limit=120):
    # Futures API endpoint
    url = "https://fapi.binance.com/fapi/v1/klines"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    
    for attempt in range(6):  # 6 retries
        try:
            response = requests.get(url, params=params, headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 30:
                    df = pd.DataFrame(data, columns=[
                        'open_time', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_asset_volume', 'number_of_trades',
                        'taker_buy_base', 'taker_buy_quote', 'ignore'
                    ])
                    df['time'] = pd.to_datetime(df['open_time'], unit='ms')
                    df['close'] = pd.to_numeric(df['close'])
                    df['open'] = pd.to_numeric(df['open'])
                    df['high'] = pd.to_numeric(df['high'])
                    df['low'] = pd.to_numeric(df['low'])
                    return df[['time', 'open', 'high', 'low', 'close', 'volume']]
            
            time.sleep(3)
            
        except Exception as e:
            time.sleep(3)
            continue
    
    return None

df = fetch_futures_data(symbol, timeframe)

if df is None or len(df) < 30:
    st.error("Binance Futures se data nahi mil paaya. Thodi der baad try karo ya timeframe change karo.")
    st.stop()

# EMA
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

st.caption("Data Source: Binance Futures API | Educational Purpose Only")
