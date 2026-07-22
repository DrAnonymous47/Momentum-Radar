import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np
import time
import os
import shutil
import zipfile

st.markdown(
  "<style>.css-1qwj096{--bs-breadcrumb-divider: none;}</style>",
  unsafe_allow_html=True
)

DEUTSCHE_AKTIEN = {
  "SAP.DE": {"name": "SAP AG", "segment": "DAX"},
  "SIE.DE": {"name": "SIEMENS AG", "segment": "DAX"},
  "RHM.DE": {"name": "Robert Bosch GmbH", "segment": "DAX"},
  "MBG.DE": {"name": "Merck KGaA", "segment": "DAX"},
  "ALV.DE": {"name": "ALLLIANZ SE", "segment": "DAX"},
  "BMW.DE": {"name": "Bayerische Motorenwerke AG", "segment": "DAX"},
  # MDAX & TecDAX
  "AIXA.DE": {"name": "Adidas AG", "segment": "MDAX"},
  "HAG.DE": {"name": "Hannover Rück SE", "segment": "TecDAX"},
  "NEM.DE": {"name": "NEC TECNALIA Research & Innovation", "segment": "TecDAX"},
  "LHA.DE": {"name": "Linde AG", "segment": "TecDAX"},
  "TKA.DE": {"name": "Technische Kunststoff-Weberei GmbH & Co. KG", "segment": "TecDAX"},
  # SDAX & NEBENWERTE
  "DEQ.DE": {"name": "Deutsche EuroShop AG", "segment": "SDAX"},
  "HDD.DE": {"name": "Deutz AG", "segment": "NEBENWERTE"},
  "CEC.DE": {"name": "Ceconomy SE", "segment": "NEBENWERTE"},
  "VAC.DE": {"name": "Viacom International Inc.", "segment": "NEBENWERTE"},
}

@st.cache_data(ttl=60 * 60)
def load_stock_data(ticker):
  start = datetime.now() - timedelta(days=210)
  end = datetime.now()
  df = yf.download(ticker, start=start, end=end)
  df['Close'] = df['Close'].apply(pd.to_numeric)
  return df[['Close']]

def calculate_stats(df):
  current_day = df.iloc[-1]
  prev_day = df.iloc[-2]
  daily_change_percentage = ((current_day - prev_day) / prev_day) * 100

  three_days_avg = df.rolling(window=3).mean()
  rsl = (current_day / three_days_avg[-1]) * 100

  return daily_change_percentage, rsl

st.sidebar.header("Filter")
max_price = st.slider("Maximum Price", min_value=0, step=1)
top_percentage = st.slider("Top %", min_value=1, max_value=5)
flop_percentage = st.slider("Flop %", min_value=1, max_value=5)
search_text = st.sidebar.text_input("Search")

st.write("# German Stock Radar - Real-time Aktien Scanner für XETRA")
st.write(f"[Filtered stocks: {len(DEUTSCHE_AKTIEN)}]")

stock_data = {}
watched = set()

for ticker, _ in DEUTSCHE_AKTIEN.items():
  stock_data[ticker] = load_stock_data(ticker)
  daily_change_percentage, rsl = calculate_stats(stock_data[ticker])
  st.write(f"### {DEUTSCHE_AKTIEN[ticker]['name']} ({DEUTSCHE_AKTIEN[ticker]['segment']})")
  st.write(f"Tagesveränderung: {daily_change_percentage:.2f}%")
  st.write(f"RSL: {rsl:.2f}% 🟢/🔴")

# KPI Cards, Tables and Interactive Chart go here...

# Filtered stocks based on search text, max price, top_percentage, flop_percentage
filtered_stocks = [stock for stock in DEUTSCHE_AKTIEN if search_text is None or stock[0] == search_text and
                  stock_data[stock[0]]['Close'].iloc[-1] <= max_price and
                  daily_change_percentage > -flop_percentage * 0.01 and
                  daily_change_percentage >= top_percentage * 0.01]

# Sort filtered stocks by daily change percentage in descending order
sorted_stocks = sorted(filtered_stocks, key=lambda x: -daily_change_percentage)

st.write("## Top Gewinner")
for stock in sorted_stocks[:10]:
  st.write(f"### {stock[0]} ({stock[1]['segment']})")
  st.write(f"Tagesveränderung: {daily_change_percentage:.2f}%")
  st.write(f"RSL: {rsl:.2f}% 🟢/🔴")

