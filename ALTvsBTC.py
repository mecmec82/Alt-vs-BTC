import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import ccxt
import seaborn as sns
import matplotlib.pyplot as plt

def getDataCCXT(ID, start, end):
    exchange = ccxt.binance()
    data = exchange.fetch_ohlcv(ID, '1h')
    data = pd.DataFrame(data)
    data.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    data = data.sort_values(by=['Date'], ascending=True)
    data['Date'] = pd.to_datetime(data['Date'], unit='ms')
    data.set_index('Date', drop=False, inplace=True)
    return data

# Set up start and finish window
now = datetime.now()
end = (now - timedelta(hours=0.5))
start = (end - timedelta(hours=50))
end = end.strftime("%Y-%m-%d %H:%M:%S")
start = start.strftime("%Y-%m-%d %H:%M:%S")

# Set parameters
SMA1 = 20
NumPoints = 168

# Altcoin list
assets = ['ETH/BTC', 'SOL/BTC', 'SUI/BTC', 'AVAX/BTC', 'APT/BTC', 'NEAR/BTC', 'INJ/BTC',
          'STX/BTC', 'DOGE/BTC', 'IMX/BTC', 'RNDR/BTC', 'FET/BTC', 'SUPER/BTC', 'HNT/BTC',
          'SEI/BTC']

# Get alt data
closeData = pd.DataFrame()
st.write("Fetching data...")
for asset in assets:
    try:
        closeData[asset] = getDataCCXT(asset, start, end)['Close']
    except:
        st.write("Failed to retrieve data for ticker: ", asset)

st.write('Running...')

# Create SMA dataframe
rollingAverageData = closeData.rolling(window=SMA1).mean()

# Trim to desired timeframe
closeData = closeData[-NumPoints:]
rollingAverageData = rollingAverageData[-NumPoints:]

# Plots
numAssets = len(closeData.columns)
numRows = int(numAssets / 2) + 1

fig, axes = plt.subplots(numRows, 2, figsize=(10, 10), sharex=True)
fig.subplots_adjust(wspace=0.3, hspace=0)
fig.suptitle('Altcoins vs BTC')

for index, asset in enumerate(closeData.columns):
    if closeData[asset].iloc[-1] > rollingAverageData[asset].iloc[0]:
        lineColor = 'green'
    else:
        lineColor = 'red'
    if index < numRows:
        ax = sns.lineplot(ax=axes[index, 0], data=closeData, x='Date', y=asset, color=lineColor)
        ax = sns.lineplot(ax=axes[index, 0], data=rollingAverageData, x='Date', y=asset, color="blue")
    else:
        ax1 = sns.lineplot(ax=axes[index - numRows, 1], data=closeData, x='Date', y=asset, color=lineColor)
        ax1 = sns.lineplot(ax=axes[index - numRows, 1], data=rollingAverageData, x='Date', y=asset, color="blue")

fig.autofmt_xdate(rotation=90)

st.pyplot(fig)
