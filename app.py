import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- KONFIGURATION & ROBUSTHEITS-LOGIK ---
st.set_page_config(page_title="Momentum Radar Pro", layout="wide")
st.title("🚀 Momentum-Radar Pro")

# Liste der Aktien (sehr liquide Auswahl für maximale Stabilität)
TICKERS = ["AAPL", "NVDA", "AMD", "TSLA", "META", "AMZN", "PLTR", "COIN", "UNH", "SAP.DE", "RHM.DE"]

def get_data(ticker):
    """Holt Daten mit Fehlerbehandlung, damit die App stabil bleibt."""
    try:
        # Lade die letzten 30 Tage, um RVOL sauber zu berechnen
        stock = yf.Ticker(ticker)
        hist = stock.history(period="30d")
        if len(hist) < 20: return None
        
        # Heutige Daten
        today = hist.iloc[-1]
        hist_20d = hist.iloc[-21:-1]
        avg_vol = hist_20d['Volume'].mean()
        
        # Berechnung der Metriken
        rvol = today['Volume'] / avg_vol if avg_vol > 0 else 0
        price_change_pct = ((today['Close'] - today['Open']) / today['Open']) * 100
        momentum_score = today['Volume'] * ((today['Close'] - today['Open']) / today['Open'])
        spanne = ((today['High'] - today['Low']) / today['Low']) * 100
        
        return {
            "Symbol": ticker,
            "Kurs": round(today['Close'], 2),
            "Änderung %": round(price_change_pct, 2),
            "RVOL": round(rvol, 2),
            "Volumen": int(today['Volume']),
            "Momentum Score": int(momentum_score),
            "Spanne %": round(spanne, 2)
        }
    except Exception:
        return None

# --- UI & LOGIK ---
if st.button("📈 Scan starten"):
    results = []
    progress_bar = st.progress(0)
    for i, ticker in enumerate(TICKERS):
        data = get_data(ticker)
        if data and data['Änderung %'] > 0 and data['RVOL'] >= 1.0: # Filter hier anpassbar
            results.append(data)
        progress_bar.progress((i + 1) / len(TICKERS))
    
    if results:
        df = pd.DataFrame(results).sort_values("Momentum Score", ascending=False)
        st.table(df)
    else:
        st.info("Keine Aktien gefunden, die heute deine Kriterien erfüllen.")

