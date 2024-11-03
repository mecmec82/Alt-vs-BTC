import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import ccxt
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def getDataCCXT(ID, timeframe, start, end):
    exchange = ccxt.coinbase()
    data = exchange.fetch_ohlcv(ID, timeframe)
    data = pd.DataFrame(data)
    data.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    data = data.sort_values(by=['Date'], ascending=True)
    data['Date'] = pd.to_datetime(data['Date'], unit='ms')
    data.set_index('Date', drop=False, inplace=True)
    return data

def fetch_data(timeframe):
    now = datetime.now()
    end = (now - timedelta(hours=0.5)).strftime("%Y-%m-%d %H:%M:%S")
    start = (now - timedelta(hours=50)).strftime("%Y-%m-%d %H:%M:%S")

    # Get BTC data
    try:
        btcData = getDataCCXT("BTC/USD", timeframe, start, end)['Close']
    except:
        st.write("Failed to retrieve BTC data")
        return None

    # Get alt data
    closeData = pd.DataFrame()
    for asset in st.session_state.assets:
        assetName = str(asset).split("/")[0]
        try:
            closeData[assetName] = getDataCCXT(asset, timeframe, start, end)['Close']
        except:
            st.write("Failed to retrieve data for ticker: ", asset)

    # Reference to BTC
    closeData = closeData.div(btcData, axis=0)
    return closeData

def plot_data(closeData, SMA1, SMA2, NumPoints):
    # Create SMA dataframe
    rollingAverageData1 = closeData.rolling(window=SMA1).mean()
    rollingAverageData2 = closeData.rolling(window=SMA2).mean()

    # Trim to desired timeframe
    closeData = closeData[-NumPoints:]
    rollingAverageData1 = rollingAverageData1[-NumPoints:]
    rollingAverageData2 = rollingAverageData2[-NumPoints:]

    # Calculate percentage increase over the time period
    percentage_increase = (closeData.iloc[-1] - closeData.iloc[0]) / closeData.iloc[0] * 100

    # Sort assets by percentage increase
    sorted_assets = percentage_increase.sort_values(ascending=False).index

    # Plots
    numAssets = len(closeData.columns)
    numRows = numAssets

    fig, axes = plt.subplots(numRows, figsize=(10, numRows * 3), sharex=True)

    fig.subplots_adjust(wspace=0.1, hspace=0.5)
    fig.suptitle('Altcoins vs BTC', y=0.92)

    for index, asset in enumerate(sorted_assets):
        x = rollingAverageData1.index
        y1 = rollingAverageData1[asset]
        y2 = rollingAverageData2[asset]

        ax = sns.lineplot(ax=axes[index], data=rollingAverageData1, x='Date', y=asset, color="blue")
        ax = sns.lineplot(ax=axes[index], data=rollingAverageData2, x='Date', y=asset, color="orange")
        ax.fill_between(x, y1, y2, where=(y1 > y2), color='green', alpha=0.2, interpolate=True)
        ax.fill_between(x, y1, y2, where=(y1 <= y2), color='red', alpha=0.2, interpolate=True)

        increase_percentage = percentage_increase[asset]
        if increase_percentage > 0:
            ax.yaxis.label.set_color('green')
            ax.tick_params(axis='y', colors='green')
            ax.spines['left'].set_color('green')
            ax.text(1.02, 0.5, f'{increase_percentage:.2f}%', transform=ax.transAxes,
                    color='green', fontsize=12, verticalalignment='center')
        else:
            ax.yaxis.label.set_color('red')
            ax.tick_params(axis='y', colors='red')
            ax.spines['left'].set_color('red')
            ax.text(1.02, 0.5, f'{increase_percentage:.2f}%', transform=ax.transAxes,
                    color='red', fontsize=12, verticalalignment='center')

    fig.autofmt_xdate(rotation=90)

    # Displaying in Streamlit
    st.pyplot(fig, use_container_width=True)

# Sidebar controls
st.sidebar.header('Settings')
SMA1 = st.sidebar.slider('SMA1', min_value=1, max_value=50, value=10)
SMA2 = st.sidebar.slider('SMA2', min_value=1, max_value=50, value=30)
NumPoints = st.sidebar.slider('Number of Points', min_value=50, max_value=500, value=200)
timeframe = st.sidebar.selectbox('Timeframe', ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1d'], index=5)
assets = st.sidebar.multiselect('Select Assets', 
                                ['ETH/USD', 'SOL/USD', 'SUI/USD', 'AVAX/USD', 'APT/USD', 'NEAR/USD', 'INJ/USD',
                                 'STX/USD', 'DOGE/USD', 'IMX/USD', 'RNDR/USD', 'FET/USD', 'SUPER/USD', 'HNT/USD',
                                 'SEI/USD'], 
                                default=['ETH/USD', 'SOL/USD', 'SUI/USD', 'AVAX/USD'])

if 'assets' not in st.session_state:
    st.session_state.assets = assets

if st.sidebar.button('Fetch Data'):
    st.session_state.closeData = fetch_data(timeframe)

if 'closeData' in st.session_state:
    plot_data(st.session_state.closeData, SMA1, SMA2, NumPoints)
else:
    st.write('Click "Fetch Data" to load the data.')
