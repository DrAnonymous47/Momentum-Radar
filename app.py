import streamlit as st
import yfinance as yf
import pandas as pd
from plotly.graph_objects import Candlestick, Layout
import datetime
import os

st.markdown(f"<style>{open('style.css', 'r').read()}</style>", unsafe_allow_html=True)

# Define the German stocks to be monitored
DEUTSCHE_AKTIEN = {
    "SAP": "DAX",
    "SIE": "DAX",
    "MBG": "DAX",
    "DTE": "DAX",
    "ALV": "DAX",
    "RHM": "MDAX",
    "BMW": "DAX",
    "LHA": "MDAX",
    "TKA": "MDAX",
    "NEM": "MDAX",
    "AIX": "TEC",
    "HAG": "MDAX",
    "DEQ": "SDAX",
    "HDD": "SDAX",
    "CEC": "OTC",
    "VAC": "SDAX",
    "MED": "SDAX",
    "HAB": "SDAX",
    "BVB": "OTC",
    "1U1": "OTC",
    "LEI": "SDAX",
    "MLP": "OTC",
}

# Load stock data for the last 7 months using yfinance and Streamlit's caching decorator
@st.cache_data(ttl=60*60*24*7)
def get_stock_data():
    df = pd.DataFrame()
    for ticker, segment in DEUTSCHE_AKTIEN.items():
        stock = yf.Ticker(ticker + '.DE')
        stock_info = stock.info
        history = stock.history(period="7mo")
        df[ticker] = history['Close']
    return df

# Calculate daily change percentage and RSL (130-day SMA)
def calculate_statistics(df):
    df['Daily Change %'] = (df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100
    df['RSL'] = (df['Close'] / df['Close'].rolling(window=130).mean()) * 100

# Main function
def main():
    st.set_page_config(layout="wide")

    # Load stock data and calculate statistics
    stock_data = get_stock_data()
    calculate_statistics(stock_data)

    # Sidebar: Filter by maximum price, top/flop percentages, and search text
    col1, col2 = st.beta_columns(2)
    max_price = col1.slider("Max Price", min_value=0, max_value=10000, value=0)
    top_percentage = col1.slider("Top %", min_value=0, max_value=5, value=2.5)
    flop_percentage = col1.slider("Flop %", min_value=0, max_value=5, value=2.5)
    search_text = col2.text_input("Search")

    # Filter the stock data based on user's preferences
    filtered_data = stock_data[stock_data['Close'] <= max_price] \
                         .loc[stock_data['Daily Change %'] >= top_percentage] \
                         .loc[stock_data['Daily Change %'] <= -flop_percentage] \
                         .query(f"index - {len(DEUTSCHE_AKTIEN)} <= index < len(Close)") \
                         .loc[stock_data.columns[:-1]] \
                         .rename(columns=lambda x: DEUTSCHE_AKTIEN[x]) \
                         .reset_index(drop=True)

    # KPI metrics for the scanned stocks, winners, and losers
    st.markdown("**Scanned Stocks:** " + ", ".join(filtered_data.columns[:-1]))
    st.metric("Winners", len(filtered_data[filtered_data['Daily Change %'] >= top_percentage]))
    st.metric("Losers", len(filtered_data[filtered_data['Daily Change %'] <= -flop_percentage]))

    # Tables for winners and losers
    st.dataframe(filtered_data[filtered_data['Daily Change %'] >= top_percentage])
    st.dataframe(filtered_data[filtered_data['Daily Change %'] <= -flop_percentage])

    # Interactive chart for a selected stock
    selected_stock = st.selectbox("Select Stock", options=list(DEUTSCHE_AKTIEN.keys()))
    fig = make_chart(selected_stock, filtered_data)
    st.plotly_chart(fig)

    # Session watchlist: Save and load watched stocks as CSV or ZIP files
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = set()

    if st.button("Save Watchlist"):
        save_as(st.session_state.watchlist, 'watchlist.csv')

    if os.path.exists('watchlist.csv'):
        watched_stocks = load_watchlist('watchlist.csv')
        st.session_state.watchlist |= watched_stocks

    for stock in filtered_data.columns[:-1]:
        if stock in st.session_state.watchlist:
            st.markdown(f'<b>{stock}</b>', unsafe_allow_html=True)

    # Download button for the watchlist data as CSV or ZIP
    if st.button("Download Watchlist Data"):
        download_csv_or_zip(filtered_data, 'watchlist')

def make_chart(ticker, filtered_data):
    fig = Layout()
    candlestick_trace = Candlestick(x=filtered_data.index,
                                     open=filtered_data[ticker]['Open'],
                                     high=filtered_data[ticker]['High'],
                                     low=filtered_data[ticker]['Low'],
                                     close=filtered_data[ticker]['Close'])
    fig.add_trace(candlestick_trace)
    fig.update_xaxes(rangeslider_visible=False,
                     range_year=[pd.to_datetime("2023-01-01").date(), pd.to_datetime("2023-12-31").date()])
    fig.add_trace({'x': filtered_data.index, 'y': filtered_data[ticker]['RSL'],
                   'line': {'color': "gray", 'width': 1}})
    fig.update_layout(showlegend=False)
    return fig

def save_as(watchlist, filename):
    df = pd.DataFrame({'Stocks': list(watchlist)})
    if filename.endswith('.csv'):
        df.to_csv(filename)
    elif filename.endswith('.zip'):
        with zipfile.ZipFile(filename, 'w') as zf:
            for stock in watchlist:
                zf.write(f"{stock}.csv", stream=open(f"{stock}.csv", "rb"))

def load_watchlist(filename):
    watchlist = set()
    with open(filename, 'r') as f:
        for line in f:
            watchlist.add(line.strip())
    return watchlist

def download_csv_or_zip(df, name):
    if df.shape[0] > 1000:
        zip_name = f"{name}_data.zip"
        with zipfile.ZipFile(zip_name, 'w') as zf:
            for col in df.columns[:-1]:
                zf.write(pd.DataFrame({col: [row[col] for row in df.itertuples()]}).to_csv(index=False),
                         f"{col}.csv")
        st.download_file(zip_name, "data.zip", "application/zip")
    else:
        csv_name = f"{name}_data.csv"
        df.to_csv(csv_name)
        st.download_file(csv_name, f"{name}_data.csv", "text/csv")

if __name__ == "__main__":
    main()

