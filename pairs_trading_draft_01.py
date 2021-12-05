import ssl
import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np
from sklearn import linear_model
import math

# import yfinance as yf
from yahoofinancials import YahooFinancials
from statsmodels.tsa.stattools import adfuller

class pair_selection:
    
    def __init__(self, sectorName, corr_threshold, p_value_threshold,
                  coint_start_date, coint_end_date):
        self.sectorName = sectorName
        self.corr_threshold = corr_threshold
        self.p_value_threshold = p_value_threshold 
        self.coint_start_date = coint_start_date
        self.coint_end_date = coint_end_date
        
    def company_list(self):
        ## Get the company list in the S&P 500
        ssl._create_default_https_context = ssl._create_unverified_context

        payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')            
        first_table = payload[0]
        df = first_table
        #print(df.columns)

        ## Group the companies by the column "GICS Sector"
        grouped_df = df.groupby("GICS Sector")
        grouped_lists = grouped_df["Symbol"].apply(list)
        grouped_lists = grouped_lists.reset_index()
        grouped_lists = grouped_lists.set_index('GICS Sector')
        return grouped_lists
    
    def ticker(self):
        company = self.company_list()    
        assets = company.loc[self.sectorName][0] #get specific ticker in the selected sector
        return assets
       
    
    def stock_price(self):
        tickers = self.ticker()
        yahoo_financials = YahooFinancials(tickers)
        data = yahoo_financials.get_historical_price_data(start_date='2014-01-01',
                                                          end_date='2021-01-01',
                                                          time_interval='daily')
    
        prices_df = pd.DataFrame({
            a: {x['formatted_date']: x['adjclose']
                  for x in data[a]['prices']}
            for a in tickers
        })
        return prices_df
    
    def corr_coint_filter(self):
        ## Filter the stock pairs by correlation matrix        
        
        prices_df = self.stock_price().loc[self.coint_start_date:self.coint_end_date] 
        prices_df = prices_df.fillna(0)
        
        tickers = self.ticker()
        corr_df = prices_df.corr()

        pairs = []
        for stock1 in tickers:
            for stock2 in tickers:
                if (corr_df.loc[stock1, stock2] >= self.corr_threshold
                        and stock1 != stock2 and (stock1, stock2) not in pairs
                        and (stock2, stock1) not in pairs):
                    pairs.append((stock1, stock2))
 
        ## Further the filtering by stationarity of the spread of pairs
        pairs_st = []
        for p in pairs:
            if adfuller(prices_df[p[0]] - prices_df[p[1]])[1] < self.p_value_threshold:
                pairs_st.append(p)
        return pairs_st                    
    
    
class trading_signal(pair_selection):
    def __init__(self, open_threshold, close_threshold, sectorName, corr_threshold, p_value_threshold, coint_start_date, coint_end_date, trade_start, trade_end, num_days):
        super().__init__(sectorName, corr_threshold, p_value_threshold, coint_start_date, coint_end_date)
        self.open_threshold = open_threshold
        self.close_threshold =close_threshold
        self.trade_start = trade_start
        self.trade_end = trade_end
        self.num_days = num_days
    
    def ratio(self):
        pair = self.corr_coint_filter()
        price = self.stock_price().loc[self.trade_start:self.trade_end]
        
        price = price.fillna(0)
        ratio_table = pd.DataFrame(index = price.index, columns= pair)
        for i in range(len(pair)):
            x = price[pair[i][0]]
            y = price[pair[i][1]] 
                
            ratio_table[pair[i]] = x / y 
        return ratio_table          
    
    
    def signal(self): #calculate ratio 
        
        pair = self.corr_coint_filter()
        price = self.stock_price().loc[self.trade_start:self.trade_end]
        
        price = price.fillna(0)
        
        signal_table = pd.DataFrame(index = price.index, columns = pair, data = None)
        for i in range(len(pair)):
            x = price[pair[i][0]]
            y = price[pair[i][1]] 
                
            ratio = x / y
            ratios_mavg90 = ratio.rolling(window=self.num_days,center=False).mean()
            std_90 = ratio.rolling(window=self.num_days,center=False).std()
        
            z_score = (ratio-ratios_mavg90)/std_90
            z_score_mean = np.mean(z_score)
            
            for j in range(len(z_score)):
                if z_score[j] > self.open_threshold: 
                    #sell x(left), buy y(right)
                    signal_table[pair[i]][j] = 1
           
                elif z_score[j] < -self.open_threshold:
                    #buy x(left), sell y(right)
                    signal_table[pair[i]][j] = -1
                
                elif abs(z_score[j]) < self.close_threshold:
                    signal_table[pair[i]][j] = 0
                    
#         pd.set_option('display.max_rows', None)
#        signal_table_adj = signal_table.dropna(how = 'all')
        return signal_table
    
    def adj_signal(self):
        table = self.signal()
        for i in range(1, table.shape[0]):
            for j in range(0, table.shape[1]):
                if table.iloc[i-1, j] == 1 and math.isnan(table.iloc[i, j]) == True:
                    table.iloc[i, j] = 1
                elif table.iloc[i-1, j] == 0 and math.isnan(table.iloc[i, j]) == True:
                    table.iloc[i, j] = 0
                elif table.iloc[i-1, j] == -1 and math.isnan(table.iloc[i, j]) == True:
                    table.iloc[i, j] = -1
                    
        pd.set_option('display.max_rows', None)
        return table
  
  
if __name__ == '__main__':
    pairs = pair_selection('Energy', 0.9, 0.05, '2014-01-01', '2016-01-01')

    trade = trading_signal(1.5, 0.5, 'Energy', 0.9, 0.05, '2014-01-01', '2016-01-01', '2016-01-01', '2021-01-01', 90)
