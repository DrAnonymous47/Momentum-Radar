import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. STREAMLIT CONFIG (Muss ganz oben stehen)
st.set_page_config(page_title="Deutscher Markt Radar Ultra Pro", layout="wide")

# Modernes FinTech Dark-Mode Design
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; border: 1px solid #2a2e39; }
</style>
""", unsafe_allow_html=True)

# 2. KOMPLETTE & KORRIGIERTE DATENBANK (Aktueller Stand XETRA)
DEUTSCHE_AKTIEN = {
    # --- DAX 40 (Die 40 größten deutschen Unternehmen) ---
    "ADS.DE": ("Adidas", "DAX"), "AIR.DE": ("Airbus", "DAX"), "ALV.DE": ("Allianz SE", "DAX"),
    "BAS.DE": ("BASF", "DAX"), "BAYN.DE": ("Bayer AG", "DAX"), "BEI.DE": ("Beiersdorf", "DAX"),
    "BMW.DE": ("BMW AG", "DAX"), "BNR.DE": ("Brenntag", "DAX"), "CBK.DE": ("Commerzbank", "DAX"),
    "CON.DE": ("Continental", "DAX"), "1COV.DE": ("Covestro", "DAX"), "DTG.DE": ("Daimler Truck", "DAX"),
    "DB1.DE": ("Deutsche Börse", "DAX"), "DBK.DE": ("Deutsche Bank", "DAX"), "DTE.DE": ("Deutsche Telekom", "DAX"),
    "DHL.DE": ("DHL Group", "DAX"), "EON.DE": ("E.ON", "DAX"), "FRE.DE": ("Fresenius", "DAX"),
    "HEI.DE": ("Heidelberg Materials", "DAX"), "HEN3.DE": ("Henkel", "DAX"), "HNR1.DE": ("Hannover Rück", "DAX"),
    "IFX.DE": ("Infineon", "DAX"), "MBG.DE": ("Mercedes-Benz Group", "DAX"), "MRK.DE": ("Merck KGaA", "DAX"),
    "MTX.DE": ("MTU Aero Engines", "DAX"), "MUV2.DE": ("Münchener Rück", "DAX"), "P911.DE": ("Porsche AG", "DAX"),
    "PAH3.DE": ("Porsche SE", "DAX"), "QIA.DE": ("Qiagen", "DAX"), "RHM.DE": ("Rheinmetall", "DAX"),
    "RWE.DE": ("RWE AG", "DAX"), "SAP.DE": ("SAP SE", "DAX"), "SRT3.DE": ("Sartorius", "DAX"),
    "SIE.DE": ("Siemens AG", "DAX"), "ENR.DE": ("Siemens Energy", "DAX"), "SHL.DE": ("Siemens Healthineers", "DAX"),
    "SY1.DE": ("Symrise", "DAX"), "VOW3.DE": ("Volkswagen Vz.", "DAX"), "VNA.DE": ("Vonovia", "DAX"),
    "ZAL.DE": ("Zalando", "DAX"),

    # --- MDAX (Mittelgroße Unternehmen) ---
    "AIXA.DE": ("Aixtron", "MDAX"), "AMZ.DE": ("SMA Solar", "MDAX"), "BC8.DE": ("Bechtle", "MDAX"),
    "BKN.DE": ("Bilfinger", "MDAX"), "BOSS.DE": ("Hugo Boss", "MDAX"), "CTS.DE": ("CTS Eventim", "MDAX"), 
    "DEL2.DE": ("Delivery Hero", "MDAX"), "EVK.DE": ("Evonik Industries", "MDAX"), "EVT.DE": ("Evotec", "MDAX"),
    "FME.DE": ("Fresenius Medical Care", "MDAX"), "FRA.DE": ("Fraport", "MDAX"), "FPE3.DE": ("Fuchs SE", "MDAX"), 
    "G1A.DE": ("GEA Group", "MDAX"), "GXI.DE": ("Gerresheimer", "MDAX"), "HAG.DE": ("Hensoldt", "MDAX"), 
    "HFG.DE": ("HelloFresh", "MDAX"), "HLE.DE": ("Hella", "MDAX"), "HOT.DE": ("Hochtief", "MDAX"), 
    "JUN3.DE": ("Jungheinrich", "MDAX"), "KBX.DE": ("Knorr-Bremse", "MDAX"), "KRN.DE": ("Krones", "MDAX"), 
    "LEG.DE": ("LEG Immobilien", "MDAX"), "LHA.DE": ("Lufthansa", "MDAX"), "NEM.DE": ("Nemetschek", "MDAX"),
    "PUM.DE": ("PUMA", "MDAX"), "RAA.DE": ("Rational", "MDAX"), "RDC.DE": ("Redcare Pharmacy", "MDAX"), 
    "SHA.DE": ("Schaeffler", "MDAX"), "SIX2.DE": ("Sixt SE", "MDAX"), "SVAB.DE": ("Ströer", "MDAX"), 
    "TAG.DE": ("TAG Immobilien", "MDAX"), "TKA.DE": ("Thyssenkrupp", "MDAX"), "TMV.DE": ("TeamViewer", "MDAX"), 
    "TLX.DE": ("Talanx", "MDAX"), "TUI1.DE": ("TUI AG", "MDAX"), "UTDI.DE": ("United Internet", "MDAX"), 
    "WCH.DE": ("Wacker Chemie", "MDAX"), "G24.DE": ("Scout24", "MDAX"), "HYQ.DE": ("Hypoport", "MDAX"),

    # --- SDAX & Nebenwerte (Kleine Unternehmen & Prime Standard) ---
    "1U1.DE": ("1&1 AG", "SDAX"), "A3M.DE": ("Auto1 Group", "SDAX"), "ADV.DE": ("Adesso", "SDAX"),
    "AT1.DE": ("Aroundtown", "SDAX"), "BVB.DE": ("Borussia Dortmund", "SDAX"), "CEC.DE": ("Ceconomy", "SDAX"),
    "COK.DE": ("Cancom", "SDAX"), "DEQ.DE": ("Deutz AG", "SDAX"), "DNX.DE": ("Dermapharm", "SDAX"),
    "DRW3.DE": ("Drägerwerk", "SDAX"), "ELG.DE": ("Elmos Semiconductor", "SDAX"), "FNTN.DE": ("Freenet", "SDAX"),
    "GFT.DE": ("GFT Technologies", "SDAX"), "GLJ.DE": ("GRENKE AG", "SDAX"), "HDD.DE": ("Heidelberger Druck", "SDAX"),
    "HHFA.DE": ("HHLA", "SDAX"), "HOC.DE": ("Hornbach Holding", "SDAX"), "JEN.DE": ("Jenoptik", "SDAX"),
    "KCO.DE": ("Klöckner & Co", "SDAX"), "KSB3.DE": ("KSB SE", "SDAX"), "KWS.DE": ("KWS Saat", "SDAX"),
    "LPK.DE": ("LPKF Laser", "SDAX"), "MDN.DE": ("MEDION", "Prime Standard"), "MLP.DE": ("MLP SE", "SDAX"),
    "PNE.DE": ("PNE AG", "SDAX"), "SMT.DE": ("SUSS MicroTec", "SDAX"), "VOS.DE": ("Vossloh", "SDAX"),
    "VAR1.DE": ("VARTA AG", "Prime Standard"), "HAB.DE": ("Hamborner REIT", "SDAX"), "SFQ.DE": ("SAF-Holland", "SDAX"),
    "WAC.DE": ("Wacker Neuson", "SDAX")
}

# 3. HIGH-SPEED BATCH DATEN LADEN
@st.cache_data(ttl=300)
def load_market_data():
    tickers = list(DEUTSCHE_AKTIEN.keys())
    
    # Lädt ALLE Ticker parallel in einem einzigen Request runter!
    raw_data = yf.download(tickers, period="7mo", progress=False)
    
    summary_data = []
    history_dict = {}

    for ticker, (name, segment) in DEUTSCHE_AKTIEN.items():
        try:
            # Extrahiere Ticker-Daten aus dem Multi-Index DataFrame
            df = pd.DataFrame({
                'Open': raw_data['Open'][ticker],
                'High': raw_data['High'][ticker],
                'Low': raw_data['Low'][ticker],
                'Close': raw_data['Close'][ticker]
            }).dropna(subset=['Close'])

            if len(df) >= 2:
                current_price = float(df['Close'].iloc[-1])
                prev_close = float(df['Close'].iloc[-2])
                
                change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
                
                # 130-Tage SMA für RSL
                if len(df) >= 130:
                    sma130 = df['Close'].rolling(window=130).mean().iloc[-1]
                    rsl = (current_price / sma130) * 100 if sma130 > 0 else None
                else:
                    rsl = None

                rsl_trend = "🟢" if (rsl and rsl >= 100) else "🔴"

                summary_data.append({
                    "Name": name,
                    "Ticker": ticker,
                    "Segment": segment,
                    "Kurs (€)": round(current_price, 2),
                    "Veränderung (%)": round(change_pct, 2),
                    "RSL": round(rsl, 2) if rsl else "N/A",
                    "Trend": rsl_trend
                })
                history_dict[ticker] = df
        except Exception:
            continue

    return pd.DataFrame(summary_data), history_dict

# 4. HAUPTANWENDUNG
def main():
    st.title("📈 Deutscher Markt Radar Ultra Pro (DAX / MDAX / SDAX)")
    
    with st.spinner("Scanne 110+ deutsche Aktientitel in Echtzeit von XETRA..."):
        df, history_dict = load_market_data()

    if df.empty:
        st.error("Fehler beim Laden der Aktiendaten. Bitte versuche es später erneut.")
        return

    # SIDEBAR FILTER
    st.sidebar.header("🔍 Filter & Einstellungen")
    
    segment_filter = st.sidebar.multiselect(
        "Index / Segment filtern:",
        options=["DAX", "MDAX", "SDAX", "Prime Standard"],
        default=[]
    )
    
    max_price = st.sidebar.number_input("Max. Preis (€) [0 = Deaktiviert]", min_value=0.0, value=0.0, step=5.0)
    top_thresh = st.sidebar.slider("Min. Gewinner Schwelle (%)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
    flop_thresh = st.sidebar.slider("Min. Verlierer Schwelle (%)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
    search_query = st.sidebar.text_input("Aktie suchen...", "")

    # FILTERING LOGIK
    filtered_df = df.copy()

    if segment_filter:
        filtered_df = filtered_df[filtered_df['Segment'].isin(segment_filter)]

    if search_query:
        filtered_df = filtered_df[
            filtered_df['Name'].str.contains(search_query, case=False) |
            filtered_df['Ticker'].str.contains(search_query, case=False)
        ]

    if max_price > 0:
        filtered_df = filtered_df[filtered_df['Kurs (€)'] <= max_price]

    # TOP & FLOP SORTIERUNG
    top_winners = filtered_df[filtered_df['Veränderung (%)'] >= top_thresh].sort_values(by='Veränderung (%)', ascending=False)
    flop_losers = filtered_df[filtered_df['Veränderung (%)'] <= -flop_thresh].sort_values(by='Veränderung (%)', ascending=True)

    # KPI METRICS
    c1, c2, c3 = st.columns(3)
    c1.metric("Gescannte Aktien", len(filtered_df))
    c2.metric("Top Gewinner", len(top_winners))
    c3.metric("Flop Verlierer", len(flop_losers))

    st.markdown("---")

    # TABELLEN
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader(f"🟢 Top Gewinner (>= +{top_thresh}%)")
        if not top_winners.empty:
            st.dataframe(
                top_winners,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Veränderung (%)": st.column_config.NumberColumn(format="+%.2f %%"),
                    "Kurs (€)": st.column_config.NumberColumn(format="%.2f €")
                }
            )
        else:
            st.info("Keine Aktien mit dieser Mindestgewinn-Schwelle gefunden.")

    with col_right:
        st.subheader(f"🔴 Flop Verlierer (<= -{flop_thresh}%)")
        if not flop_losers.empty:
            st.dataframe(
                flop_losers,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Veränderung (%)": st.column_config.NumberColumn(format="%.2f %%"),
                    "Kurs (€)": st.column_config.NumberColumn(format="%.2f €")
                }
            )
        else:
            st.info("Keine Aktien mit dieser Mindestverlust-Schwelle gefunden.")

    st.markdown("---")

    # INTERAKTIVER CHART
    st.subheader("📊 Interaktiver Candlestick-Chart")
    
    available_tickers = [t for t in filtered_df['Ticker'].tolist() if t in history_dict]
    
    if available_tickers:
        selected_ticker = st.selectbox(
            "Aktie für Analyse auswählen:",
            options=available_tickers,
            format_func=lambda x: f"{DEUTSCHE_AKTIEN[x][0]} ({x}) [{DEUTSCHE_AKTIEN[x][1]}]"
        )

        if selected_ticker in history_dict:
            stock_df = history_dict[selected_ticker].copy()
            stock_df['SMA130'] = stock_df['Close'].rolling(window=130).mean()

            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=stock_df.index,
                open=stock_df['Open'],
                high=stock_df['High'],
                low=stock_df['Low'],
                close=stock_df['Close'],
                name="Kurs"
            ))
            
            fig.add_trace(go.Scatter(
                x=stock_df.index,
                y=stock_df['SMA130'],
                mode='lines',
                name='130-Tage SMA',
                line=dict(color='orange', width=1.5)
            ))

            fig.update_layout(
                title=f"{DEUTSCHE_AKTIEN[selected_ticker][0]} ({selected_ticker})",
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # WATCHLIST & EXPORT
    st.subheader("⭐ Watchlist & Daten-Export")
    
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []

    selected_wl = st.selectbox("Aktie zur Watchlist hinzufügen:", df['Ticker'].tolist(), key="wl_add")
    if st.button("Zu Watchlist hinzufügen"):
        if selected_wl not in st.session_state.watchlist:
            st.session_state.watchlist.append(selected_wl)
            st.success(f"{selected_wl} zur Watchlist hinzugefügt!")

    if st.session_state.watchlist:
        st.write("Deine geparkten Favoriten:", st.session_state.watchlist)

    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Alle gefilterten Daten als CSV herunterladen",
        data=csv_data,
        file_name="aktien_radar_daten.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()

