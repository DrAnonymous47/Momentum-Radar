import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. Konfiguration
st.set_page_config(page_title="Index Radar Pro", layout="wide")
st.title(f"📈 Index Radar Pro – Stand: {datetime.now().strftime('%d.%m.%Y')}")

# 2. Ticker Liste
TICKER_MAP = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BMW.DE": "BMW",
    "DTE.DE": "Deutsche Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens", "VOW3.DE": "Volkswagen",
    "RHM.DE": "Rheinmetall", "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "RWE.DE": "RWE"
}

# 3. Logik
def lade_daten():
    daten = []
    for ticker, name in TICKER_MAP.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="7mo").dropna()
            if len(df) < 130: continue
            
            akt = float(df['Close'].iloc[-1])
            vor = float(df['Close'].iloc[-2])
            change = ((akt - vor) / vor) * 100
            
            # RSL Berechnung
            sma130 = df['Close'].rolling(window=130).mean().iloc[-1]
            rsl = (akt / sma130) * 100
            
            daten.append({"Name": name, "Kurs": akt, "Delta %": change, "RSL": rsl})
        except: continue
    return pd.DataFrame(daten)

# 4. UI ohne Styling-Abhängigkeiten (Stabil)
if st.button("🚀 Marktanalyse starten"):
    with st.spinner("Scanne Markt..."):
        df = lade_daten()
        if not df.empty:
            df_top = df.sort_values(by="Delta %", ascending=False).head(10)
            df_flop = df.sort_values(by="Delta %", ascending=True).head(10)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🟢 TOP 10")
                st.dataframe(df_top, use_container_width=True)
            with col2:
                st.subheader("🔴 FLOP 10")
                st.dataframe(df_flop, use_container_width=True)
        else:
            st.error("Keine Daten gefunden. Bitte erneut versuchen.")
