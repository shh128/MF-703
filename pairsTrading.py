## 
# pairsTrading.py - Final Project, MF 703
# Name: Chikang Kuo, Shuxian Hong, Zhihao Zhang, Zelin Zhao
# Description: 703 final project
# 

import ssl
import pandas as pd
# import yfinance as yf
from yahoofinancials import YahooFinancials
from statsmodels.tsa.stattools import adfuller

def pairSelection(sectorName, corr_threshold, p_value_threshold, 
                  coint_start_date, coint_end_date):
    ## Get the company list in the S&P 500
    ssl._create_default_https_context = ssl._create_unverified_context
    
    payload=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    first_table = payload[0]
    df = first_table
    print(df.columns)
    
    ## Group the companies by the column "GICS Sector"
    grouped_df = df.groupby("GICS Sector")
    grouped_lists = grouped_df["Symbol"].apply(list)
    grouped_lists = grouped_lists.reset_index()
    grouped_lists = grouped_lists.set_index('GICS Sector')
    print(grouped_lists)
    
    ## Get the historical data in the specific sector
    assets = grouped_lists.loc[sectorName][0]
    
    yahoo_financials = YahooFinancials(assets)
    data = yahoo_financials.get_historical_price_data(start_date='2014-01-01', 
                                                      end_date='2021-01-01', 
                                                      time_interval='daily')
    
    
    prices_df = pd.DataFrame({
        a: {x['formatted_date']: x['adjclose'] for x in data[a]['prices']} for a in assets
        }) 
    
    prices_df = prices_df.loc[coint_start_date:coint_end_date]
    print(prices_df)
    print(prices_df.isnull().sum())
    
    ## Filter the stock pairs by correlation matrix
    corr_df = prices_df.corr()
    pairs = []    
    for stock1 in assets:
        for stock2 in assets:
            if (corr_df.loc[stock1,stock2] >= corr_threshold
                and stock1 != stock2 
                and (stock1, stock2) not in pairs 
                and (stock2, stock1) not in pairs):
                pairs.append((stock1, stock2))  
    print("The pairs with correlation above the threshold 0.9:\n", pairs)

    ## Further the filtering by stationarity of the spread of pairs
    pairs_st = []
    for p in pairs:
        if adfuller(prices_df[p[0]] - prices_df[p[1]])[1] < p_value_threshold:
            pairs_st.append(p)
    print("The pairs with stationarity of the spread:\n", pairs_st)




################################################################################
if __name__ == '__main__':
    pairSelection('Information Technology', 0.9, 0.05, '2014-01-01', '2016-01-01')
    
