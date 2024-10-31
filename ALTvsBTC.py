import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import ccxt
import matplotlib.pyplot as plt
import seaborn as sns

def getDataCCXT(ID,start,end):
    exchange = ccxt.coinbase()
    data = exchange.fetch_ohlcv (ID, '1h') 
    data = pd.DataFrame(data)
    #data = pd.DataFrame(reversed_data)
    data.columns= ["Date","Open","High","Low","Close","Volume"]
    data=data.sort_values(by=['Date'],ascending=True)
    data['Date'] = pd.to_datetime(data['Date'],unit='ms')
    data.set_index('Date', drop=False, inplace=True)
    return data

st.write('fetching data...')

data=np.nan

##set up start and finish window
now = datetime.now()
end= (now - timedelta(hours = 0.5))#.strftime("%Y-%m-%d %H:%M:%S")
start= (end - timedelta(hours = 50))#.strftime("%Y-%m-%d %H:%M:%S")
end=end.strftime("%Y-%m-%d %H:%M:%S")
start=start.strftime("%Y-%m-%d %H:%M:%S")

# set 
SMA1=20
NumPoints = 168

# altcoin list
#assets=['ETH/USD','SOL/USD','SUI/USD','AVAX/USD']

assets=['ETH/USD','SOL/USD','SUI/USD','AVAX/USD','APT/USD','NEAR/USD','INJ/USD',
        'STX/USD','DOGE/USD','IMX/USD','RNDR/USD','FET/USD','SUPER/USD','HNT/USD',
       'SEI/USD']

#get BTC data
try:
    btcData=getDataCCXT("BTC/USD",start,end)['Close']
except:
    st.write("failed to retrieve BTC data")


#get alt data
closeData=pd.DataFrame()
for asset in assets:
    assetName = str(asset).split("/")[0]
    #st.write(assetName)
    try:
        closeData[assetName]=getDataCCXT(asset,start,end)['Close']
    except:
        st.write("failed to retrieve data for ticker: ",asset)

# reference to BTC
closeData = closeData.div(btcData, axis=0)


# create SMA dataframe
rollingAverageData = closeData.rolling(window=SMA1).mean()

# trim to desired timeframe
closeData = closeData[-NumPoints:]
rollingAverageData = rollingAverageData[-NumPoints:]


# Plots
numAssets=len(closeData.columns)
numRows=int(numAssets/2)

fig, axes = plt.subplots(numRows, 2, figsize=(10, 10),sharex=True)
fig.subplots_adjust(wspace=0.3,hspace=0)
fig.suptitle('altcoins vs BTC')

for index, asset in enumerate(closeData.columns):
    if closeData[asset].iloc[-1]>rollingAverageData[asset].iloc[0]:
        lineColor='green'
    else:
        lineColor='red'
    if index < numRows:
        ax=sns.lineplot(ax=axes[index,0], data=closeData, x='Date', y=asset, color=lineColor)
        ax=sns.lineplot(ax=axes[index,0], data=rollingAverageData, x='Date', y=asset, color="blue")
        #ax.tick_params(axis='x', rotation=90)
    else:
        ax1=sns.lineplot(ax=axes[index-numRows,1], data=closeData, x='Date', y=asset, color=lineColor)
        ax1=sns.lineplot(ax=axes[index-numRows,1], data=rollingAverageData, x='Date', y=asset, color="blue")
        #ax1.tick_params(axis='x', rotation=90)

fig.autofmt_xdate(rotation=90)

#clear text before charts
st.empty()

st.pyplot(fig)

