import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# =============================================================================
# 1. SEITEN-KONFIGURATION & LAYOUT
# =============================================================================
st.set_page_config(
    page_title="Index Radar Pro", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# 2. ERWEITERTE AKTIEN-DATENBANK MIT INDEX-ZUORDNUNG
# =============================================================================
# Format: Ticker: (Name, Index)
AKTIEN_DATENBANK = {
    # --- DAX ---
    "ADS.DE": ("Adidas", "DAX"), "ALV.DE": ("Allianz", "DAX"), "BAS.DE": ("BASF", "DAX"),
    "BAYN.DE": ("Bayer", "DAX"), "BEI.DE": ("Beiersdorf", "DAX"), "BMW.DE": ("BMW", "DAX"),
    "BNR.DE": ("Brenntag", "DAX"), "CBK.DE": ("Commerzbank", "DAX"), "CON.DE": ("Continental", "DAX"),
    "1COV.DE": ("Covestro", "DAX"), "DTG.DE": ("Daimler Truck", "DAX"), "DBK.DE": ("Deutsche Bank", "DAX"),
    "DB1.DE": ("Deutsche Börse", "DAX"), "DPW.DE": ("DHL Group", "DAX"), "DTE.DE": ("Deutsche Telekom", "DAX"),
    "EOAN.DE": ("E.ON", "DAX"), "FRE.DE": ("Fresenius", "DAX"), "HNR1.DE": ("Hannover Rück", "DAX"),
    "HEI.DE": ("Heidelberg Materials", "DAX"), "HEN3.DE": ("Henkel", "DAX"), "IFX.DE": ("Infineon", "DAX / TecDAX"),
    "MBG.DE": ("Mercedes-Benz", "DAX"), "MRK.DE": ("Merck", "DAX"), "MTX.DE": ("MTU Aero", "DAX"),
    "MUV2.DE": ("Munich Re", "DAX"), "PAH3.DE": ("Porsche", "DAX"), "PUM.DE": ("Puma", "DAX"),
    "QIA.DE": ("Qiagen", "DAX / TecDAX"), "RHM.DE": ("Rheinmetall", "DAX"), "RWE.DE": ("RWE", "DAX"),
    "SAP.DE": ("SAP", "DAX / TecDAX"), "SRT3.DE": ("Sartorius", "DAX / TecDAX"), "SIE.DE": ("Siemens", "DAX"),
    "ENR.DE": ("Siemens Energy", "DAX"), "SHL.DE": ("Siemens Healthineers", "DAX"), "SY1.DE": ("Symrise", "DAX"),
    "VOW3.DE": ("Volkswagen", "DAX"), "VNA.DE": ("Vonovia", "DAX"), "ZAL.DE": ("Zalando", "DAX"),

    # --- TecDAX HIGHLIGHTS ---
    "AIXA.DE": ("Aixtron", "TecDAX"), "AFX.DE": ("Carl Zeiss Meditec", "TecDAX"),
    "COK.DE": ("Cancom", "TecDAX"), "EVT.DE": ("Evotec", "TecDAX"),
    "FNTN.DE": ("Freenet", "TecDAX"), "JEN.DE": ("Jenoptik", "TecDAX"),
    "NEM.DE": ("Nemetschek", "TecDAX"), "NDX1.DE": ("Nordex", "TecDAX"),
    "O2D.DE": ("Telefonica", "TecDAX"), "S92.DE": ("SMA Solar Tech", "TecDAX"),
    "UTDI.DE": ("United Internet", "TecDAX"), "WAF.DE": ("Siltronic", "TecDAX"),
    "IOS.DE": ("IONOS", "TecDAX"), "SUAN.DE": ("SÜSS MicroTec", "TecDAX"),
    "TMV.DE": ("TeamViewer", "TecDAX"), "ELG.DE": ("Elmos Semi", "TecDAX"),

    # --- MDAX & SDAX WERTE ---
    "LHA.DE": ("Lufthansa", "MDAX"), "FRA.DE": ("Fraport", "MDAX"), "EVK.DE": ("Evonik", "MDAX"),
    "GXI.DE": ("Gerresheimer", "MDAX"), "HAG.DE": ("Hensoldt", "MDAX"), "HOT.DE": ("Hochtief", "MDAX"),
    "JUN3.DE": ("Jungheinrich", "MDAX"), "KRN.DE": ("Krones", "MDAX"), "LEG.DE": ("LEG Immobilien", "MDAX"),
    "NOEJ.DE": ("Norma Group", "SDAX"), "PSM.DE": ("ProSiebenSat.1", "MDAX"), "CTS.DE": ("CTS Eventim", "MDAX"),
    "DUE.DE": ("Dürr", "MDAX"), "FIE.DE": ("Fielmann", "MDAX"), "G1A.DE": ("GEA Group", "MDAX"),
    "HLAG.DE": ("Hapag-Lloyd", "MDAX"), "KGX.DE": ("KION Group", "MDAX"), "KCO.DE": ("Klöckner & Co", "SDAX"),
    "NDA.DE": ("Aurubis", "MDAX"), "RRTL.DE": ("RTL Group", "MDAX"), "TEG.DE": ("TAG Immobilien", "MDAX"),
    "TKA.DE": ("thyssenkrupp", "MDAX"), "1U1.DE": ("1&1", "SDAX"), "WCH.DE": ("Wacker Chemie", "MDAX"),
    "PNE3.DE": ("PNE AG", "SDAX"), "SNG.DE": ("SGL Carbon", "SDAX")
}

# =============================================================================
# 3. KERNLOGIK: BERECHNUNG DER DATEN
# =============================================================================
@st.cache_data(ttl=60)
def lade_und_berechne_markt_daten():
    erfolgreiche_treffer = []
    
    for ticker, (name, index_name) in AKTIEN_DATENBANK.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="7mo")
            
            if df.empty or len(df) < 130:
                continue
                
            df = df.dropna()
            
            ist_kurs = float(df['Close'].iloc[-1])
            schluss_vortag = float(df['Close'].iloc[-2])
            
            abw_vortag_prozent = ((ist_kurs - schluss_vortag) / schluss_vortag) * 100
            
            if len(df) >= 4:
                durchschnitt_3_tage = df['Close'].iloc[-4:-1].mean()
            else:
                durchschnitt_3_tage = schluss_vortag
                
            abw_3_tage_prozent = ((ist_kurs - durchschnitt_3_tage) / durchschnitt_3_tage) * 100
            
            sma_130 = df['Close'].rolling(window=130).mean().iloc[-1]
            rsl_wert = (ist_kurs / sma_130) * 100
            
            # Filter A: Preis unter 100 Euro
            if ist_kurs > 100.0:
                continue
                
            # Logik für TOPs (> +2.5% UND RSL > 100)
            ist_top_kandidat = (abw_vortag_prozent > 2.5) and (rsl_wert > 100.0)
            
            # Logik für FLOPs (< -2.5%, RSL ignoriert)
            ist_flop_kandidat = (abw_vortag_prozent < -2.5)
            
            if not (ist_top_kandidat or ist_flop_kandidat):
                continue
                
            erfolgreiche_treffer.append({
                "Name": name,
                "Index": index_name,
                "IST Kurs": ist_kurs,
                "Schluss Vortag": schluss_vortag,
                "Abw. Vortag (%)": abw_vortag_prozent,
                "Ø 3 Tage": durchschnitt_3_tage,
                "Abw. 3 Tage (%)": abw_3_tage_prozent,
                "RSL": rsl_wert
            })
            
        except Exception:
            continue
            
    return pd.DataFrame(erfolgreiche_treffer)

