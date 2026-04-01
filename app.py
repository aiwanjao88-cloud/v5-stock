import streamlit as st
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="V5 波段後台")
st.title("🛡️ V5 國發級波段後台")

stock_no = st.sidebar.text_input("輸入台股代碼", "2330")
df = yf.download(f"{stock_no}.TW", period="1y")

# 核心邏輯
df['MA100'] = ta.sma(df['Close'], length=100)
df['High60'] = df['High'].rolling(window=60).max()
now = df.iloc[-1]
score = sum([now['Close'] > now['MA100'], now['Close'] >= df.iloc[-2]['High60']]) * 50

st.metric("當前股價", f"{now['Close']:.1f}")
st.metric("系統評分", f"{int(score)} 分")

if score >= 100:
    st.success("🎯 符合狙擊條件！")
else:
    st.error("📉 訊號不足，觀望。")
