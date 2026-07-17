import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================================================================
# KONFIGURATION & KLASSENSTRUKTUR
# =============================================================================
st.set_page_config(page_title="Index Radar Pro Enterprise", layout="wide")

class MarketAnalyzer:
    """Klasse zur professionellen Marktanalyse und Datenaufbereitung."""
    def __init__(self):
        self.ticker_map = {
            "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer", 
            "BMW.DE": "BMW", "DTE.DE": "Deutsche Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens", 
            "VOW3.DE": "Volkswagen", "RHM.DE": "Rheinmetall", "IFX.DE": "Infineon", 
            "MBG.DE": "Mercedes-Benz", "RWE.DE": "RWE", "AIR.DE": "Airbus", 
            "CON.DE": "Continental", "ZAL.DE": "Zalando", "LHA.DE": "Lufthansa",
            "IOS.DE": "IONOS", "CBK.DE": "Commerzbank", "DBK.DE": "Deutsche Bank",
            "EOAN.DE": "E.ON", "PUM.DE": "Puma", "MTX.DE": "MTU Aero Engines"
        }
        self.results = []

    def fetch_data(self, ticker):
        """Sicheres Abrufen von Daten mit Raten-Begrenzung."""
        time.sleep(0.6)
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        return stock, df

    def calculate_metrics(self, df):
        """Berechnet technische Indikatoren mit Fehlerprüfung."""
        if len(df) < 130: return None, None
        
        current = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        change = ((current - prev) / prev) * 100
        
        sma_130 = df['Close'].rolling(window=130).mean().iloc[-1]
        rsl = (current / sma_130) * 100
        
        avg_3d = df['Close'].iloc[-4:-1].mean()
        
        return change, rsl, avg_3d

# =============================================================================
# UI-LAYOUT & LOGIK
# =============================================================================
def main():
    st.title("📈 Index Radar Pro | Enterprise Edition")
    st.markdown(f"**Datum:** {datetime.now().strftime('%d.%m.%Y')} | **System-Status:** Online")
    
    analyzer = MarketAnalyzer()
    
    with st.sidebar:
        st.header("⚙️ Filter-Einstellungen")
        min_change = st.slider("Min. Veränderung %", -5.0, 0.0, -2.5)
        max_change = st.slider("Max. Veränderung %", 0.0, 5.0, 2.5)
        show_all = st.checkbox("Alle Werte zeigen (Ignoriere Filter)", False)

    if st.button("🚀 Profi-Scan initialisieren", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (ticker, name) in enumerate(analyzer.ticker_map.items()):
            status_text.text(f"Analysiere: {name} ({ticker})...")
            try:
                stock, df = analyzer.fetch_data(ticker)
                if df.empty: continue
                
                change, rsl, avg3 = analyzer.calculate_metrics(df)
                if change is None: continue
                
                # Filter-Logik
                if not show_all and not (min_change <= change <= max_change):
                    continue
                
                # Visualisierung-Logik
                with st.expander(f"{ticker} | {name} | {change:.2f}%"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.metric("Aktueller Kurs", f"{df['Close'].iloc[-1]:.2f} €")
                        color = "green" if rsl > 110 else "red"
                        st.markdown(f"RSL-Wert: <span style='color:{color}'>{rsl:.2f}</span>", unsafe_allow_html=True)
                        st.write(f"Ø 3-Tage: {avg3:.2f} €")
                    with c2:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df.index[-60:], y=df['Close'][-60:], name="Kurs", line=dict(color='cyan')))
                        fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0))
                        st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"Fehler bei {ticker}: {e}")
            
            progress_bar.progress((i + 1) / len(analyzer.ticker_map))
        
        status_text.text("Analyse abgeschlossen.")

# =============================================================================
# ERWEITERTE FUNKTIONEN (Platzhalter für Stabilität)
# =============================================================================
def log_event(message):
    """Interne Protokollierung für Fehlerdiagnose."""
    with open("system_log.txt", "a") as f:
        f.write(f"{datetime.now()}: {message}\n")

if __name__ == "__main__":
    main()
