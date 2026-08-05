streamlit
ccxt
pandas
pandas_ta
plotly
requests

import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time
import requests

# Page config
st.set_page_config(
    page_title="🤖 AI Trading Guide - BTC & Gold",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #00ff88; text-align: center; }
    .signal-box { padding: 1.5rem; border-radius: 15px; text-align: center; font-size: 1.8rem; font-weight: bold; margin: 1rem 0; }
    .buy { background-color: #00c853; color: white; }
    .sell { background-color: #ff1744; color: white; }
    .hold { background-color: #ff9100; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🤖 AI Trading Guide</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#888;">Binance USDT Perpetual Futures • Smart Signals</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Settings")
asset = st.sidebar.selectbox("📊 Asset", ["BTCUSDT", "XAUUSDT"], index=0)
timeframe = st.sidebar.selectbox("⏱️ Timeframe", ["5m", "15m", "30m", "1h", "4h", "1d"], index=2)
refresh_rate = st.sidebar.slider("🔄 Auto Refresh (sec)", 15, 120, 45)

st.sidebar.markdown("---")
st.sidebar.subheader("📱 Telegram Alerts")
enable_telegram = st.sidebar.checkbox("Enable Telegram Alerts", value=False)
if enable_telegram:
    bot_token = st.sidebar.text_input("Bot Token", type="password")
    chat_id = st.sidebar.text_input("Chat ID")

st.sidebar.markdown("---")
st.sidebar.info("Binance Futures Data • Educational Purpose Only")

# Exchange
@st.cache_resource
def get_exchange():
    return ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'future'}})

exchange = get_exchange()

@st.cache_data(ttl=refresh_rate)
def fetch_data(symbol, timeframe, limit=200):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        if not ohlcv: return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        return None

def calculate_indicators(df):
    df = df.copy()
    df['EMA9'] = ta.ema(df['Close'], length=9)
    df['EMA21'] = ta.ema(df['Close'], length=21)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    if macd is not None:
        df = pd.concat([df, macd], axis=1)
    bb = ta.bbands(df['Close'], length=20)
    if bb is not None:
        df = pd.concat([df, bb], axis=1)
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    return df

def generate_signal(df):
    if df is None or len(df) < 30:
        return "HOLD", 50, "Insufficient data", None
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    score = 0
    reasons = []
    
    # EMA
    if latest['EMA9'] > latest['EMA21'] and prev['EMA9'] <= prev['EMA21']:
        score += 35
        reasons.append("✅ EMA Golden Cross")
    elif latest['EMA9'] < latest['EMA21'] and prev['EMA9'] >= prev['EMA21']:
        score -= 35
        reasons.append("❌ EMA Death Cross")
    elif latest['EMA9'] > latest['EMA21']:
        score += 15
        reasons.append("📈 Bullish EMA")
    else:
        score -= 15
        reasons.append("📉 Bearish EMA")
    
    # RSI
    if pd.notna(latest['RSI']):
        if latest['RSI'] < 30:
            score += 25
            reasons.append(f"✅ RSI Oversold ({latest['RSI']:.1f})")
        elif latest['RSI'] > 70:
            score -= 25
            reasons.append(f"❌ RSI Overbought ({latest['RSI']:.1f})")
    
    # MACD
    if 'MACD_12_26_9' in latest and pd.notna(latest['MACD_12_26_9']):
        if latest['MACD_12_26_9'] > latest.get('MACDs_12_26_9', 0):
            score += 15
            reasons.append("✅ MACD Bullish")
        else:
            score -= 15
            reasons.append("❌ MACD Bearish")
    
    if score >= 30:
        signal = "BUY"
        confidence = min(95, max(55, int(score * 0.9)))
    elif score <= -30:
        signal = "SELL"
        confidence = min(95, max(55, int(abs(score) * 0.9)))
    else:
        signal = "HOLD"
        confidence = 50 + abs(score)
    
    reason_text = " • ".join(reasons)
    
    # Trade Plan
    trade_plan = None
    if signal in ["BUY", "SELL"]:
        entry = round(latest['Close'], 2)
        atr = latest.get('ATR', entry * 0.015)
        if signal == "BUY":
            sl = round(entry - (atr * 1.5), 2)
            tp = round(entry + (atr * 3), 2)
            rr = round((tp - entry) / (entry - sl), 2) if (entry - sl) > 0 else 0
            trade_plan = {"action": "LONG", "entry": entry, "stop_loss": sl, "take_profit": tp, "rr": f"1:{rr}"}
        else:
            sl = round(entry + (atr * 1.5), 2)
            tp = round(entry - (atr * 3), 2)
            rr = round((entry - tp) / (sl - entry), 2) if (sl - entry) > 0 else 0
            trade_plan = {"action": "SHORT", "entry": entry, "stop_loss": sl, "take_profit": tp, "rr": f"1:{rr}"}
    
    return signal, confidence, reason_text, trade_plan

# Main
df = fetch_data(asset, timeframe)
if df is None or df.empty:
    st.error("Data nahi mil paaya. Thodi der baad try karo.")
    st.stop()

df = calculate_indicators(df)
signal, confidence,

