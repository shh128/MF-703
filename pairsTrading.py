## 
# pairsTrading.py - Final Project, MF 703
# Name: Chikang Kuo, Shuxian Hong, Zhihao Zhang, Zelin Zhao
# Description: 703 final project
# 

import ssl
import pandas as pd
# import yfinance as yf
from yahoofinancials import YahooFinancials

def pairSelection(sectorName):
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

    print(prices_df.corr() >= 0.9)






################################################################################
if __name__ == '__main__':
    pairSelection('Communication Services')
    
    
    
    
    
    
