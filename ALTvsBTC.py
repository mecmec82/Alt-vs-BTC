import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import ccxt
import matplotlib.pyplot as plt
import seaborn as sns

def getDataCCXT(ID, start, end):
    exchange = ccxt.coinbase()
    data = exchange.fetch_ohlcv(ID, '2h')
    data = pd.DataFrame(data)
    data.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    data = data.sort_values(by=['Date'], ascending=True)
    data['Date'] = pd.to_datetime(data['Date'], unit='ms')
    data.set_index('Date', drop=False, inplace=True)
    return data

# Sidebar controls
st.sidebar.header('Settings')
SMA1 = st.sidebar.slider('SMA1', min_value=1, max_value=50, value=10)
SMA2 = st.sidebar.slider('SMA2', min_value=1, max_value=50, value=30)
NumPoints = st.sidebar.slider('Number of Points', min_value=50, max_value=500, value=300)
assets = st.sidebar.multiselect('Select Assets', 
                                ['ETH/USD', 'SOL/USD', 'SUI/USD', 'AVAX/USD', 'APT/USD', 'NEAR/USD', 'INJ/USD',
                                 'STX/USD', 'DOGE/USD', 'IMX/USD', 'RNDR/USD', 'FET/USD', 'SUPER/USD', 'HNT/USD',
                                 'SEI/USD'], 
                                default=['ETH/USD', 'SOL/USD', 'SUI/USD', 'AVAX/USD'])

st.write('Fetching data...')

data = np.nan

# Set up start and finish window
now = datetime.now()
end = (now - timedelta(hours=0.5)).strftime("%Y-%m-%d %H:%M:%S")
start = (now - timedelta(hours=50)).strftime("%Y-%m-%d %H:%M:%S")

# Get BTC data
try:
    btcData = getDataCCXT("BTC/USD", start, end)['Close']
except:
    st.write("Failed to retrieve BTC data")

# Get alt data
closeData = pd.DataFrame()
for asset in assets:
    assetName = str(asset).split("/")[0]
    try:
        closeData[assetName] = getDataCCXT(asset, start, end)['Close']
    except:
        st.write("Failed to retrieve data for ticker: ", asset)

# Reference to BTC
closeData = closeData.div(btcData, axis=0)

# Create SMA dataframe
rollingAverageData1 = closeData.rolling(window=SMA1).mean()
rollingAverageData2 = closeData.rolling(window=SMA2).mean()

# Trim to desired timeframe
closeData = closeData[-NumPoints:]
rollingAverageData1 = rollingAverageData1[-NumPoints:]
rollingAverageData2 = rollingAverageData2[-NumPoints:]

# Plots
numAssets = len(closeData.columns)
numRows = numAssets

fig, axes = plt.subplots(numRows, figsize=(3, 20), sharex=True)

fig.subplots_adjust(wspace=0.3, hspace=0)
fig.suptitle('Altcoins vs BTC')

for index, asset in enumerate(closeData.columns):
    x = rollingAverageData1.index
    y1 = rollingAverageData1[asset]
    y2 = rollingAverageData2[asset]

    ax = sns.lineplot(ax=axes[index], data=rollingAverageData1, x='Date', y=asset, color="blue")
    ax = sns.lineplot(ax=axes[index], data=rollingAverageData2, x='Date', y=asset, color="orange")
    ax.fill_between(x, y1, y2, where=(y1 > y2), color='green', alpha=0.2, interpolate=True)
    ax.fill_between(x, y1, y2, where=(y1 <= y2), color='red', alpha=0.2, interpolate=True)

    if rollingAverageData1[asset][-1] > rollingAverageData2[asset][-1]:
        ax.yaxis.label.set_color('green')
        ax.tick_params(axis='y', colors='green')
        ax.spines['left'].set_color('green')

fig.autofmt_xdate(rotation=90)

# Displaying in Streamlit
st.pyplot(fig, use_container_width=False)
