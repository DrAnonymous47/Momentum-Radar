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
# 2. VOLLSTÄNDIGE AKTIEN-DATENBANK (DAX 40, MDAX 50, TECDAX 30, SDAX 70)
# =============================================================================
# Format: "TICKER.DE": ("Firmenname", "Index")
AKTIEN_DATENBANK = {
    # --- DAX 40 (VOLLSTÄNDIG) ---
    "ADS.DE": ("Adidas", "DAX"),
    "ALV.DE": ("Allianz", "DAX"),
    "BAS.DE": ("BASF", "DAX"),
    "BAYN.DE": ("Bayer", "DAX"),
    "BEI.DE": ("Beiersdorf", "DAX"),
    "BMW.DE": ("BMW", "DAX"),
    "BNR.DE": ("Brenntag", "DAX"),
    "CBK.DE": ("Commerzbank", "DAX"),
    "CON.DE": ("Continental", "DAX"),
    "1COV.DE": ("Covestro", "DAX"),
    "DTG.DE": ("Daimler Truck", "DAX"),
    "DBK.DE": ("Deutsche Bank", "DAX"),
    "DB1.DE": ("Deutsche Börse", "DAX"),
    "DPW.DE": ("DHL Group", "DAX"),
    "DTE.DE": ("Deutsche Telekom", "DAX / TecDAX"),
    "EOAN.DE": ("E.ON", "DAX"),
    "FRE.DE": ("Fresenius", "DAX"),
    "HNR1.DE": ("Hannover Rück", "DAX"),
    "HEI.DE": ("Heidelberg Materials", "DAX"),
    "HEN3.DE": ("Henkel", "DAX"),
    "IFX.DE": ("Infineon", "DAX / TecDAX"),
    "MBG.DE": ("Mercedes-Benz Group", "DAX"),
    "MRK.DE": ("Merck", "DAX"),
    "MTX.DE": ("MTU Aero Engines", "DAX"),
    "MUV2.DE": ("Münchener Rück", "DAX"),
    "PAH3.DE": ("Porsche Automobil Holding", "DAX"),
    "P911.DE": ("Porsche AG Vz.", "DAX"),
    "PUM.DE": ("Puma", "DAX"),
    "QIA.DE": ("Qiagen", "DAX / TecDAX"),
    "RHM.DE": ("Rheinmetall", "DAX"),
    "RWE.DE": ("RWE", "DAX"),
    "SAP.DE": ("SAP", "DAX / TecDAX"),
    "SRT3.DE": ("Sartorius", "DAX / TecDAX"),
    "SIE.DE": ("Siemens", "DAX"),
    "ENR.DE": ("Siemens Energy", "DAX"),
    "SHL.DE": ("Siemens Healthineers", "DAX"),
    "SY1.DE": ("Symrise", "DAX"),
    "VOW3.DE": ("Volkswagen Vz.", "DAX"),
    "VNA.DE": ("Vonovia", "DAX"),
    "ZAL.DE": ("Zalando", "DAX"),

    # --- MDAX 50 & TECDAX 30 (VOLLSTÄNDIG) ---
    "AIXA.DE": ("Aixtron", "TecDAX / MDAX"),
    "AFX.DE": ("Carl Zeiss Meditec", "TecDAX / MDAX"),
    "BC8.DE": ("Bechtle", "TecDAX / MDAX"),
    "BKG.DE": ("Bilfinger", "MDAX"),
    "EVD.DE": ("CTS Eventim", "MDAX"),
    "DWNI.DE": ("Deutsche Wohnen", "MDAX"),
    "DUE.DE": ("Dürr", "MDAX"),
    "EVK.DE": ("Evonik Industries", "MDAX"),
    "EVT.DE": ("Evotec", "TecDAX / MDAX"),
    "FIE.DE": ("Fielmann", "MDAX"),
    "FRA.DE": ("Fraport", "MDAX"),
    "FNTN.DE": ("freenet", "TecDAX / MDAX"),
    "G1A.DE": ("GEA Group", "MDAX"),
    "GXI.DE": ("Gerresheimer", "MDAX"),
    "HLAG.DE": ("Hapag-Lloyd", "MDAX"),
    "HAG.DE": ("Hensoldt", "TecDAX / MDAX"),
    "HOT.DE": ("Hochtief", "MDAX"),
    "HYQ.DE": ("Hypoport", "MDAX"),
    "JEN.DE": ("Jenoptik", "TecDAX / MDAX"),
    "JUN3.DE": ("Jungheinrich", "MDAX"),
    "KGX.DE": ("KION Group", "MDAX"),
    "KRN.DE": ("Krones", "MDAX"),
    "LEG.DE": ("LEG Immobilien", "MDAX"),
    "LHA.DE": ("Lufthansa", "MDAX"),
    "NEM.DE": ("Nemetschek", "TecDAX / MDAX"),
    "NDX1.DE": ("Nordex", "TecDAX / MDAX"),
    "PNE3.DE": ("PNE AG", "SDAX / TecDAX"),
    "PSM.DE": ("ProSiebenSat.1", "MDAX"),
    "RRTL.DE": ("RTL Group", "MDAX"),
    "S92.DE": ("SMA Solar Technology", "TecDAX / MDAX"),
    "SZG.DE": ("Salzgitter", "MDAX"),
    "TEG.DE": ("TAG Immobilien", "MDAX"),
    "TKA.DE": ("thyssenkrupp", "MDAX"),
    "UTDI.DE": ("United Internet", "TecDAX / MDAX"),
    "WCH.DE": ("Wacker Chemie", "MDAX"),
    "WAF.DE": ("Siltronic", "TecDAX / MDAX"),
    "IOS.DE": ("IONOS", "TecDAX / MDAX"),
    "SUAN.DE": ("SÜSS MicroTec", "TecDAX / SDAX"),
    "TMV.DE": ("TeamViewer", "TecDAX / MDAX"),
    "ELG.DE": ("Elmos Semiconductor", "TecDAX / SDAX"),
    "COK.DE": ("Cancom", "TecDAX / SDAX"),
    "O2D.DE": ("Telefónica Deutschland", "TecDAX / MDAX"),

    # --- SDAX 70 (WICHTIGE VERTRETER & ERGÄNZUNGEN) ---
    "1U1.DE": ("1&1", "SDAX / TecDAX"),
    "AT1.DE": ("Aroundtown", "SDAX"),
    "DEQ.DE": ("Deutz", "SDAX"),
    "DRW3.DE": ("Drägerwerk", "SDAX"),
    "DWS.DE": ("DWS Group", "SDAX"),
    "GFT.DE": ("GFT Technologies", "SDAX / TecDAX"),
    "HAB.DE": ("Hamborner REIT", "SDAX"),
    "HLE.DE": ("HELLA", "SDAX"),
    "KCO.DE": ("Klöckner & Co", "SDAX"),
    "MOR.DE": ("MorphoSys", "SDAX / TecDAX"),
    "NOEJ.DE": ("Norma Group", "SDAX"),
    "SGL.DE": ("SGL Carbon", "SDAX"),
    "SOW.DE": ("Software AG", "SDAX"),
    "SNG.DE": ("STRATEC", "SDAX / TecDAX"),
    "TPE.DE": ("Technotrans", "SDAX"),
    "VAC.DE": ("Varta", "SDAX"),
    "WAC.DE": ("Wacker Neuson", "SDAX")
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
            
            # --- FILTER ---
            # Bedingung A: Preis unter 100 Euro
            if ist_kurs > 100.0:
                continue
                
            # Bedingung B: TOPs (> +2.5% UND RSL > 100)
            ist_top_kandidat = (abw_vortag_prozent > 2.5) and (rsl_wert > 100.0)
            
            # Bedingung C: FLOPs (< -2.5%, RSL ignoriert)
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
        with st.spinner("Scanne alle Aktien aus DAX, MDAX, SDAX & TecDAX..."):
            df_ergebnis = lade_und_berechne_markt_daten()
            
            if df_ergebnis.empty:
                st.warning("⚠️ Keine Treffer! Kein Wert aus den vier Indizes erfüllt aktuell alle Kriterien.")
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
                    st.subheader("🟢 Top 10 Ausbrüche (RSL > 100)")
                    st.dataframe(df_top10, use_container_width=True, hide_index=True, column_config=spalten_layout)
                else:
                    st.info("Aktuell keine Top-Treffer (keine Aktie über +2,5% mit RSL > 100).")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if not df_flop10.empty:
                    st.subheader("🔴 Flop 10 Einbrüche (RSL ignoriert)")
                    st.dataframe(df_flop10, use_container_width=True, hide_index=True, column_config=spalten_layout)
                else:
                    st.info("Aktuell keine Flop-Treffer (keine Aktie unter -2,5%).")

                st.success(f"✅ Letztes Update: {datetime.now().strftime('%H:%M:%S Uhr')}")

    if live_modus:
        with tabellen_platzhalter.container():
            zeichne_tabellen()
        time.sleep(60) 
        st.rerun()     
    else:
        if st.button("🚀 Marktanalyse ausführen", type="primary"):
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

