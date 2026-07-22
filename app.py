import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. STREAMLIT CONFIGURATION
st.set_page_config(page_title="Deutscher Markt Radar Pro", layout="wide")

# Modernes Dark-Mode Design
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; border: 1px solid #2a2e39; }
</style>
""", unsafe_allow_html=True)

# 2. PRÄZISE DATENBANK (INKL. TECDAX-ZUORDNUNG)
DEUTSCHE_AKTIEN = {
    # --- DAX 40 ---
    "ADS.DE": ("Adidas", "DAX"), "AIR.DE": ("Airbus", "DAX"), "ALV.DE": ("Allianz", "DAX"),
    "BAS.DE": ("BASF", "DAX"), "BAYN.DE": ("Bayer", "DAX"), "BEI.DE": ("Beiersdorf", "DAX"),
    "BMW.DE": ("BMW", "DAX"), "BNR.DE": ("Brenntag", "DAX"), "CBK.DE": ("Commerzbank", "DAX"),
    "CON.DE": ("Continental", "DAX"), "1COV.DE": ("Covestro", "DAX"), "DTG.DE": ("Daimler Truck", "DAX"),
    "DB1.DE": ("Deutsche Börse", "DAX"), "DBK.DE": ("Deutsche Bank", "DAX"), "DTE.DE": ("Deutsche Telekom", "DAX/TecDAX"),
    "DHL.DE": ("DHL Group", "DAX"), "EON.DE": ("E.ON", "DAX"), "FRE.DE": ("Fresenius", "DAX"),
    "HEI.DE": ("Heidelberg Materials", "DAX"), "HEN3.DE": ("Henkel", "DAX"), "HNR1.DE": ("Hannover Rück", "DAX"),
    "IFX.DE": ("Infineon", "DAX/TecDAX"), "MBG.DE": ("Mercedes-Benz Group", "DAX"), "MRK.DE": ("Merck KGaA", "DAX"),
    "MTX.DE": ("MTU Aero Engines", "DAX"), "MUV2.DE": ("Münchener Rück", "DAX"), "P911.DE": ("Porsche AG", "DAX"),
    "PAH3.DE": ("Porsche SE", "DAX"), "QIA.DE": ("Qiagen", "DAX/TecDAX"), "RHM.DE": ("Rheinmetall", "DAX"),
    "RWE.DE": ("RWE", "DAX"), "SAP.DE": ("SAP", "DAX/TecDAX"), "SRT3.DE": ("Sartorius", "DAX/TecDAX"),
    "SIE.DE": ("Siemens", "DAX"), "ENR.DE": ("Siemens Energy", "DAX"), "SHL.DE": ("Siemens Healthineers", "DAX/TecDAX"),
    "SY1.DE": ("Symrise", "DAX"), "VOW3.DE": ("Volkswagen Vz.", "DAX"), "VNA.DE": ("Vonovia", "DAX"),
    "ZAL.DE": ("Zalando", "DAX"),

    # --- MDAX ---
    "DEQ.DE": ("Deutz AG", "MDAX"), "JEN.DE": ("Jenoptik", "MDAX/TecDAX"),
    "SZG.DE": ("Salzgitter AG", "MDAX"), "AIXA.DE": ("Aixtron", "MDAX/TecDAX"), 
    "BC8.DE": ("Bechtle", "MDAX/TecDAX"), "BKN.DE": ("Bilfinger", "MDAX"),
    "BOSS.DE": ("Hugo Boss", "MDAX"), "CTS.DE": ("CTS Eventim", "MDAX"), 
    "EVK.DE": ("Evonik", "MDAX"), "FRA.DE": ("Fraport", "MDAX"), 
    "G1A.DE": ("GEA Group", "MDAX"), "GXI.DE": ("Gerresheimer", "MDAX"), 
    "HAG.DE": ("Hensoldt", "MDAX/TecDAX"), "KBX.DE": ("Knorr-Bremse", "MDAX"), 
    "KRN.DE": ("Krones", "MDAX"), "LEG.DE": ("LEG Immobilien", "MDAX"), 
    "LHA.DE": ("Lufthansa", "MDAX"), "NEM.DE": ("Nemetschek", "MDAX/TecDAX"),
    "PUM.DE": ("PUMA", "MDAX"), "RAA.DE": ("Rational", "MDAX"), 
    "SHA.DE": ("Schaeffler", "MDAX"), "TAG.DE": ("TAG Immobilien", "MDAX"), 
    "TKA.DE": ("Thyssenkrupp", "MDAX"), "TLX.DE": ("Talanx", "MDAX"), 
    "TUI1.DE": ("TUI AG", "MDAX"), "UTDI.DE": ("United Internet", "MDAX/TecDAX"), 
    "WCH.DE": ("Wacker Chemie", "MDAX"),

    # --- SDAX & REINE TECDAX-WERTE ---
    "1U1.DE": ("1&1 AG", "SDAX"), "A3M.DE": ("Auto1 Group", "SDAX"), 
    "ADV.DE": ("Adesso", "SDAX"), "AT1.DE": ("Aroundtown", "SDAX"), 
    "BVB.DE": ("Borussia Dortmund", "SDAX"), "CEC.DE": ("Ceconomy", "SDAX"),
    "COK.DE": ("Cancom", "SDAX/TecDAX"), "DNX.DE": ("Dermapharm", "SDAX"), 
    "DRW3.DE": ("Drägerwerk", "SDAX/TecDAX"), "ELG.DE": ("Elmos Semiconductor", "SDAX/TecDAX"), 
    "FNTN.DE": ("Freenet", "SDAX/TecDAX"), "FIE.DE": ("Fielmann", "SDAX"), 
    "AFX.DE": ("Carl Zeiss Meditec", "SDAX/TecDAX"), "TMV.DE": ("TeamViewer", "SDAX"), 
    "GFT.DE": ("GFT Tech", "SDAX"), "GLJ.DE": ("Grenke", "SDAX"), 
    "HDD.DE": ("Heidelberger Druck", "SDAX"), "HOC.DE": ("Hornbach", "SDAX"), 
    "JUN3.DE": ("Jungheinrich", "SDAX"), "KCO.DE": ("Klöckner & Co", "SDAX"), 
    "KWS.DE": ("KWS Saat", "SDAX"), "LPK.DE": ("LPKF Laser", "SDAX"), 
    "MLP.DE": ("MLP SE", "SDAX"), "PNE.DE": ("PNE AG", "SDAX"), 
    "RDC.DE": ("Redcare Pharmacy", "SDAX"), "SGL.DE": ("SGL Carbon", "SDAX"), 
    "SMT.DE": ("SUSS MicroTec", "SDAX/TecDAX"), "VOS.DE": ("Vossloh", "SDAX"), 
    "HAB.DE": ("Hamborner REIT", "SDAX"), "WAC.DE": ("Wacker Neuson", "SDAX"), 
    "EVT.DE": ("Evotec", "SDAX/TecDAX"), "AMZ.DE": ("SMA Solar", "SDAX/TecDAX"), 
    "HFG.DE": ("HelloFresh", "SDAX"), "KTN.DE": ("Kontron", "TecDAX"),
    "NDX1.DE": ("Nordex", "TecDAX"), "IOS.DE": ("Ionos", "TecDAX"),
    "TPE.DE": ("PVA TePla", "TecDAX"), "VER.DE": ("Verbio", "TecDAX")
}

# 3. DATENABRUF VIA XETRA
@st.cache_data(ttl=300)
def load_market_data():
    tickers = list(DEUTSCHE_AKTIEN.keys())
    raw_data = yf.download(tickers, period="5d", interval="1d", progress=False)
    
    summary_data = []

    for ticker, (name, segment) in DEUTSCHE_AKTIEN.items():
        try:
            close_series = raw_data['Close'][ticker].dropna()
            
            if len(close_series) >= 2:
                current_price = float(close_series.iloc[-1])
                prev_close = float(close_series.iloc[-2])
                
                change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0

                summary_data.append({
                    "Name": name,
                    "Ticker": ticker,
                    "Index / Segment": segment,
                    "Kurs (€)": round(current_price, 2),
                    "Tagesveränderung (%)": round(change_pct, 2)
                })
        except Exception:
            continue

    return pd.DataFrame(summary_data)

# 4. BENUTZEROBERFLÄCHE
def main():
    st.title("📈 Deutscher Markt & TecDAX Radar")
    
    with st.spinner("Lade XETRA-Echtzeitdaten..."):
        df = load_market_data()

    if df.empty:
        st.error("Keine Daten geladen.")
        return

    # SIDEBAR FILTER
    st.sidebar.header("🔍 Filter & Suche")
    
    # Filter-Optionen basierend auf den neuen Segmenten
    selected_index = st.sidebar.selectbox(
        "Index / Segment wählen:",
        options=["Alle anzeigen", "DAX", "MDAX", "SDAX", "TecDAX (inkl. Doppeltlistungen)"]
    )
    
    search_query = st.sidebar.text_input("Aktie suchen...", "")

    filtered_df = df.copy()

    if selected_index == "DAX":
        filtered_df = filtered_df[filtered_df['Index / Segment'].str.startswith("DAX")]
    elif selected_index == "MDAX":
        filtered_df = filtered_df[filtered_df['Index / Segment'].str.contains("MDAX")]
    elif selected_index == "SDAX":
        filtered_df = filtered_df[filtered_df['Index / Segment'].str.contains("SDAX")]
    elif selected_index == "TecDAX (inkl. Doppeltlistungen)":
        filtered_df = filtered_df[filtered_df['Index / Segment'].str.contains("TecDAX")]

    if search_query:
        filtered_df = filtered_df[
            filtered_df['Name'].str.contains(search_query, case=False) |
            filtered_df['Ticker'].str.contains(search_query, case=False)
        ]

    sorted_df = filtered_df.sort_values(by="Tagesveränderung (%)", ascending=False)

    # METRIKEN
    c1, c2 = st.columns(2)
    c1.metric("Gescannte Werte", len(sorted_df))
    if not sorted_df.empty:
        top = sorted_df.iloc[0]
        c2.metric("Top-Performer", f"{top['Name']} ({top['Tagesveränderung (%)']:+.2f}%)")

    st.markdown("---")

    st.subheader("📊 Übersicht")
    st.dataframe(
        sorted_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tagesveränderung (%)": st.column_config.NumberColumn(format="%+.2f %%"),
            "Kurs (€)": st.column_config.NumberColumn(format="%.2f €")
        }
    )

if __name__ == "__main__":
    main()

