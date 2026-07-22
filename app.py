import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. STREAMLIT CONFIG (Muss ganz oben stehen)
st.set_page_config(page_title="Deutscher Markt Radar", layout="wide")

# Modernes FinTech Dark-Mode Design
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1e222d; padding: 15px; border-radius: 10px; border: 1px solid #2a2e39; }
</style>
""", unsafe_allow_html=True)

# 2. DATENBANK (XETRA TICKER)
DEUTSCHE_AKTIEN = {
    "SAP.DE": ("SAP SE", "DAX"),
    "SIE.DE": ("Siemens AG", "DAX"),
    "MBG.DE": ("Mercedes-Benz Group", "DAX"),
    "DTE.DE": ("Deutsche Telekom", "DAX"),
    "ALV.DE": ("Allianz SE", "DAX"),
    "RHM.DE": ("Rheinmetall AG", "DAX"),
    "BMW.DE": ("BMW AG", "DAX"),
    "LHA.DE": ("Lufthansa", "MDAX"),
    "TKA.DE": ("Thyssenkrupp", "MDAX"),
    "NEM.DE": ("Nemetschek", "MDAX"),
    "AIXA.DE": ("Aixtron", "TecDAX"),
    "HAG.DE": ("Hensoldt", "MDAX"),
    "DEQ.DE": ("Deutz AG", "SDAX"),
    "HDD.DE": ("Heidelberger Druck", "SDAX"),
    "CEC.DE": ("Ceconomy", "SDAX"),
    "VAC.DE": ("VARTA AG", "SDAX"),
    "MED.DE": ("MEDION", "SDAX"),
    "HAB.DE": ("Hamborner REIT", "SDAX"),
    "BVB.DE": ("Borussia Dortmund", "SDAX"),
    "1U1.DE": ("1&1 AG", "SDAX"),
    "LEI.DE": ("Leoni AG", "SDAX"),
    "MLP.DE": ("MLP SE", "SDAX")
}

# 3. DATEN LADEN & BERECHNEN
@st.cache_data(ttl=60)
def load_market_data():
    summary_data = []
    history_dict = {}

    for ticker, (name, segment) in DEUTSCHE_AKTIEN.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="7mo")
            
            if len(df) >= 2:
                current_price = float(df['Close'].iloc[-1])
                prev_close = float(df['Close'].iloc[-2])
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                # 130-Tage SMA für RSL
                if len(df) >= 130:
                    sma130 = df['Close'].rolling(window=130).mean().iloc[-1]
                    rsl = (current_price / sma130) * 100
                else:
                    rsl = None

                rsl_trend = "🟢" if (rsl and rsl >= 100) else "🔴"

                summary_data.append({
                    "Ticker": ticker,
                    "Name": name,
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
    st.title("📈 Deutscher Markt Radar Ultra Pro")
    
    # Daten laden
    with st.spinner("Lade Echtzeitkurse von XETRA..."):
        df, history_dict = load_market_data()

    if df.empty:
        st.error("Fehler beim Laden der Aktiendaten. Bitte versuche es später erneut.")
        return

    # SIDEBAR FILTER
    st.sidebar.header("🔍 Filter & Einstellungen")
    max_price = st.sidebar.number_input("Max. Preis (€) [0 = Deaktiviert]", min_value=0.0, value=0.0, step=5.0)
    top_thresh = st.sidebar.slider("Top Gewinner Schwelle (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
    flop_thresh = st.sidebar.slider("Flop Verlierer Schwelle (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
    search_query = st.sidebar.text_input("Aktie suchen...", "")

    # FILTERING LOGIK
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[
            filtered_df['Name'].str.contains(search_query, case=False) |
            filtered_df['Ticker'].str.contains(search_query, case=False)
        ]

    if max_price > 0:
        filtered_df = filtered_df[filtered_df['Kurs (€)'] <= max_price]

    top_winners = filtered_df[filtered_df['Veränderung (%)'] >= top_thresh]
    flop_losers = filtered_df[filtered_df['Veränderung (%)'] <= -flop_thresh]

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
        st.dataframe(top_winners, use_container_width=True)

    with col_right:
        st.subheader(f"🔴 Flop Verlierer (<= -{flop_thresh}%)")
        st.dataframe(flop_losers, use_container_width=True)

    st.markdown("---")

    # INTERAKTIVER CHART
    st.subheader("📊 Interaktiver Candlestick-Chart")
    selected_ticker = st.selectbox(
        "Aktie für Analyse auswählen:",
        options=list(history_dict.keys()),
        format_func=lambda x: f"{DEUTSCHE_AKTIEN[x][0]} ({x})"
    )

    if selected_ticker in history_dict:
        stock_df = history_dict[selected_ticker].copy()
        stock_df['SMA130'] = stock_df['Close'].rolling(window=130).mean()

        fig = go.Figure()
        
        # Candlestick Trace
        fig.add_trace(go.Candlestick(
            x=stock_df.index,
            open=stock_df['Open'],
            high=stock_df['High'],
            low=stock_df['Low'],
            close=stock_df['Close'],
            name="Kurs"
        ))
        
        # 130-Tage SMA Linie
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

