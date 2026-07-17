import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Index Radar Pro", layout="wide")
heute = datetime.now().strftime("%d.%m.%Y")
st.title(f"📈 Index Radar Pro – Stand: {heute}")

# Vollständige Liste
AKTIEN_LISTE = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer", "BMW.DE": "BMW",
    "DTE.DE": "Deutsche Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens", "VOW3.DE": "Volkswagen",
    "RHM.DE": "Rheinmetall", "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "RWE.DE": "RWE",
    "AIR.DE": "Airbus", "CON.DE": "Continental", "ZAL.DE": "Zalando", "LHA.DE": "Lufthansa"
}

def farbe(val, pos_ist_gruen=True):
    if val > 0: return "color: #00FF00;" if pos_ist_gruen else "color: #FF0000;"
    return "color: #FF0000;" if pos_ist_gruen else "color: #00FF00;"

if st.button("🚀 Profi-Scan starten (Alle Daten + Charts)"):
    for ticker, name in AKTIEN_LISTE.items():
        try:
            time.sleep(0.6) # Schutz gegen Yahoo-Sperre
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo")
            if len(df) < 130: continue
            
            info = stock.info
            akt = df['Close'].iloc[-1]
            vor = df['Close'].iloc[-2]
            change = ((akt - vor) / vor) * 100
            
            # Bereich +/- 2.5%
            if -2.5 <= change <= 2.5:
                rsl = (akt / df['Close'].rolling(130).mean().iloc[-1]) * 100
                avg3 = df['Close'].iloc[-4:-1].mean()
                
                with st.expander(f"{ticker} | {name} | Änderung: {change:.2f}%"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Kurs:** {akt:.2f} €")
                        st.markdown(f"**RSL-Wert:** <span style='{farbe(rsl-110)}'>{rsl:.2f}</span>", unsafe_allow_html=True)
                        st.write(f"**Ø 3-Tage:** {avg3:.2f} €")
                        st.write(f"**Empfehlung:** {info.get('recommendationKey', 'N/A').upper()}")
                    with c2:
                        fig = go.Figure(data=go.Scatter(x=df.index, y=df['Close'], line=dict(color='cyan')))
                        fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0))
                        st.plotly_chart(fig, use_container_width=True)
                    st.write(f"**Business:** {info.get('longBusinessSummary', 'Keine Info')[:400]}...")
        except: continue
