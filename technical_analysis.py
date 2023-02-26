import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
import datetime
import warnings
from ta.trend import MACD
warnings.filterwarnings('ignore')

def calculated_df(df):
    df['Date'] = df.index
    df['Day_Perc_Change'] = df['Adj Close'].pct_change()*100
    df.dropna(inplace= True)
    df['Trend']= np.zeros(df['Day_Perc_Change'].count())
    df['Trend']= df['Day_Perc_Change'].apply(lambda x:trend(x))
    return df

def last_2_years_price_plot(df):
    df['Adj Close'].plot()
    plt.xlabel('Date')
    plt.ylabel('Adj Close Price')

# def daily_percent_change(df):
    
def daily_percent_change_plot(df):
    calculated_df(df)['Day_Perc_Change'].plot()
    plt.xlabel('Date')
    plt.ylabel('Percenatge returns')

def daily_percent_change_histogram(df):
    calculated_df(df)['Day_Perc_Change'].hist(bins = 50) 
    plt.xlabel('Daily returns')
    plt.ylabel('Frequency')
    plt.show()

def trend(x):
    if x > -0.5 and x <= 0.5:
        return 'Slight or No change'
    elif x > 0.5 and x <= 1:
        return 'Slight Positive'
    elif x > -1 and x <= -0.5:
        return 'Slight Negative'
    elif x > 1 and x <= 3:
        return 'Positive'
    elif x > -3 and x <= -1:
        return 'Negative'
    elif x > 3 and x <= 7:
        return 'Among top gainers'
    elif x > -7 and x <= -3:
        return 'Among top losers'
    elif x > 7:
        return 'Bull run'
    elif x <= -7:
        return 'Bear drop'
    
def trend_pie_chart(df):
    pie_label = sorted([i for i in calculated_df(df).loc[:, 'Trend'].unique()])
    plt.pie(calculated_df(df)['Trend'].value_counts(), labels = pie_label, autopct = '%1.1f%%', radius = 2)
    plt.show()

def volume_plot(df):
    # Daily volume of trade has been reduced in scale to match with the daily return scale
    calculated_data = calculated_df(df)
    plt.stem(calculated_data['Date'], calculated_data['Day_Perc_Change'])
    (calculated_data['Volume']/1000000).plot(figsize = (15, 7.5), color = 'green', alpha = 0.5)
    plt.show()
    
def volatility_plot(df):
    ADANI_vol = calculated_df(df)['Day_Perc_Change'].rolling(7).std()*np.sqrt(7)
    ADANI_vol.plot()


def generate_buy_sell_signals(condition_buy, condition_sell, dataframe, strategy):
    last_signal = None
    indicators = []
    buy = []
    sell = []
    for i in range(0, len(dataframe)):
        # if buy condition is true and last signal was not Buy
        if condition_buy(i, dataframe) and last_signal != 'Buy':
            last_signal = 'Buy'
            indicators.append(last_signal)
            buy.append(dataframe['Close'].iloc[i])
            sell.append(np.nan)
        # if sell condition is true and last signal was Buy
        elif condition_sell(i, dataframe)  and last_signal == 'Buy':
            last_signal = 'Sell'
            indicators.append(last_signal)
            buy.append(np.nan)
            sell.append(dataframe['Close'].iloc[i])
        else:
            indicators.append(last_signal)
            buy.append(np.nan)
            sell.append(np.nan)

    dataframe[f"{strategy}_Last_Signal"] = np.array(last_signal)
    dataframe[f"{strategy}_Indicator"] = np.array(indicators)
    dataframe[f"{strategy}_Buy"] = np.array(buy)
    dataframe[f"{strategy}_Sell"] = np.array(sell)


def get_macd(company):
    close_prices = company['Close']
    window_slow = 26
    signal = 9
    window_fast = 12
    macd = MACD(close_prices, window_slow, window_fast, signal)
    company['MACD'] = macd.macd()
    company['MACD_Histogram'] = macd.macd_diff()
    company['MACD_Signal'] = macd.macd_signal()

    generate_buy_sell_signals(
    lambda x, company: company['MACD'].values[x] < company['MACD_Signal'].iloc[x],
    lambda x, company: company['MACD'].values[x] > company['MACD_Signal'].iloc[x],
    company,
    'MACD')
    return company

def plot_price_and_signals(company, strategy):
    data = get_macd(company)
    last_signal_val = data[f"{strategy}_Last_Signal"].values[-1]
    last_signal = 'Unknown' if not last_signal_val else last_signal_val
    title = f'Close Price Buy/Sell Signals using {strategy}.  Last Signal: {last_signal}'
    # fig.suptitle(f'Top: ADANI Stock Price. Bottom: {strategy}')
    if not data[f'{strategy}_Buy'].isnull().all():
        plt.scatter(data.index, data[f'{strategy}_Buy'], color='green', label='Buy Signal', marker='^', alpha=1)
    if not data[f'{strategy}_Sell'].isnull().all():
        plt.scatter(data.index, data[f'{strategy}_Sell'], color='red', label='Sell Signal', marker='v', alpha=1)
    plt.plot(company['Close'], label='Close Price', color='blue', alpha=0.35)
    plt.xticks(rotation=45)
    plt.title(title)
    plt.xlabel('Date', fontsize=20)
    plt.ylabel('Close Price', fontsize=18)
    plt.legend(loc='upper left')


def plot_macd(company):
    macd = get_macd(company)
    # Create and plot the graph
    # fig, axs = plt.subplots(2, sharex=True, figsize=(20,8))
    # plot_price_and_signals(fig, company, macd, 'MACD', axs)
    # plt.figure(figsize=(20,8))
    plt.plot(macd['MACD'], label=' MACD', color = 'green')
    plt.plot(macd['MACD_Signal'], label='Signal Line', color='orange')
    positive = macd['MACD_Histogram'][(macd['MACD_Histogram'] >= 0)]
    negative = macd['MACD_Histogram'][(macd['MACD_Histogram'] < 0)]
    plt.bar(positive.index, positive, color='green')
    plt.bar(negative.index, negative, color='red')    
    plt.legend(loc='upper left')
    # axs[1].grid()
    # print(os.path.abspath(image))
    plt.show()
