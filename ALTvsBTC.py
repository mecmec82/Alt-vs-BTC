import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import ccxt
import matplotlib.pyplot as plt
import seaborn as sns

def get_data_ccxt(exchange, symbol, timeframe, start, end):
    try:
        data = exchange.fetch_ohlcv(symbol, timeframe, since=start, limit=1000)
        df = pd.DataFrame(data, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
        df['Date'] = pd.to_datetime(df['Date'], unit='ms')
        df.set_index('Date', inplace=True)
        return df
    except Exception as e:
        st.write(f"Failed to retrieve data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_data(assets, start, end):
    exchange = ccxt.coinbase()
    btc_data = get_data_ccxt(exchange, "BTC/USD", '2h', start, end)['Close']
    close_data = pd.DataFrame()

    for asset in assets:
        asset_name = asset.split("/")[0]
        data = get_data_ccxt(exchange, asset, '2h', start, end)
        if not data.empty:
            close_data[asset_name] = data['Close']
        else:
            st.write(f"Failed to retrieve data for {asset}")

    close_data = close_data.div(btc_data, axis=0)
    return close_data

def calculate_sma(data, window):
    return data.rolling(window=window).mean()

def plot_data(close_data, sma1, sma2, num_points):
    close_data = close_data[-num_points:]
    sma1_data = calculate_sma(close_data, SMA1)[-num_points:]
    sma2_data = calculate_sma(close_data, SMA2)[-num_points:]

    num_assets = len(close_data.columns)
    fig, axes = plt.subplots(num_assets, figsize=(10, 20), sharex=True)
    fig.subplots_adjust(wspace=0.3, hspace=0)
    fig.suptitle('Altcoins vs BTC')

    for index, asset in enumerate(close_data.columns):
        x = sma1_data.index
        y1 = sma1_data[asset]
        y2 = sma2_data[asset]

        ax = sns.lineplot(ax=axes[index], data=sma1_data, x='Date', y=asset, color="blue")
        ax = sns.lineplot(ax=axes[index], data=sma2_data, x='Date', y=asset, color="orange")
        ax.fill_between(x, y1, y2, where=(y1 > y2), color='green', alpha=0.2, interpolate=True)
        ax.fill_between(x, y1, y2, where=(y1 <= y2), color='red', alpha=0.2, interpolate=True)

        if y1.iloc[-1] > y2.iloc[-1]:
            ax.yaxis.label.set_color('green')
            ax.tick_params(axis='y', colors='green')
            ax.spines['left'].set_color('green')

    fig.autofmt_xdate(rotation=90)
    st.pyplot(fig, use_container_width=False)

st.write('Fetching data...')

now = datetime.now()
end = (now - timedelta(hours=0.5)).timestamp() * 1000
start = (now - timedelta(hours=50)).timestamp() * 1000

SMA1 = 10
SMA2 = 30
NumPoints = 300

assets = ['ETH/USD', 'SOL/USD', 'SUI/USD', 'AVAX/USD', 'APT/USD', 'NEAR/USD', 'INJ/USD',
          'STX/USD', 'DOGE/USD', 'IMX/USD', 'RNDR/USD', 'FET/USD', 'SUPER/USD', 'HNT/USD',
          'SEI/USD']

close_data = fetch_data(assets, start, end)
plot_data(close_data, SMA1, SMA2, NumPoints)
