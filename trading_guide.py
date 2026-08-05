import streamlit as st
import ccxt
import pandas as pd
import time

st.set_page_config(page_title="AI Trading Guide", page_icon="📈", layout="wide")

st.title("🤖 AI Trading Guide - Binance Futures")
st.markdown("**BTCUSDT & XAUUSDT** | Real-time Signals")

st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Asset", ["BTCUSDT", "XAUUSDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "4h"])

@st.cache_data(ttl=45)
def get_binance_data(symbol, tf, limit=150):
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        # Retry 2 times
        for attempt in range(3):
            try:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
                if ohlcv and len(ohlcv) > 30:
                    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
                    df['time'] = pd.to_datetime(df['time'], unit='ms')
                    return df
                time.sleep(1)
            except Exception as e:
                if attempt == 2:
                    return None
                time.sleep(2)
        return None
    except:
        return None

df = get_binance_data(symbol, timeframe)

if df is None or len(df) < 30:
    st.error("Binance se data nahi mil paaya. Thodi der baad try karo ya timeframe change karo.")
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

st.caption("Data Source: Binance Futures | Educational Purpose Only")
