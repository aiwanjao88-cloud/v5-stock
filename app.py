import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. 介面設定
st.set_page_config(page_title="V5 專業波段後台", layout="wide")
st.title("🛡️ V5 國發級波段交易系統")

# 2. 側邊選單
st.sidebar.header("🔍 選股設定")
stock_no = st.sidebar.text_input("輸入台股代碼", "2330")
stock_id = f"{stock_no}.TW"

# 3. 數據抓取
try:
    df = yf.download(stock_id, start=(datetime.now() - timedelta(days=365)))
    
    # 指標計算
    df['MA100'] = ta.sma(df['Close'], length=100) # 週20MA
    df['VMA20'] = ta.sma(df['Volume'], length=20) # 20日均量
    df['High60'] = df['High'].rolling(window=60).max() # 60日高點
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=14) # 波動度
    
    now = df.iloc[-1]
    prev = df.iloc[-2]

    # 4. 判定邏輯 (Level 1 & 2)
    c1 = now['Close'] > now['MA100']             # 站上週線
    c2 = (now['MA100'] - df.iloc[-5]['MA100']) > 0 # 趨勢向上
    c3 = now['Close'] >= prev['High60']         # 突破高點
    c4 = now['Volume'] > now['VMA20'] * 1.5      # 成交量放大
    
    score = sum([c1, c2, c3, c4]) * 25

    # 5. 數據面板
    col1, col2, col3 = st.columns(3)
    col1.metric("目前價格", f"{now['Close']:.1f}")
    col2.metric("系統評分", f"{int(score)} 分")
    col3.metric("趨勢狀態", "🔥 強力噴發" if score >= 75 else "⚖️ 盤整觀察")

    # 6. 專業交易計畫
    st.divider()
    if score >= 75:
        st.success("✅ **符合進場訊號：主升段啟動中**")
        p1, p2, p3 = st.columns(3)
        p1.info(f"📍 **建議進場位**\n\n約在 {now['Close']:.1f} 附近")
        p2.warning(f"🛑 **ATR 風控止損**\n\n嚴守 {now['Close'] - 1.5*now['ATR']:.1f}")
        p3.success(f"🎯 **波段目標價**\n\n第一階段 {now['Close'] + 3*now['ATR']:.1f}")
    else:
        st.error("❌ **目前訊號不足：建議觀望，不要追高**")

    # 7. 視覺化 K 線圖
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="K線")])
    fig.add_trace(go.Scatter(x=df.index, y=df['MA100'], line=dict(color='orange', width=2), name="週20MA趨勢線"))
    fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("💡 請在左側輸入正確的台股代碼 (例如: 2330, 2454, 2317)")