st.write("## Flop Verlierer")
for stock in reversed(sorted(filtered_stocks, key=lambda x: x[0], reverse=True)[:10]):
  st.write(f"### {stock[0]} ({stock[1]['segment']})")
  st.write(f"Tagesveränderung: {daily_change_percentage:.2f}%")
  st.write(f"RSL: {rsl:.2f}% 🟢/🔴")

# Interactive chart for a selected stock
selected_stock = st.selectbox("Auswählen", [stock[0] for stock in sorted_stocks])
fig = go.Figure()
fig.add_trace(go.Candlestick(x=stock_data[selected_stock].index,
                             open=stock_data[selected_stock]['Open'],
                             high=stock_data[selected_stock]['High'],
                             low=stock_data[selected_stock]['Low'],
                             close=stock_data[selected_stock]['Close']))
fig.add_trace(go.Scatter(y=[three_days_avg[-1]], x=stock_data[selected_stock].index, mode='lines', name="130-Tage SMA"))
fig.update_layout(title={'text': f"{selected_stock} ({DEUTSCHE_AKTIEN[selected_stock]['segment']})",
                        'y': 0.95},
                 xaxis_rangeslider_visible=False)
st.plotly_chart(fig)

# Session Watchlist and CSV Export Button go here...

# Save the session watchlist to a temporary file
def save_watchlist():
  temp_folder = get_scratchpad_folder()
  os.makedirs(temp_folder, exist_ok=True)
  temp_file = f"{temp_folder}/watchlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
  with open(temp_file, 'w', newline='') as csvfile:
      fieldnames = ["Ticker", "Name", "Segment"]
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
      writer.writeheader()
      for stock in watched:
          writer.writerow({"Ticker": stock[0], "Name": DEUTSCHE_AKTIEN[stock[0]]["name"], "Segment": DEUTSCHE_AKTIEN[stock[0]]["segment"]})
  return temp_file

# Load the session watchlist from a temporary file
def load_watchlist(filename=None):
  if filename is None:
      load_file_attachment("watchlist.csv")  # If attachment is missing, try to load it from the workspace.
  elif not os.path.isfile(filename):
      raise FileNotFoundError(f"The watchlist file '{filename}' does not exist.")
  with open(filename, 'r', newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      watched_stocks = [(stock["Ticker"], DEUTSCHE_AKTIEN[stock["Ticker"]]) for stock in reader]
  return watched_stocks

# CSV Export Button functionality
CSV_EXPORT_BUTTON_STYLE = """
<style>
.stButton > .css-184z95q {
background: #2c3e50; /* W3Schools Blue */
border: none;
color: white;
padding: 15px 32px;
text-align: center;
text-decoration: none;
display: inline-block;
font-size: 16px;
margin: 4px 2px;
cursor: pointer;
}
.stButton > .css-184z95q:hover {
background: #3eaccc; /* W3Schools Blue */
}
</style>"""
CSV_EXPORT_BUTTON = f'<button id="csvExportButton" class="stButton" type="button" onclick="downloadCSV(\'{save_watchlist()}\')">Download Watchlist (.csv)</button>'

# Add the CSV Export Button to the app UI
st.markdown(CSV_EXPORT_BUTTON_STYLE, unsafe_allow_html=True)
st.write(CSV_EXPORT_BUTTON)

# Initialize session watchlist
watchlist = load_watchlist()

# Session Watchlist functionality
def add_to_watchlist(ticker):
  global watched
  if ticker not in watched:
      watched.add(ticker)
      st.session_state.watched = list(watched)
      save_watchlist()

def remove_from_watchlist(ticker):
  global watched
  if ticker in watched:
      watched.remove(ticker)
      st.session_state.watched = list(watched)
      save_watchlist()

# Function to download the watchlist as CSV
def downloadCSV(filename):
  with open(filename, 'r', encoding='utf-8') as csvfile:
      data = csvfile.read()
  zip_memory = zipfile.ZipFile(None, mode='w', compression=zipfile.ZIP_DEFLATED)
  zip_memory.writestr('watchlist.csv', data.encode())
  zip_memory.close()

  # Create a temporary directory for the downloaded file
  temp_folder = get_scratchpad_folder()
  os.makedirs(temp_folder, exist_ok=True)
  temp_file = f"{temp_folder}/watchlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

  # Write the downloaded file to the temporary zip archive
  with open(temp_file, 'wb') as zipped_file:
      zip_memory.open(temp_file)
      shutil.copyfileobj(zip_memory, zipped_file)
      zip_memory.close()

  # Open a new tab to download the file
  st.write("Download in progress...", unsafe_allow_html=True)
  st.markdown(f'<a href="{temp_file}" download>Download Watchlist (.zip)</a>', unsafe_allow_html=True)
