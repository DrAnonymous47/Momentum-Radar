import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Momentum Radar Pro", layout="wide")
st.title("🚀 Momentum-Radar Pro")

# Ionos wurde hier als IOS.DE hinzugefügt
TICKERS = ["AAPL", "NVDA", "AMD", "TSLA", "META", "AMZN", "PLTR", "COIN", "UNH", "SAP.DE", "RHM.DE", "IOS.DE"]

def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="30d")
        if len(hist) < 20: return None
        today = hist.iloc[-1]
        hist_20d = hist.iloc[-21:-1]
        avg_vol = hist_20d['Volume'].mean()
        rvol = today['Volume'] / avg_vol if avg_vol > 0 else 0
        price_change_pct = ((today['Close'] - today['Open']) / today['Open']) * 100
        momentum_score = today['Volume'] * ((today['Close'] - today['Open']) / today['Open'])
        return {"Symbol": ticker, "Kurs": round(today['Close'], 2), "Änderung %": round(price_change_pct, 2), "RVOL": round(rvol, 2), "Momentum Score": int(momentum_score)}
    except Exception:
        return None

if st.button("📈 Scan starten"):
    results = []
    for ticker in TICKERS:
        data = get_data(ticker)
        if data and data['Änderung %'] > 0 and data['RVOL'] >= 1.0:
            results.append(data)
    if results:
        df = pd.DataFrame(results).sort_values("Momentum Score", ascending=False)
        st.table(df)
    else:
        st.info("Keine passenden Aktien gefunden.")
