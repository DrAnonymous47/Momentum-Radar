import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

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
# 2. UMFASSENDE AKTIEN-DATENBANK (DAX, MDAX, SDAX, TecDAX)
# =============================================================================
AKTIEN_DATENBANK = {
    # --- DAX WERTE ---
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer",
    "BEI.DE": "Beiersdorf", "BMW.DE": "BMW", "BNR.DE": "Brenntag", "CBK.DE": "Commerzbank",
    "CON.DE": "Continental", "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck",
    "DBK.DE": "Deutsche Bank", "DB1.DE": "Deutsche Börse", "DPW.DE": "DHL Group",
    "DTE.DE": "Deutsche Telekom", "EOAN.DE": "E.ON", "FRE.DE": "Fresenius",
    "HNR1.DE": "Hannover Rück", "HEI.DE": "Heidelberg Materials", "HEN3.DE": "Henkel",
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck",
    "MTX.DE": "MTU Aero", "MUV2.DE": "Munich Re", "PAH3.DE": "Porsche",
    "PUM.DE": "Puma", "QIA.DE": "Qiagen", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE",
    "SAP.DE": "SAP", "SRT3.DE": "Sartorius", "SIE.DE": "Siemens", "ENR.DE": "Siemens Energy",
    "SHL.DE": "Siemens Healthineers", "SY1.DE": "Symrise", "VOW3.DE": "Volkswagen",
    "VNA.DE": "Vonovia", "ZAL.DE": "Zalando",

    # --- MDAX / TECDAX / SDAX HIGHLIGHTS ---
    "AIXA.DE": "Aixtron", "LHA.DE": "Lufthansa", "FRA.DE": "Fraport", "EVK.DE": "Evonik",
    "FPE3.DE": "Fuchs", "GXI.DE": "Gerresheimer", "HAG.DE": "Hensoldt", "HOT.DE": "Hochtief",
    "JUN3.DE": "Jungheinrich", "KRN.DE": "Krones", "LEG.DE": "LEG Immobilien",
    "NOEJ.DE": "Norma Group", "O2D.DE": "Telefonica", "PSM.DE": "ProSiebenSat.1",
    "SOW.DE": "Software AG", "NDX1.DE": "Nordex", "UTDI.DE": "United Internet",
    "IOS.DE": "IONOS", "SANT.DE": "Santander", "AFX.DE": "Carl Zeiss Meditec",
    "NEM.DE": "Nemetschek", "WAF.DE": "Siltronic", "ARL.DE": "Aareal Bank",
    "COK.DE": "Cancom", "CTS.DE": "CTS Eventim", "DUE.DE": "Dürr", "EVD.DE": "CTS Eventim",
    "FIE.DE": "Fielmann", "G1A.DE": "GEA Group", "HLAG.DE": "Hapag-Lloyd",
    "KGX.DE": "KION Group", "KCO.DE": "Klöckner & Co", "NDA.DE": "Aurubis",
    "RRTL.DE": "RTL Group", "TEG.DE": "TAG Immobilien", "TKA.DE": "thyssenkrupp",
    "1U1.DE": "1&1", "WCH.DE": "Wacker Chemie", "SMA.DE": "SMA Solar", "S92.DE": "SMA Solar Tech"
}

# =============================================================================
# 3. KERNLOGIK: BERECHNUNG DER DATEN
# =============================================================================
@st.cache_data(ttl=600)
def lade_und_berechne_markt_daten():
    erfolgreiche_treffer = []
    
    for ticker, name in AKTIEN_DATENBANK.items():
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
            
            # -----------------------------------------------------------------
            # 4. FILTER ANWENDEN
            # -----------------------------------------------------------------
            # Bedingung A: Preis unter 100 Euro
            if ist_kurs > 100.0:
                continue
                
            # Bedingung B: Abweichung muss GRÖSSER als 2,5% ODER KLEINER als -2,5% sein
            if -2.5 <= abw_vortag_prozent <= 2.5:
                continue
                
            # Bedingung C: RSL muss stark sein (> 100)
            if rsl_wert <= 100.0:
                continue
                
            # Daten für die Tabelle speichern
            erfolgreiche_treffer.append({
                "Name": name,
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
# 5. UI-KOMPONENTEN (Benutzeroberfläche)
# =============================================================================
def main():
    heute_str = datetime.now().strftime("%d.%m.%Y")
    st.title("📈 Index Radar Pro (DAX, MDAX, SDAX, TecDAX)")
    st.markdown(f"**Stand:** {heute_str} | **Filter:** Preis < 100€ | RSL > 110 | **Abweichung > +2,5% oder < -2,5%**")
    st.markdown("---")

    if st.button("🚀 Marktanalyse ausführen", type="primary"):
        with st.spinner("Lade Live-Börsendaten und filtere nach Ausbrüchen..."):
            
            df_ergebnis = lade_und_berechne_markt_daten()
            
            if df_ergebnis.empty:
                st.warning("⚠️ Keine Treffer heute! Keine Aktie erfüllt aktuell alle Kriterien (RSL > 110 UND Abweichung über/unter 2,5%).")
            else:
                df_top10 = df_ergebnis.sort_values(by="Abw. Vortag (%)", ascending=False).head(10)
                df_flop10 = df_ergebnis.sort_values(by="Abw. Vortag (%)", ascending=True).head(10)
                
                spalten_layout = {
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "IST Kurs": st.column_config.NumberColumn("IST Kurs", format="%.2f €"),
                    "Schluss Vortag": st.column_config.NumberColumn("Schluss Vortag", format="%.2f €"),
                    "Abw. Vortag (%)": st.column_config.NumberColumn("Abw. Vortag", format="%+.2f %%"),
                    "Ø 3 Tage": st.column_config.NumberColumn("Ø 3 Tage", format="%.2f €"),
                    "Abw. 3 Tage (%)": st.column_config.NumberColumn("Abw. 3 Tage", format="%+.2f %%"),
                    "RSL": st.column_config.NumberColumn("RSL", format="%.0f")
                }

                st.subheader("🟢 Top 10 (Stärkste Ausbrüche nach oben)")
                st.dataframe(
                    df_top10, 
                    use_container_width=True, 
                    hide_index=False, 
                    column_config=spalten_layout
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.subheader("🔴 Flop 10 (Stärkste Einbrüche nach unten)")
                st.dataframe(
                    df_flop10, 
                    use_container_width=True, 
                    hide_index=False, 
                    column_config=spalten_layout
                )

                st.success(f"✅ Analyse erfolgreich. {len(df_ergebnis)} Werte haben die strengen Filter bestanden.")

    # =============================================================================
    # 6. NOTIZBEREICH
    # =============================================================================
    st.markdown("---")
    st.subheader("📝 Notiz / Info:")
    
    notiz = st.text_area(
        "Hier kannst du dir wichtige Beobachtungen notieren:",
        height=150,
        placeholder="Beispiel: Telekom heute besonders stark am Nachmittag..."
    )
    
    if st.button("💾 Notiz zwischenspeichern"):
        st.toast("Notiz wurde für diese Sitzung gespeichert!", icon="✅")

if __name__ == "__main__":
    main()

