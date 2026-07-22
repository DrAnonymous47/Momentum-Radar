import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# =============================================================================
# 1. SEITEN-KONFIGURATION & LAYOUT
# =============================================================================
# Wir nutzen das breite Layout, damit die Tabelle wie auf deinem Zettel 
# komplett auf den Bildschirm passt.
st.set_page_config(
    page_title="Index Radar Pro", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# 2. UMFASSENDE AKTIEN-DATENBANK (DAX, MDAX, SDAX, TecDAX)
# =============================================================================
# Hier sind die wichtigsten Werte aus den deutschen Indizes sauber aufgelistet.
# Das Programm iteriert später durch diese Liste.
AKTIEN_DATENBANK = {
    # --- DAX WERKTE ---
    "ADS.DE": "Adidas",
    "ALV.DE": "Allianz",
    "BAS.DE": "BASF",
    "BAYN.DE": "Bayer",
    "BEI.DE": "Beiersdorf",
    "BMW.DE": "BMW",
    "BNR.DE": "Brenntag",
    "CBK.DE": "Commerzbank",
    "CON.DE": "Continental",
    "1COV.DE": "Covestro",
    "DTG.DE": "Daimler Truck",
    "DBK.DE": "Deutsche Bank",
    "DB1.DE": "Deutsche Börse",
    "DPW.DE": "DHL Group",
    "DTE.DE": "Deutsche Telekom",
    "EOAN.DE": "E.ON",
    "FRE.DE": "Fresenius",
    "HNR1.DE": "Hannover Rück",
    "HEI.DE": "Heidelberg Materials",
    "HEN3.DE": "Henkel",
    "IFX.DE": "Infineon",
    "MBG.DE": "Mercedes-Benz",
    "MRK.DE": "Merck",
    "MTX.DE": "MTU Aero",
    "MUV2.DE": "Munich Re",
    "PAH3.DE": "Porsche",
    "PUM.DE": "Puma",
    "QIA.DE": "Qiagen",
    "RHM.DE": "Rheinmetall",
    "RWE.DE": "RWE",
    "SAP.DE": "SAP",
    "SRT3.DE": "Sartorius",
    "SIE.DE": "Siemens",
    "ENR.DE": "Siemens Energy",
    "SHL.DE": "Siemens Healthineers",
    "SY1.DE": "Symrise",
    "VOW3.DE": "Volkswagen",
    "VNA.DE": "Vonovia",
    "ZAL.DE": "Zalando",

    # --- MDAX / TECDAX / SDAX HIGHLIGHTS (Wie auf deinem Zettel gewünscht) ---
    "AIXA.DE": "Aixtron",
    "LHA.DE": "Lufthansa",
    "FRA.DE": "Fraport",
    "EVK.DE": "Evonik",
    "FPE3.DE": "Fuchs",
    "GXI.DE": "Gerresheimer",
    "HAG.DE": "Hensoldt",
    "HOT.DE": "Hochtief",
    "JUN3.DE": "Jungheinrich",
    "KRN.DE": "Krones",
    "LEG.DE": "LEG Immobilien",
    "NOEJ.DE": "Norma Group",
    "O2D.DE": "Telefonica",
    "PSM.DE": "ProSiebenSat.1",
    "SOW.DE": "Software AG",
    "NDX1.DE": "Nordex", # Extra aus deiner Skizze
    "UTDI.DE": "United Internet",
    "IOS.DE": "IONOS",
    "SANT.DE": "Santander",
    "AFX.DE": "Carl Zeiss Meditec",
    "NEM.DE": "Nemetschek",
    "WAF.DE": "Siltronic",
    "ARL.DE": "Aareal Bank",
    "COK.DE": "Cancom",
    "CTS.DE": "CTS Eventim",
    "DUE.DE": "Dürr",
    "EVD.DE": "CTS Eventim",
    "FIE.DE": "Fielmann",
    "G1A.DE": "GEA Group",
    "HLAG.DE": "Hapag-Lloyd",
    "KGX.DE": "KION Group",
    "KCO.DE": "Klöckner & Co",
    "NDA.DE": "Aurubis",
    "RRTL.DE": "RTL Group",
    "TEG.DE": "TAG Immobilien",
    "TKA.DE": "thyssenkrupp",
    "1U1.DE": "1&1",
    "WCH.DE": "Wacker Chemie",
    "SMA.DE": "SMA Solar", # Extra aus deiner Skizze
    "S92.DE": "SMA Solar Tech"
}

# =============================================================================
# 3. KERNLOGIK: BERECHNUNG DER DATEN
# =============================================================================
@st.cache_data(ttl=600) # Cache speichert Daten für 10 Minuten, um Ladezeiten zu sparen
def lade_und_berechne_markt_daten():
    """
    Diese Funktion lädt die Daten aller Aktien herunter und berechnet exakt
    die Spalten, die du auf deinem Zettel gezeichnet hast.
    """
    erfolgreiche_treffer = []
    
    for ticker, name in AKTIEN_DATENBANK.items():
        try:
            # 1. Daten von Yahoo Finance laden (7 Monate für die 130-Tage-Linie)
            stock = yf.Ticker(ticker)
            df = stock.history(period="7mo")
            
            # 2. Fehler abfangen: Hat die Aktie genug Handelstage?
            if df.empty or len(df) < 130:
                continue
                
            # NaNs (leere Felder) entfernen für saubere Mathematik
            df = df.dropna()
            
            # 3. Variablen gemäß deiner Skizze berechnen
            ist_kurs = float(df['Close'].iloc[-1])
            schluss_vortag = float(df['Close'].iloc[-2])
            
            # Abweichung zum Vortag berechnen (in Prozent)
            abw_vortag_prozent = ((ist_kurs - schluss_vortag) / schluss_vortag) * 100
            
            # Durchschnitt der 3 Tage (T-2, T-3, T-4)
            if len(df) >= 4:
                durchschnitt_3_tage = df['Close'].iloc[-4:-1].mean()
            else:
                durchschnitt_3_tage = schluss_vortag
                
            # Abweichung zum 3-Tage-Schnitt (in Prozent)
            abw_3_tage_prozent = ((ist_kurs - durchschnitt_3_tage) / durchschnitt_3_tage) * 100
            
            # RSL Wert berechnen (Relative Stärke nach Levy - 130 Tage)
            sma_130 = df['Close'].rolling(window=130).mean().iloc[-1]
            rsl_wert = (ist_kurs / sma_130) * 100
            
            # 4. FILTER ANWENDEN
            # Wir speichern den Wert NUR, wenn alle Bedingungen erfüllt sind.
            # Bedingung A: Preis unter 100 Euro
            if ist_kurs > 100.0:
                continue
                
            # Bedingung B: +/- 2.5% zum Vortag (wie auf Zettel notiert)
            if not (-2.5 <= abw_vortag_prozent <= 2.5):
                continue
                
            # Bedingung C: RSL muss stark sein (> 110)
            if rsl_wert <= 110.0:
                continue
                
            # 5. Daten exakt nach deiner Tabellenstruktur anordnen
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
            # Falls bei einer Aktie ein Fehler auftritt, leise weitermachen
            continue
            
    return pd.DataFrame(erfolgreiche_treffer)

# =============================================================================
# 4. UI-KOMPONENTEN (Die Benutzeroberfläche aufbauen)
# =============================================================================
def main():
    # Header Bereich
    heute_str = datetime.now().strftime("%d.%m.%Y")
    st.title("📈 Index Radar Pro (DAX, MDAX, SDAX, TecDAX)")
    st.markdown(f"**Stand:** {heute_str} | **Filter:** Preis < 100€ | RSL > 110 | +/- 2.5% zum Vortag")
    st.markdown("---")

    # Start-Knopf
    if st.button("🚀 Marktanalyse ausführen", type="primary"):
        with st.spinner("Lade Live-Börsendaten und berechne Indikatoren..."):
            
            # Die schwere Berechnungsfunktion aufrufen
            df_ergebnis = lade_und_berechne_markt_daten()
            
            # Prüfen ob wir nach dem strengen Filter überhaupt Treffer haben
            if df_ergebnis.empty:
                st.warning("⚠️ Keine Treffer heute! Keine Aktie erfüllt aktuell alle Kriterien (RSL > 110 UND Bewegung +/- 2,5%).")
            else:
                # Top und Flop sortieren (wie auf dem Zettel: Top/Flop 10)
                df_top10 = df_ergebnis.sort_values(by="Abw. Vortag (%)", ascending=False).head(10)
                df_flop10 = df_ergebnis.sort_values(by="Abw. Vortag (%)", ascending=True).head(10)
                
                # -------------------------------------------------------------
                # TABELLEN-KONFIGURATION (Crash-sicheres Design ohne jinja2)
                # -------------------------------------------------------------
                # Wir zwingen Streamlit dazu, die Spalten genau wie in deiner
                # Skizze zu formatieren und benennen.
                spalten_layout = {
                    "Name": st.column_config.TextColumn(
                        "Name", 
                        width="medium"
                    ),
                    "IST Kurs": st.column_config.NumberColumn(
                        "IST Kurs", 
                        format="%.2f €"
                    ),
                    "Schluss Vortag": st.column_config.NumberColumn(
                        "Schluss Vortag", 
                        format="%.2f €"
                    ),
                    "Abw. Vortag (%)": st.column_config.NumberColumn(
                        "Abw. Vortag", 
                        format="%+.2f %%", 
                    ),
                    "Ø 3 Tage": st.column_config.NumberColumn(
                        "Ø 3 Tage", 
                        format="%.2f €"
                    ),
                    "Abw. 3 Tage (%)": st.column_config.NumberColumn(
                        "Abw. 3 Tage", 
                        format="%+.2f %%"
                    ),
                    "RSL": st.column_config.NumberColumn(
                        "RSL", 
                        format="%.0f"
                    )
                }

                # Ausgabe der TOP 10 Tabelle
                st.subheader("🟢 Top 10 (Stärkste im Korridor)")
                st.dataframe(
                    df_top10, 
                    use_container_width=True, 
                    hide_index=False, 
                    column_config=spalten_layout
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Ausgabe der FLOP 10 Tabelle
                st.subheader("🔴 Flop 10 (Schwächste im Korridor)")
                st.dataframe(
                    df_flop10, 
                    use_container_width=True, 
                    hide_index=False, 
                    column_config=spalten_layout
                )

                st.success(f"✅ Analyse erfolgreich. {len(df_ergebnis)} Werte haben die strengen Filter bestanden.")

    # =============================================================================
    # 5. NOTIZBEREICH (Wie unten auf dem Zettel gezeichnet)
    # =============================================================================
    st.markdown("---")
    st.subheader("📝 Notiz / Info:")
    
    # Textarea, in der du während dem Trading Anmerkungen eintragen kannst.
    notiz = st.text_area(
        "Hier kannst du dir wichtige Beobachtungen, Trends oder Auffälligkeiten notieren:",
        height=150,
        placeholder="Beispiel: Telekom heute besonders stark am Nachmittag..."
    )
    
    if st.button("💾 Notiz zwischenspeichern"):
        st.toast("Notiz wurde für diese Sitzung gespeichert!", icon="✅")

# Programm-Einstiegspunkt
if __name__ == "__main__":
    main()
