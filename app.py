import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. SEITEN-KONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Index Radar Pro", page_icon="📈", layout="wide")

heute = datetime.now().strftime("%d.%m.%Y")
st.title(f"📈 Index Radar Pro – Stand: {heute}")

# -----------------------------------------------------------------------------
# 2. TICKER-DATENBANK
# -----------------------------------------------------------------------------
TICKER_MAP = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BMW.DE": "BMW", "DTE.DE": "Deutsche Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens",
    "VOW3.DE": "Volkswagen", "RHM.DE": "Rheinmetall", "IFX.DE": "Infineon",
    "MBG.DE": "Mercedes-Benz", "RWE.DE": "RWE", "AIR.DE": "Airbus", "ZAL.DE": "Zalando",
    "LHA.DE": "Lufthansa", "IOS.DE": "IONOS", "CBK.DE": "Commerzbank", "DBK.DE": "Deutsche Bank"
}

# -----------------------------------------------------------------------------
# 3. KERN-FUNKTIONEN
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def hole_marktdaten():
    ergebnisse = []
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
            
            # 3-Tage Schnitt
            avg3 = df['Close'].iloc[-4:-1].mean()
            abweichung = ((akt - avg3) / avg3) * 100
            
            ergebnisse.append({
                "Name": name, "Kurs": akt, "Vortag": vor,
                "Delta %": change, "RSL": rsl, "Abweichung %": abweichung
            })
        except: continue
    return pd.DataFrame(ergebnisse)

# -----------------------------------------------------------------------------
# 4. UI & LOGIK
# -----------------------------------------------------------------------------
if st.button("🚀 Marktanalyse starten", type="primary"):
    with st.spinner("Berechne Daten..."):
        df = hole_marktdaten()
        
        # Metriken oben
        c1, c2, c3 = st.columns(3)
        c1.metric("Gescannte Firmen", len(TICKER_MAP))
        c2.metric("Aktive Treffer", len(df))
        c3.metric("Durchschnitt RSL", f"{df['RSL'].mean():.2f}")
        
        # Sortierung für Top / Flop
        df_top = df.sort_values(by="Delta %", ascending=False).head(10)
        df_flop = df.sort_values(by="Delta %", ascending=True).head(10)
        
        # Anzeige der Tabellen
        tab1, tab2 = st.tabs(["🟢 TOP 10 Performer", "🔴 FLOP 10 Performer"])
        
        with tab1:
            st.dataframe(df_top.style.format({"Kurs": "{:.2f} €", "Delta %": "{:.2f} %", "RSL": "{:.2f}"})
                         .background_gradient(subset=["Delta %"], cmap="Greens"), use_container_width=True)
            
        with tab2:
            st.dataframe(df_flop.style.format({"Kurs": "{:.2f} €", "Delta %": "{:.2f} %", "RSL": "{:.2f}"})
                         .background_gradient(subset=["Delta %"], cmap="Reds"), use_container_width=True)
        
        st.success("Analyse abgeschlossen!")
