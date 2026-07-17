import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. KONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Index Radar Pro", page_icon="📈", layout="wide")
st.title(f"📈 Index Radar Pro – {datetime.now().strftime('%d.%m.%Y')}")

# Deine erweiterte Aktienliste
AKTIEN_LISTE = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BMW.DE": "BMW",
    "DTE.DE": "Deutsche Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens", "VOW3.DE": "Volkswagen",
    "RHM.DE": "Rheinmetall", "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "RWE.DE": "RWE"
}

# -----------------------------------------------------------------------------
# 2. LOGIK
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def scanne_markt():
    daten = []
    for ticker, name in AKTIEN_LISTE.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo").dropna()
            if len(df) < 130: continue
            
            akt = float(df['Close'].iloc[-1])
            vor = float(df['Close'].iloc[-2])
            change = ((akt - vor) / vor) * 100
            
            # RSL & 3-Tage Schnitt
            sma130 = df['Close'].rolling(window=130).mean().iloc[-1]
            rsl = (akt / sma130) * 100
            avg3 = df['Close'].iloc[-4:-1].mean()
            
            # Filter: +/- 2.5% Bewegung
            if -2.5 <= change <= 2.5:
                daten.append({
                    "Ticker": ticker, "Name": name, "Kurs": akt, 
                    "Delta %": change, "RSL": rsl, "3T-Schnitt": avg3
                })
        except: continue
    return pd.DataFrame(daten)

# -----------------------------------------------------------------------------
# 3. BENUTZEROBERFLÄCHE
# -----------------------------------------------------------------------------
if st.button("🚀 Profi-Analyse starten", type="primary"):
    with st.spinner("Scanne Indizes..."):
        df = scanne_markt()
        
        if not df.empty:
            # Zusammenfassung
            col1, col2 = st.columns(2)
            col1.metric("Gefundene Treffer", len(df))
            
            # Top & Flop Tabellen
            st.markdown("### 🟢 Top / 🔴 Flop (nach Delta %)")
            st.dataframe(df.sort_values("Delta %", ascending=False), use_container_width=True, hide_index=True)
            
            # Detail-Expander für jeden Treffer
            st.markdown("---")
            st.subheader("Detail-Analyse der Treffer")
            for _, row in df.iterrows():
                with st.expander(f"{row['Ticker']} - {row['Name']} ({row['Delta %']:.2f}%)"):
                    ticker_obj = yf.Ticker(row['Ticker'])
                    hist = ticker_obj.history(period="1mo")
                    
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.write(f"**Kurs:** {row['Kurs']:.2f} €")
                        st.write(f"**RSL:** {row['RSL']:.2f}")
                        st.write(f"**Sektor:** {ticker_obj.info.get('sector', 'N/A')}")
                    with c2:
                        fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'])])
                        fig.update_layout(height=150, margin=dict(l=0,r=0,t=0,b=0))
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Keine Aktien im Bereich +/- 2.5% gefunden.")
