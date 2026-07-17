import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Index Radar Pro", page_icon="📈", layout="wide")

heute = datetime.now().strftime("%d.%m.%Y")
st.title(f"📈 Index Radar Pro – Stand: {heute}")

AKTIEN_LISTE = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BMW.DE": "BMW",
    "DTE.DE": "Deutsche Telekom", "SAP.DE": "SAP", "SIE.DE": "Siemens", "VOW3.DE": "Volkswagen"
}

def get_styled_color(val, is_rsl=False):
    if is_rsl: return 'color: #00FF00; font-weight: bold;' if val > 110 else 'color: #FF0000; font-weight: bold;'
    return 'color: #00FF00; font-weight: bold;' if val > 0 else 'color: #FF0000; font-weight: bold;'

if st.button("🚀 Markt-Scan ausführen"):
    for ticker, name in AKTIEN_LISTE.items():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        info = stock.info
        
        akt_kurs = hist['Close'].iloc[-1]
        vortag = hist['Close'].iloc[-2]
        change = ((akt_kurs - vortag) / vortag) * 100
        
        # Filter: Zeige nur, wenn im Bereich +/- 2.5%
        if -2.5 <= change <= 2.5:
            with st.expander(f"{ticker} - {name} ({change:.2f}%)"):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write(f"**Firma:** {info.get('longName', name)}")
                    st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
                    st.write(f"**Empfehlung:** {info.get('recommendationKey', 'N/A').upper()}")
                
                with col2:
                    fig = go.Figure(data=[go.Scatter(x=hist.index, y=hist['Close'], line=dict(color='#1f77b4'))])
                    fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown(f"**Business Summary:** {info.get('longBusinessSummary', 'Keine Infos verfügbar.')[:300]}...")
