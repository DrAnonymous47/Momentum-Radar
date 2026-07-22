import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Deutscher Markt Radar Pro", layout="wide")

# Modernes FinTech Dark-Mode Design
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; border: 1px solid #2a2e39; }
</style>
""", unsafe_allow_html=True)

# 1. GEPRÜFTE XETRA-DATENBANK (Exakte Ticker für deutsche Börse)
DEUTSCHE_AKTIEN = {
    # --- DAX 40 ---
    "ADS.DE": ("Adidas", "DAX"), "AIR.DE": ("Airbus", "DAX"), "ALV.DE": ("Allianz", "DAX"),
    "BAS.DE": ("BASF", "DAX"), "BAYN.DE": ("Bayer", "DAX"), "BEI.DE": ("Beiersdorf", "DAX"),
    "BMW.DE": ("BMW", "DAX"), "BNR.DE": ("Brenntag", "DAX"), "CBK.DE": ("Commerzbank", "DAX"),
    "CON.DE": ("Continental", "DAX"), "1COV.DE": ("Covestro", "DAX"), "DTG.DE": ("Daimler Truck", "DAX"),
    "DB1.DE": ("Deutsche Börse", "DAX"), "DBK.DE": ("Deutsche Bank", "DAX"), "DTE.DE": ("Deutsche Telekom", "DAX"),
    "DHL.DE": ("DHL Group", "DAX"), "EON.DE": ("E.ON", "DAX"), "FRE.DE": ("Fresenius", "DAX"),
    "HEI.DE": ("Heidelberg Materials", "DAX"), "HEN3.DE": ("Henkel", "DAX"), "HNR1.DE": ("Hannover Rück", "DAX"),
    "IFX.DE": ("Infineon", "DAX"), "MBG.DE": ("Mercedes-Benz", "DAX"), "MRK.DE": ("Merck", "DAX"),
    "MTX.DE": ("MTU Aero Engines", "DAX"), "MUV2.DE": ("Münchener Rück", "DAX"), "P911.DE": ("Porsche AG", "DAX"),
    "PAH3.DE": ("Porsche SE", "DAX"), "QIA.DE": ("Qiagen", "DAX"), "RHM.DE": ("Rheinmetall", "DAX"),
    "RWE.DE": ("RWE", "DAX"), "SAP.DE": ("SAP", "DAX"), "SRT3.DE": ("Sartorius", "DAX"),
    "SIE.DE": ("Siemens", "DAX"), "ENR.DE": ("Siemens Energy", "DAX"), "SHL.DE": ("Siemens Healthineers", "DAX"),
    "SY1.DE": ("Symrise", "DAX"), "VOW3.DE": ("Volkswagen", "DAX"), "VNA.DE": ("Vonovia", "DAX"),
    "ZAL.DE": ("Zalando", "DAX"),

    # --- MDAX ---
    "AIXA.DE": ("Aixtron", "MDAX"), "BC8.DE": ("Bechtle", "MDAX"), "BKN.DE": ("Bilfinger", "MDAX"),
    "BOSS.DE": ("Hugo Boss", "MDAX"), "CTS.DE": ("CTS Eventim", "MDAX"), "EVK.DE": ("Evonik", "MDAX"),
    "EVT.DE": ("Evotec", "MDAX"), "FME.DE": ("Fresenius Medical Care", "MDAX"), "FRA.DE": ("Fraport", "MDAX"),
    "G1A.DE": ("GEA Group", "MDAX"), "GXI.DE": ("Gerresheimer", "MDAX"), "HAG.DE": ("Hensoldt", "MDAX"),
    "HFG.DE": ("HelloFresh", "MDAX"), "JUN3.DE": ("Jungheinrich", "MDAX"), "KBX.DE": ("Knorr-Bremse", "MDAX"),
    "KRN.DE": ("Krones", "MDAX"), "LEG.DE": ("LEG Immobilien", "MDAX"), "LHA.DE": ("Lufthansa", "MDAX"),
    "NEM.DE": ("Nemetschek", "MDAX"), "PUM.DE": ("PUMA", "MDAX"), "RAA.DE": ("Rational", "MDAX"),
    "RDC.DE": ("Redcare Pharmacy", "MDAX"), "SHA.DE": ("Schaeffler", "MDAX"), "SIX2.DE": ("Sixt", "MDAX"),
    "SVAB.DE": ("Ströer", "MDAX"), "TAG.DE": ("TAG Immobilien", "MDAX"), "TKA.DE": ("Thyssenkrupp", "MDAX"),
    "TMV.DE": ("TeamViewer", "MDAX"), "TLX.DE": ("Talanx", "MDAX"), "TUI1.DE": ("TUI", "MDAX"),
    "UTDI.DE": ("United Internet", "MDAX"), "WCH.DE": ("Wacker Chemie", "MDAX"),

    # --- SDAX & KLEINUNTERNEHMEN ---
    "DEQ.DE": ("Deutz AG", "SDAX"),
    "1U1.DE": ("1&1", "SDAX"),
    "A3M.DE": ("Auto1 Group", "SDAX"),
    "ADV.DE": ("Adesso", "SDAX"), "AT1.DE": ("Aroundtown", "SDAX"),
    "BVB.DE": ("Borussia Dortmund", "SDAX"), "CEC.DE": ("Ceconomy", "SDAX"),
    "COK.DE": ("Cancom", "SDAX"), "DNX.DE": ("Dermapharm", "SDAX"),
    "DRW3.DE": ("Drägerwerk", "SDAX"), "ELG.DE": ("Elmos Semi", "SDAX"),
    "FNTN.DE": ("Freenet", "SDAX"), "GFT.DE": ("GFT Tech", "SDAX"),
    "GLJ.DE": ("Grenke", "SDAX"), "HDD.DE": ("Heidelberger Druck", "SDAX"),
    "HOC.DE": ("Hornbach", "SDAX"), "JEN.DE": ("Jenoptik", "SDAX"),
    "KCO.DE": ("Klöckner & Co", "SDAX"), "KWS.DE": ("KWS Saat", "SDAX"),
    "LPK.DE": ("LPKF Laser", "SDAX"), "MLP.DE": ("MLP SE", "SDAX"),
    "MOR.DE": ("MorphoSys", "SDAX"), "PNE.DE": ("PNE AG", "SDAX"),
    "SGL.DE": ("SGL Carbon", "SDAX"), "SMT.DE": ("SUSS MicroTec", "SDAX"),
    "VOS.DE": ("Vossloh", "SDAX"), "VAR1.DE": ("VARTA AG", "SDAX"),
    "HAB.DE": ("Hamborner REIT", "SDAX"), "WAC.DE": ("Wacker Neuson", "SDAX")
}

# 2. PRÄZISER ECHTZEIT-ABRUF
@st.cache_data(ttl=60)
def load_market_data():
    tickers = list(DEUTSCHE_AKTIEN.keys())
    
    # Holt exakte Schluss- und Livekurse von XETRA
    raw_data = yf.download(tickers, period="5d", interval="1d", progress=False)
    
    summary_data = []
    history_dict = {}

    for ticker, (name, segment) in DEUTSCHE_AKTIEN.items():
        try:
            # Extrahiere die Kursreihe für die jeweilige Aktie
            close_series = raw_data['Close'][ticker].dropna()
            
            if len(close_series) >= 2:
                current_price = float(close_series.iloc[-1])
                prev_close = float(close_series.iloc[-2])
                
                change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0

                summary_data.append({
                    "Name": name,
                    "Ticker": ticker,
                    "Segment": segment,
                    "Kurs (€)": round(current_price, 2),
                    "Veränderung (%)": round(change_pct, 2)
                })
        except Exception:
            continue

    return pd.DataFrame(summary_data)

# 3. GUI
def main():
    st.title("📈 Deutscher Markt Radar (Präzise XETRA-Daten)")
    
    with st.spinner("Synchronisiere Live-Daten von Börse Frankfurt / XETRA..."):
        df = load_market_data()

    if df.empty:
        st.error("Verbindungsfehler zur Börse. Bitte neu laden.")
        return

    # FILTER
    st.sidebar.header("🔍 Filter")
    segment_filter = st.sidebar.multiselect("Index wählen:", ["DAX", "MDAX", "SDAX"], default=[])
    search_query = st.sidebar.text_input("Aktie suchen (z. B. Deutz):", "")

    filtered_df = df.copy()

    if segment_filter:
        filtered_df = filtered_df[filtered_df['Segment'].isin(segment_filter)]

    if search_query:
        filtered_df = filtered_df[
            filtered_df['Name'].str.contains(search_query, case=False) |
            filtered_df['Ticker'].str.contains(search_query, case=False)
        ]

    # TOP & FLOP
    top_winners = filtered_df.sort_values(by='Veränderung (%)', ascending=False)
    
    st.subheader("📊 Live Marktübersicht")
    st.dataframe(
        top_winners,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Veränderung (%)": st.column_config.NumberColumn(format="%.2f %%"),
            "Kurs (€)": st.column_config.NumberColumn(format="%.2f €")
        }
    )

if __name__ == "__main__":
    main()

