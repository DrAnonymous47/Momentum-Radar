import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. SEITEN-KONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Index Radar Pro", page_icon="📈", layout="wide")

heute = datetime.now().strftime("%d.%m.%Y")
st.title(f"🇩🇪 Index Radar Pro – Stand: {heute}")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. TICKER-WÖRTERBUCH (VOLLE NAMEN AUSGESCHRIEBEN)
# -----------------------------------------------------------------------------
AKTIEN_NAMEN = {
    "ADS.DE": "Adidas", "ALV.DE": "Allianz", "BAS.DE": "BASF", "BAYN.DE": "Bayer", 
    "BEI.DE": "Beiersdorf", "BMW.DE": "BMW", "BNR.DE": "Brenntag", "CBK.DE": "Commerzbank",
    "CON.DE": "Continental", "1COV.DE": "Covestro", "DTG.DE": "Daimler Truck", 
    "DTE.DE": "Deutsche Telekom", "DPW.DE": "DHL Group", "DBK.DE": "Deutsche Bank", 
    "DB1.DE": "Deutsche Börse", "EOAN.DE": "E.ON", "FRE.DE": "Fresenius", 
    "HNR1.DE": "Hannover Rück", "HEI.DE": "Heidelberg Materials", "HEN3.DE": "Henkel", 
    "IFX.DE": "Infineon", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck", 
    "MTX.DE": "MTU Aero Engines", "MUV2.DE": "Munich Re", "PAH3.DE": "Porsche Holding", 
    "PUM.DE": "Puma", "QIA.DE": "Qiagen", "RHM.DE": "Rheinmetall", "SAP.DE": "SAP", 
    "SRT3.DE": "Sartorius", "SIE.DE": "Siemens", "ENR.DE": "Siemens Energy", 
    "SY1.DE": "Symrise", "VOW3.DE": "Volkswagen", "VNA.DE": "Vonovia", "ZAL.DE": "Zalando",
    "AIXA.DE": "Aixtron", "LHA.DE": "Lufthansa", "FRA.DE": "Fraport", "EVK.DE": "Evonik", 
    "IOS.DE": "IONOS", "RWE.DE": "RWE", "NDX1.DE": "Nordex", "SANT.DE": "Santander",
    "TKA.DE": "thyssenkrupp", "WCH.DE": "Wacker Chemie", "FPE3.DE": "Fuchs Petrolub"
}

# -----------------------------------------------------------------------------
# 3. KERN-BERECHNUNG
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def lade_und_analysiere_daten():
    ergebnisse = []
    
    for ticker, name in AKTIEN_NAMEN.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="7mo")
            
            if df.empty or len(df) < 130:
                continue
            
            df = df.dropna()
            
            aktueller_kurs = float(df['Close'].iloc[-1])
            vortag_kurs = float(df['Close'].iloc[-2])
            
            # FILTER 1: Preis darf maximal 100 Euro sein
            if aktueller_kurs > 100.0:
                continue
                
            # FILTER 2 (HAUPTFILTER): Bewegung NUR zwischen -2.5% und +2.5%
            heute_prozent = ((aktueller_kurs - vortag_kurs) / vortag_kurs) * 100
            if heute_prozent < -2.5 or heute_prozent > 2.5:
                continue
                
            # RSL BERECHNUNG (Kein Filter mehr, nur noch Wert-Ermittlung!)
            sma_130 = df['Close'].rolling(window=130).mean().iloc[-1]
            rsl_wert = (aktueller_kurs / sma_130) * 100
                
            # Durchschnitt der 3 Vortage berechnen (T-2, T-3, T-4)
            if len(df) >= 4:
                durchschnitt_3_vortage = df['Close'].iloc[-4:-1].mean()
            else:
                durchschnitt_3_vortage = vortag_kurs
                
            abweichung_3d_prozent = ((aktueller_kurs - durchschnitt_3_vortage) / durchschnitt_3_vortage) * 100
            
            # Treffer zur Liste hinzufügen
            ergebnisse.append({
                "Firmenname": name,
                "Aktuell": aktueller_kurs,
                "Vortag": vortag_kurs,
                "Heute %": heute_prozent,
                "3-Tage-Schnitt": durchschnitt_3_vortage,
                "Abweichung %": abweichung_3d_prozent,
                "RSL": rsl_wert
            })
            
        except Exception:
            continue
            
    return pd.DataFrame(ergebnisse)

# -----------------------------------------------------------------------------
# 4. FARB-LOGIK FÜR DIE TABELLE (Grün / Rot)
# -----------------------------------------------------------------------------
def färbe_rsl(wert):
    # RSL > 110 ist Grün, ansonsten Rot
    if wert > 110:
        return 'color: #00FF00; font-weight: bold;'
    else:
        return 'color: #FF0000; font-weight: bold;'

def färbe_prozent(wert):
    # Alles über 0 ist Grün, alles unter 0 ist Rot
    if wert > 0:
        return 'color: #00FF00; font-weight: bold;'
    elif wert < 0:
        return 'color: #FF0000; font-weight: bold;'
    else:
        return 'color: gray;'

# -----------------------------------------------------------------------------
# 5. BENUTZEROBERFLÄCHE
# -----------------------------------------------------------------------------
st.info("⚙️ **Aktive Filter:** 1. Preis max. 100 € | 2. Tagesbewegung **exakt zwischen -2,5% und +2,5%**")

if st.button("🚀 Marktanalyse jetzt starten (Dauert ca. 15 Sekunden)", type="primary"):
    
    with st.spinner("Scanne Indizes, berechne RSL und bewerte Schwankungen..."):
        df_ergebnisse = lade_und_analysiere_daten()
        
        st.markdown("---")
        
        if df_ergebnisse.empty:
            st.warning("⚠️ **Kein Treffer!** Aktuell gibt es keine Aktie unter 100€, die heute exakt zwischen -2,5% und +2,5% liegt.")
        else:
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Gescannte Firmen", len(AKTIEN_NAMEN))
            col_m2.metric("Treffer nach Filterung (+/- 2.5%)", len(df_ergebnisse))
            
            df_top = df_ergebnisse.sort_values(by="Heute %", ascending=False).head(10)
            df_flop = df_ergebnisse.sort_values(by="Heute %", ascending=True).head(10)
            
            # Formatierung und Einfärbung der Tabellen anwenden
            format_dict = {
                "Aktuell": "{:.2f} €",
                "Vortag": "{:.2f} €",
                "3-Tage-Schnitt": "{:.2f} €",
                "Heute %": "{:.2f} %",
                "Abweichung %": "{:.2f} %",
                "RSL": "{:.2f}"
            }
            
            # Tabellen stylen (Farben für RSL und Prozente zuweisen)
            styled_top = df_top.style.format(format_dict)\
                               .applymap(färbe_rsl, subset=["RSL"])\
                               .applymap(färbe_prozent, subset=["Heute %", "Abweichung %"])
                               
            styled_flop = df_flop.style.format(format_dict)\
                                 .applymap(färbe_rsl, subset=["RSL"])\
                                 .applymap(färbe_prozent, subset=["Heute %", "Abweichung %"])
            
            st.markdown("### 🟢 TOP 10 (Im Bereich +2,5% bis 0%)")
            st.dataframe(styled_top, use_container_width=True, hide_index=True)
            
            st.markdown("### 🔴 FLOP 10 (Im Bereich 0% bis -2,5%)")
            st.dataframe(styled_flop, use_container_width=True, hide_index=True)
            
            st.success("✅ Analyse fehlerfrei abgeschlossen. Alle Werte farblich markiert!")
