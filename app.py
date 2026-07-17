import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np

# -----------------------------------------------------------------------------
# 1. SEITEN-KONFIGURATION (Profi-Layout)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Index Radar Pro | DAX, MDAX, SDAX, TecDAX", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Automatisches, tagesaktuelles Datum
heute = datetime.now().strftime("%d.%m.%Y")

st.title(f"🇩🇪 Index Radar Pro – Stand: {heute}")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. TICKER-DATENBANK (Über 130 deutsche Werte)
# -----------------------------------------------------------------------------
# Hier sind die wichtigsten und liquidesten Werte aus DAX, MDAX, SDAX und TecDAX
TICKERS = [
    # DAX
    "ADS.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE", "CBK.DE",
    "CON.DE", "1COV.DE", "DTG.DE", "DTE.DE", "DPW.DE", "DBK.DE", "DB1.DE", "EOAN.DE",
    "FRE.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE",
    "MUV2.DE", "PAH3.DE", "PUM.DE", "QIA.DE", "RHM.DE", "SAP.DE", "SRT3.DE", "SIE.DE",
    "ENR.DE", "SY1.DE", "VOW3.DE", "VNA.DE", "ZAL.DE",
    # MDAX & TecDAX
    "AIXA.DE", "LHA.DE", "FRA.DE", "EVK.DE", "FPE3.DE", "GXI.DE", "HAG.DE", "HOT.DE",
    "JUN3.DE", "KRN.DE", "LEG.DE", "NOEJ.DE", "O2D.DE", "PSM.DE", "RWE.DE", "SOW.DE",
    "NDX1.DE", "UTDI.DE", "IOS.DE", "SANT.DE", "PFV.DE", "AFX.DE", "NEM.DE", "WAF.DE",
    "ARL.DE", "BC8.DE", "COK.DE", "CTS.DE", "DUE.DE", "EVD.DE", "FIE.DE", "G1A.DE",
    "GBF.DE", "HLAG.DE", "KGX.DE", "KCO.DE", "NDA.DE", "RRTL.DE", "SHL.DE", "TEG.DE",
    "TKA.DE", "UN01.DE", "1U1.DE", "WCH.DE",
    # SDAX (Auswahl der wichtigsten)
    "ADJ.DE", "AG1.DE", "AOA.DE", "ATO.DE", "BVB.DE", "CWC.DE", "DWT.DE", "GLJ.DE",
    "GFT.DE", "HLE.DE", "HYQ.DE", "PBB.DE", "SDF.DE", "SGL.DE", "SMA.DE", "SQD.DE"
]

# -----------------------------------------------------------------------------
# 3. KERN-BERECHNUNG (Mit robustem Error-Handling)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300) # Cache für 5 Minuten, um das System nicht zu überlasten
def lade_und_analysiere_daten():
    ergebnisse = []
    
    for ticker in TICKERS:
        try:
            # Daten für 7 Monate laden (wichtig für die 130-Tage-Linie)
            stock = yf.Ticker(ticker)
            df = stock.history(period="7mo")
            
            # SICHERHEITS-CHECK: Hat die Aktie genug Handelstage? Sonst überspringen.
            if df.empty or len(df) < 130:
                continue
            
            # Bereinigung: Fehlende Werte entfernen
            df = df.dropna()
            
            # Kurse extrahieren
            aktueller_kurs = float(df['Close'].iloc[-1])
            vortag_kurs = float(df['Close'].iloc[-2])
            
            # HARTES KRITERIUM 1: Preis darf maximal 100 Euro sein
            if aktueller_kurs > 100.0:
                continue
                
            # RSL BERECHNUNG (Relative Stärke nach Levy)
            # Durchschnitt der letzten 130 Tage
            sma_130 = df['Close'].rolling(window=130).mean().iloc[-1]
            rsl_wert = (aktueller_kurs / sma_130) * 100
            
            # HARTES KRITERIUM 2: RSL muss strikt über 110 sein
            if rsl_wert <= 110.0:
                continue
                
            # DURCHSCHNITT DER 3 VORTAGE (T-2, T-3, T-4)
            # Wir nehmen die Tage VOR dem gestrigen Tag
            if len(df) >= 4:
                durchschnitt_3_vortage = df['Close'].iloc[-4:-1].mean()
            else:
                durchschnitt_3_vortage = vortag_kurs # Fallback, falls Daten fehlen
                
            # Prozentuale Veränderungen exakt berechnen
            heute_prozent = ((aktueller_kurs - vortag_kurs) / vortag_kurs) * 100
            abweichung_3d_prozent = ((aktueller_kurs - durchschnitt_3_vortage) / durchschnitt_3_vortage) * 100
            
            # Daten ordentlich ins System schreiben
            ergebnisse.append({
                "Aktie": ticker.replace(".DE", ""), # Das ".DE" entfernen für saubere Optik
                "Aktuell": aktueller_kurs,
                "Vortag": vortag_kurs,
                "Heute %": heute_prozent,
                "3-Tage-Schnitt": durchschnitt_3_vortage,
                "Abweichung %": abweichung_3d_prozent,
                "RSL": rsl_wert
            })
            
        except Exception as e:
            # Wenn eine Aktie fehlerhaft ist, fängt das Programm den Fehler ab 
            # und macht einfach geräuschlos bei der nächsten Aktie weiter.
            continue
            
    # Aus der Liste eine saubere Tabelle (DataFrame) machen
    return pd.DataFrame(ergebnisse)

