import streamlit as st
import ccxt
import pandas as pd
import ta
import plotly.graph_objects as go
from datetime import datetime
import time

st.set_page_config(page_title="AI Trading Guide", page_icon="📈", layout="wide")

st.title("🤖 AI Trading Guide - Binance Futures")
st.markdown("**BTCUSDT & XAUUSDT** | Real-time Signals")

# Sidebar
st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Asset", ["BTCUSDT", "XAUUSDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "4h"])

# Exchange
exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'future'}})

@st.cache_data(ttl=30)
def get_data(symbol, tf):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=200)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        return df
    except:
        return None

df = get_data(symbol, timeframe)

if df is None or len(df) < 50:
    st.error("Data nahi mil paaya")
    st.stop()

# Indicators using 'ta' library
df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
df['ema21'] = ta.trend.ema_indicator(df['close'], window=21)
df['rsi'] = ta.momentum.rsi(df['close'], window=14)

# Simple Signal
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

# Display
st.subheader(f"Current Price: ${latest['close']:.2f}")

if signal == "BUY":
    st.success(f"🟢 BUY Signal | Confidence: {confidence}%")
elif signal == "SELL":
    st.error(f"🔴 SELL Signal | Confidence: {confidence}%")
else:
    st.warning(f"🟡 HOLD | No strong signal")

# Chart
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close']))
fig.add_trace(go.Scatter(x=df['time'], y=df['ema9'], name="EMA9"))

cd ~/trading-app && cat > trading_guide.py << 'EOF'
import streamlit as st
import ccxt
import pandas as pd
import ta
import plotly.graph_objects as go

st.set_page_config(page_title="AI Trading Guide", page_icon="📈", layout="wide")

st.title("🤖 AI Trading Guide - Binance Futures")

st.sidebar.header("Settings")
symbol = st.sidebar.selectbox("Asset", ["BTCUSDT", "XAUUSDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["5m", "15m", "30m", "1h", "4h"])

exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'future'}})

@st.cache_data(ttl=30)
def get_data(symbol, tf):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=200)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        return df
    except:
        return None

df = get_data(symbol, timeframe)

if df is None or len(df) < 50:
    st.error("Data nahi mil paaya")
    st.stop()

df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
df['ema21'] = ta.trend.ema_indicator(df['close'], window=21)

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

fig = go.Figure()
fig.add_trace(go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close']))
fig.add_trace(go.Scatter(x=df['time'], y=df['ema9'], name="EMA9"))
fig.add_trace(go.Scatter(x=df['time'], y=df['ema21'], name="EMA21"))
fig.update_layout(height=500, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

st.caption("Binance Futures | Educational Use Only")