# =============================================================================
# 4. UI & AUTO-UPDATE LOGIK
# =============================================================================
def main():
    heute_str = datetime.now().strftime("%d.%m.%Y")
    st.title("📈 Index Radar Pro (DAX, MDAX, SDAX, TecDAX)")
    st.markdown(f"**Stand:** {heute_str} | **Filter:** Preis < 100€ | **Tops:** > +2,5% & RSL>100 | **Flops:** < -2,5%")
    
    col_switch, _ = st.columns([1, 3])
    with col_switch:
        live_modus = st.toggle("🔄 Live-Radar aktivieren (60s Update)")
    
    st.markdown("---")

    tabellen_platzhalter = st.empty()
    
    def zeichne_tabellen():
        with st.spinner("Lade Live-Börsendaten für DAX, MDAX, SDAX & TecDAX..."):
            df_ergebnis = lade_und_berechne_markt_daten()
            
            if df_ergebnis.empty:
                st.warning("⚠️ Keine Treffer! Keine Aktie aus den Indizes erfüllt aktuell die Ausbruchs-Kriterien.")
            else:
                df_tops = df_ergebnis[df_ergebnis["Abw. Vortag (%)"] > 0]
                df_flops = df_ergebnis[df_ergebnis["Abw. Vortag (%)"] < 0]
                
                df_top10 = df_tops.sort_values(by="Abw. Vortag (%)", ascending=False).head(10)
                df_flop10 = df_flops.sort_values(by="Abw. Vortag (%)", ascending=True).head(10)
                
                spalten_layout = {
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Index": st.column_config.TextColumn("Index", width="small"),
                    "IST Kurs": st.column_config.NumberColumn("IST Kurs", format="%.2f €"),
                    "Schluss Vortag": st.column_config.NumberColumn("Schluss Vortag", format="%.2f €"),
                    "Abw. Vortag (%)": st.column_config.NumberColumn("Abw. Vortag", format="%+.2f %%"),
                    "Ø 3 Tage": st.column_config.NumberColumn("Ø 3 Tage", format="%.2f €"),
                    "Abw. 3 Tage (%)": st.column_config.NumberColumn("Abw. 3 Tage", format="%+.2f %%"),
                    "RSL": st.column_config.NumberColumn("RSL", format="%.0f")
                }

                if not df_top10.empty:
                    st.subheader("🟢 Top 10 Ausbrüche (DAX / MDAX / SDAX / TecDAX | RSL > 100)")
                    st.dataframe(df_top10, use_container_width=True, hide_index=True, column_config=spalten_layout)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if not df_flop10.empty:
                    st.subheader("🔴 Flop 10 Einbrüche (DAX / MDAX / SDAX / TecDAX | RSL ignoriert)")
                    st.dataframe(df_flop10, use_container_width=True, hide_index=True, column_config=spalten_layout)

                st.success(f"✅ Letztes Update: {datetime.now().strftime('%H:%M:%S Uhr')}")

    if live_modus:
        with tabellen_platzhalter.container():
            zeichne_tabellen()
        time.sleep(60) 
        st.rerun()     
    else:
        if st.button("🚀 Marktanalyse manuell ausführen", type="primary"):
            with tabellen_platzhalter.container():
                zeichne_tabellen()

    # =============================================================================
    # 5. NOTIZBEREICH
    # =============================================================================
    st.markdown("---")
    st.subheader("📝 Notiz / Info:")
    
    st.text_area(
        "Hier kannst du dir wichtige Beobachtungen notieren:",
        height=150,
        placeholder="Beispiel: TecDAX-Werte heute besonders stark..."
    )

if __name__ == "__main__":
    main()
