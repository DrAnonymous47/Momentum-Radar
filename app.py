import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# =============================================================================
# 1. SEITEN-KONFIGURATION & LAYOUT
# =============================================================================
st.set_page_config(
    page_title="Deutscher Markt Radar Pro", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# 2. GESAMTE DEUTSCHE AKTIEN-DATENBANK (VOLLSTÄNDIGER MARKT SCAN)
# =============================================================================
DEUTSCHE_AKTIEN = {
    # --- DAX 40 ---
    "ADS.DE": ("Adidas", "DAX"), "ALV.DE": ("Allianz", "DAX"), "BAS.DE": ("BASF", "DAX"),
    "BAYN.DE": ("Bayer", "DAX"), "BEI.DE": ("Beiersdorf", "DAX"), "BMW.DE": ("BMW", "DAX"),
    "BNR.DE": ("Brenntag", "DAX"), "CBK.DE": ("Commerzbank", "DAX"), "CON.DE": ("Continental", "DAX"),
    "1COV.DE": ("Covestro", "DAX"), "DTG.DE": ("Daimler Truck", "DAX"), "DBK.DE": ("Deutsche Bank", "DAX"),
    "DB1.DE": ("Deutsche Börse", "DAX"), "DPW.DE": ("DHL Group", "DAX"), "DTE.DE": ("Deutsche Telekom", "DAX"),
    "EOAN.DE": ("E.ON", "DAX"), "FRE.DE": ("Fresenius", "DAX"), "HNR1.DE": ("Hannover Rück", "DAX"),
    "HEI.DE": ("Heidelberg Materials", "DAX"), "HEN3.DE": ("Henkel", "DAX"), "IFX.DE": ("Infineon", "DAX"),
    "MBG.DE": ("Mercedes-Benz Group", "DAX"), "MRK.DE": ("Merck", "DAX"), "MTX.DE": ("MTU Aero Engines", "DAX"),
    "MUV2.DE": ("Münchener Rück", "DAX"), "PAH3.DE": ("Porsche SE", "DAX"), "P911.DE": ("Porsche AG Vz.", "DAX"),
    "PUM.DE": ("Puma", "DAX"), "QIA.DE": ("Qiagen", "DAX"), "RHM.DE": ("Rheinmetall", "DAX"),
    "RWE.DE": ("RWE", "DAX"), "SAP.DE": ("SAP", "DAX"), "SRT3.DE": ("Sartorius", "DAX"),
    "SIE.DE": ("Siemens", "DAX"), "ENR.DE": ("Siemens Energy", "DAX"), "SHL.DE": ("Siemens Healthineers", "DAX"),
    "SY1.DE": ("Symrise", "DAX"), "VOW3.DE": ("Volkswagen Vz.", "DAX"), "VNA.DE": ("Vonovia", "DAX"),
    "ZAL.DE": ("Zalando", "DAX"),

    # --- MDAX & TECDAX ---
    "AIXA.DE": ("Aixtron", "TecDAX"), "AFX.DE": ("Carl Zeiss Meditec", "TecDAX"),
    "BC8.DE": ("Bechtle", "MDAX"), "BKG.DE": ("Bilfinger", "MDAX"), "EVD.DE": ("CTS Eventim", "MDAX"),
    "DWNI.DE": ("Deutsche Wohnen", "MDAX"), "DUE.DE": ("Dürr", "MDAX"), "EVK.DE": ("Evonik", "MDAX"),
    "EVT.DE": ("Evotec", "TecDAX"), "FIE.DE": ("Fielmann", "MDAX"), "FRA.DE": ("Fraport", "MDAX"),
    "FNTN.DE": ("freenet", "TecDAX"), "G1A.DE": ("GEA Group", "MDAX"), "GXI.DE": ("Gerresheimer", "MDAX"),
    "HLAG.DE": ("Hapag-Lloyd", "MDAX"), "HAG.DE": ("Hensoldt", "TecDAX"), "HOT.DE": ("Hochtief", "MDAX"),
    "HYQ.DE": ("Hypoport", "MDAX"), "JEN.DE": ("Jenoptik", "TecDAX"), "JUN3.DE": ("Jungheinrich", "MDAX"),
    "KGX.DE": ("KION Group", "MDAX"), "KRN.DE": ("Krones", "MDAX"), "LEG.DE": ("LEG Immobilien", "MDAX"),
    "LHA.DE": ("Lufthansa", "MDAX"), "NEM.DE": ("Nemetschek", "TecDAX"), "NDX1.DE": ("Nordex", "TecDAX"),
    "PSM.DE": ("ProSiebenSat.1", "MDAX"), "RRTL.DE": ("RTL Group", "MDAX"), "S92.DE": ("SMA Solar", "TecDAX"),
    "SZG.DE": ("Salzgitter", "MDAX"), "TEG.DE": ("TAG Immobilien", "MDAX"), "TKA.DE": ("thyssenkrupp", "MDAX"),
    "UTDI.DE": ("United Internet", "TecDAX"), "WCH.DE": ("Wacker Chemie", "MDAX"), "WAF.DE": ("Siltronic", "TecDAX"),
    "IOS.DE": ("IONOS", "TecDAX"), "SUAN.DE": ("SÜSS MicroTec", "TecDAX"), "TMV.DE": ("TeamViewer", "TecDAX"),
    "ELG.DE": ("Elmos Semi", "TecDAX"), "COK.DE": ("Cancom", "TecDAX"), "O2D.DE": ("Telefónica", "TecDAX"),

    # --- SDAX, NEBENWERTE & SMALL-CAPS (KLASSIKER & KLEINE MARKEN) ---
    "DEQ.DE": ("Deutz AG", "SDAX / Nebenwert"),
    "HDD.DE": ("Heidelberger Druck", "Nebenwert"),
    "CEC.DE": ("Ceconomy (MediaMarkt/Saturn)", "SDAX"),
    "BVB.DE": ("Borussia Dortmund", "SDAX"),
    "VAC.DE": ("Varta", "SDAX / Nebenwert"),
    "LEI.DE": ("Leifheit", "Nebenwert"),
    "MLP.DE": ("MLP SE", "SDAX"),
    "MED.DE": ("Medios", "SDAX"),
    "HAB.DE": ("Hamborner REIT", "SDAX"),
    "1U1.DE": ("1&1", "SDAX"),
    "AT1.DE": ("Aroundtown", "SDAX"),
    "DRW3.DE": ("Drägerwerk", "SDAX"),
    "DWS.DE": ("DWS Group", "SDAX"),
    "GFT.DE": ("GFT Technologies", "SDAX"),
    "HLE.DE": ("HELLA", "SDAX"),
    "KCO.DE": ("Klöckner & Co", "SDAX"),
    "MOR.DE": ("MorphoSys", "SDAX"),
    "NOEJ.DE": ("Norma Group", "SDAX"),
    "SGL.DE": ("SGL Carbon", "SDAX"),
    "SOW.DE": ("Software AG", "SDAX"),
    "SNG.DE": ("STRATEC", "SDAX"),
    "TPE.DE": ("Technotrans", "Nebenwert"),
    "WAC.DE": ("Wacker Neuson", "SDAX"),
    "PNE3.DE": ("PNE AG", "SDAX"),
    "PFV.DE": ("Pfeiffer Vacuum", "Nebenwert"),
    "ADV.DE": ("Adesso", "SDAX"), "A2E.DE": ("Aumann", "Nebenwert"),
    "G24.DE": ("Scout24", "MDAX"), "GLJ.DE": ("GRENKE", "SDAX"),
    "B9C.DE": ("Basler", "Nebenwert"), "LNS.DE": ("LPKF Laser", "Nebenwert"),
    "KTA.DE": ("KWS Saat", "SDAX"), "S3T.DE": ("Secunet", "SDAX"),
    "SAX.DE": ("Ströer", "MDAX"), "GMM.DE": ("Hamborner", "SDAX"),
    "O2D.DE": ("Telefónica Deutschland", "TecDAX"), "BWB.DE": ("Bet-at-home", "Nebenwert")
}

# =============================================================================
# 3. KERNLOGIK: DATA-FETCHING & BERECHNUNG
# =============================================================================
@st.cache_data(ttl=60)
def lade_und_berechne_markt_daten(max_preis, min_top_prozent, min_flop_prozent):
    erfolgreiche_treffer = []
    
    for ticker, (name, segment) in DEUTSCHE_AKTIEN.items():
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
            
            # RSL (130 Tage SMA) - Rein als Info!
            sma_130 = df['Close'].rolling(window=130).mean().iloc[-1]
            rsl_wert = (ist_kurs / sma_130) * 100
            
            # -----------------------------------------------------------------
            # FILTER-LOGIK (RSL SPIELT HIER NULL ROLLE)
            # -----------------------------------------------------------------
            # Optionaler Preisfilter (0 = Deaktiviert, zeigt alle Aktien)
            if max_preis > 0 and ist_kurs > max_preis:
                continue
                
            # Schwellenwerte für Gewinner/Verlierer
            ist_top = (abw_vortag_prozent >= min_top_prozent)
            ist_flop = (abw_vortag_prozent <= -abs(min_flop_prozent))
            
            if not (ist_top or ist_flop):
                continue
                
            # RSL als reine Infoanzeige (Grün/Rot)
            rsl_text = f"🟢 {rsl_wert:.0f}" if rsl_wert >= 100.0 else f"🔴 {rsl_wert:.0f}"
                
            erfolgreiche_treffer.append({
                "Name": name,
                "Segment": segment,
                "IST Kurs": ist_kurs,
                "Schluss Vortag": schluss_vortag,
                "Abw. Vortag (%)": abw_vortag_prozent,
                "Ø 3 Tage": durchschnitt_3_tage,
                "Abw. 3 Tage (%)": abw_3_tage_prozent,
                "RSL (Info)": rsl_text
            })
            
        except Exception:
            continue
            
    return pd.DataFrame(erfolgreiche_treffer)

# =============================================================================
# 4. DASHBOARD OBERFLÄCHE
# =============================================================================
def main():
    heute_str = datetime.now().strftime("%d.%m.%Y")
    st.title("📈 Deutscher Markt Radar Pro")
    st.markdown(f"**Stand:** {heute_str} | Automatische Analyse aller deutschen Werte")
    
    st.sidebar.header("⚙️ Filter & Einstellungen")
    
    max_preis = st.sidebar.number_input(
        "Maximaler Aktienkurs in € (0 = Alle Kurse/Keine Grenze):", 
        min_value=0, 
        max_value=1000, 
        value=0, 
        step=10,
        help="0 bedeutet: Es gibt kein Preislimit. Auch Aktien unter 10 € oder über 100 € werden angezeigt."
    )
    
    min_top_prozent = st.sidebar.slider(
        "Top-Schwelle (Mindestgewinn in %):", 
        min_value=0.5, 
        max_value=10.0, 
        value=2.5, 
        step=0.5
    )
    
    min_flop_prozent = st.sidebar.slider(
        "Flop-Schwelle (Mindestverlust in %):", 
        min_value=0.5, 
        max_value=10.0, 
        value=2.5, 
        step=0.5
    )
    
    live_modus = st.sidebar.toggle("🔄 Live-Radar aktivieren (60s Update)")
    
    st.markdown("---")

    tabellen_platzhalter = st.empty()
    
    def zeichne_tabellen():
        with st.spinner("Scanne alle deutschen Marktwerte..."):
            df_ergebnis = lade_und_berechne_markt_daten(max_preis, min_top_prozent, min_flop_prozent)
            
            if df_ergebnis.empty:
                st.warning("⚠️ Keine Treffer mit den aktuellen Schwellenwerten gefunden.")
            else:
                df_tops = df_ergebnis[df_ergebnis["Abw. Vortag (%)"] > 0]
                df_flops = df_ergebnis[df_ergebnis["Abw. Vortag (%)"] < 0]
                
                df_top15 = df_tops.sort_values(by="Abw. Vortag (%)", ascending=False).head(15)
                df_flop15 = df_flops.sort_values(by="Abw. Vortag (%)", ascending=True).head(15)
                
                spalten_layout = {
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Segment": st.column_config.TextColumn("Segment", width="small"),
                    "IST Kurs": st.column_config.NumberColumn("IST Kurs", format="%.2f €"),
                    "Schluss Vortag": st.column_config.NumberColumn("Schluss Vortag", format="%.2f €"),
                    "Abw. Vortag (%)": st.column_config.NumberColumn("Abw. Vortag", format="%+.2f %%"),
                    "Ø 3 Tage": st.column_config.NumberColumn("Ø 3 Tage", format="%.2f €"),
                    "Abw. 3 Tage (%)": st.column_config.NumberColumn("Abw. 3 Tage", format="%+.2f %%"),
                    "RSL (Info)": st.column_config.TextColumn("RSL (Info)", width="small")
                }

                if not df_top15.empty:
                    st.subheader(f"🟢 Top Ausbrüche (≥ +{min_top_prozent}%)")
                    st.dataframe(df_top15, use_container_width=True, hide_index=True, column_config=spalten_layout)
                else:
                    st.info(f"Aktuell keine Gewinner über +{min_top_prozent}%.")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if not df_flop15.empty:
                    st.subheader(f"🔴 Flop Einbrüche (≤ -{min_flop_prozent}%)")
                    st.dataframe(df_flop15, use_container_width=True, hide_index=True, column_config=spalten_layout)
                else:
                    st.info(f"Aktuell keine Verlierer unter -{min_flop_prozent}%.")

                st.success(f"✅ Letztes Update: {datetime.now().strftime('%H:%M:%S Uhr')} | Gesamtzahl überprüfter deutscher Firmen: {len(DEUTSCHE_AKTIEN)}")

    if live_modus:
        with tabellen_platzhalter.container():
            zeichne_tabellen()
        time.sleep(60) 
        st.rerun()     
    else:
        if st.button("🚀 Markt jetzt scannen", type="primary"):
            with tabellen_platzhalter.container():
                zeichne_tabellen()

    # =============================================================================
    # 5. NOTIZBEREICH
    # =============================================================================
    st.markdown("---")
    st.subheader("📝 Notizen:")
    st.text_area(
        "Handelsbeobachtungen festhalten:",
        height=120,
        placeholder="z. B. Deutz oder Heidelberger Druck heute besonders aktiv..."
    )

if __name__ == "__main__":
    main()