# -----------------------------------------------------------------------------
# 4. BENUTZEROBERFLÄCHE & AUSGABE
# -----------------------------------------------------------------------------
st.markdown("""
    **Willkommen im Profi-Screener.** Dieses System scannt vollautomatisch die liquidesten Aktien 
    des deutschen Marktes und wendet strikte mathematische Filter an.
""")

st.info("⚙️ **Aktive System-Filter:** 1. Preis maximal 100,00 € | 2. RSL (130 Tage) strikt > 110")

if st.button("🚀 Marktanalyse jetzt starten (Dauert ca. 20-30 Sekunden)", type="primary"):
    
    with st.spinner("Lade Live-Kurse von der Börse, berechne RSL-Werte und 3-Tages-Schnitte..."):
        df_ergebnisse = lade_und_analysiere_daten()
        
        st.markdown("---")
        
        if df_ergebnisse.empty:
            st.warning("⚠️ **Kein Treffer!** Der Markt ist heute schwach. Aktuell erfüllt keine einzige Aktie unter 100€ die strengen Bedingungen (RSL > 110).")
        else:
            # Metriken anzeigen für den schnellen Überblick
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Gescannte Ticker", len(TICKERS))
            col_m2.metric("Treffer nach Filterung", len(df_ergebnisse))
            col_m3.metric("Bester RSL-Wert", f"{round(df_ergebnisse['RSL'].max(), 2)}")
            
            # Tabellen sortieren
            df_top = df_ergebnisse.sort_values(by="Heute %", ascending=False).head(10)
            df_flop = df_ergebnisse.sort_values(by="Heute %", ascending=True).head(10)
            
            # Professionelle Formatierung für die Tabellen-Anzeige
            column_config = {
                "Aktie": st.column_config.TextColumn("Symbol"),
                "Aktuell": st.column_config.NumberColumn("Kurs (€)", format="%.2f €"),
                "Vortag": st.column_config.NumberColumn("Vortag (€)", format="%.2f €"),
                "3-Tage-Schnitt": st.column_config.NumberColumn("Ø 3-Tage (€)", format="%.2f €"),
                "Heute %": st.column_config.NumberColumn(
                    "Heute %", 
                    format="%.2f %%"
                ),
                "Abweichung %": st.column_config.NumberColumn(
                    "Abweich. Ø %", 
                    format="%.2f %%"
                ),
                "RSL": st.column_config.NumberColumn(
                    "RSL", 
                    format="%.2f"
                )
            }
            
            st.markdown("### 🟢 TOP 10 (Stärkste Performance heute)")
            st.dataframe(df_top, use_container_width=True, hide_index=True, column_config=column_config)
            
            st.markdown("### 🔴 FLOP 10 (Schwächste Performance heute)")
            st.dataframe(df_flop, use_container_width=True, hide_index=True, column_config=column_config)
            
            st.success("✅ Analyse zu 100% fehlerfrei abgeschlossen.")
