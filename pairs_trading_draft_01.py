#!/usr/bin/env python
# coding: utf-8

# In[264]:


import ssl
import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np
from sklearn import linear_model

# import yfinance as yf
from yahoofinancials import YahooFinancials
from statsmodels.tsa.stattools import adfuller


# In[265]:


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


# In[266]:


if __name__ == '__main__':
    pairs = pair_selection('Information Technology', 0.9, 0.05, '2014-01-01', '2016-01-01')


# In[267]:


pairs.company_list()


# In[268]:


pairs.corr_coint_filter()


# In[281]:


class trading_signal(pair_selection):
    def __init__(self, open_threshold, close_threshold, sectorName, corr_threshold, p_value_threshold, coint_start_date, coint_end_date, trade_start, trade_end, num_days):
        super().__init__(sectorName, corr_threshold, p_value_threshold, coint_start_date, coint_end_date)
        self.open_threshold = open_threshold
        self.close_threshold =close_threshold
        self.trade_start = trade_start
        self.trade_end = trade_end
        self.num_days = num_days
    

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
                    
        pd.set_option('display.max_rows', None)
        signal_table_adj = signal_table.dropna(how = 'all')
        return signal_table_adj


# In[282]:


if __name__ == '__main__':
    trade = trading_signal(1.5, 0.5, 'Information Technology', 0.9, 0.05, '2014-01-01', '2016-01-01', '2016-01-01', '2021-01-01', 90)


# In[283]:


trade.signal()


# In[ ]:


#下面这部分是选一个pair解释cointegration的图和p-value的，backtesting的时候不用管，写report的时候用

## estimate spread - if two stocks are cointegrated, any divergence in the spread should be temporary and go back to the mean
## check the whether the graph of the price movement is actually fluctuating around the mean
## spread = log(y) - beta * log (x) - alpha
## this part is created to show explain stationary in final project

pair = pairs.corr_coint_filter()
test_pair = pair[random.randint(0,len(pair)-1)]
print(test_pair)

def test_spread(x, y): #calculate spread for a random selected stationary pair
    regr = linear_model.LinearRegression()
    x_constant = pd.concat([x, pd.Series([1]*len(x),index = x.index)], axis=1)
    regr.fit(x_constant, y)
    beta = regr.coef_[0]
    alpha = regr.intercept_
    spd = y - beta * x - alpha
    
    return spd 

price = pairs.stock_price().loc['2014-01-01':'2016-01-01']
x = np.log(price[test_pair[0]])
y = np.log(price[test_pair[1]])
spread = test_spread(x, y)
spread.plot()
plt.axhline(0,color = 'red', linestyle='--')
plt.ylabel('spread')
        
        
# test stationary
adf = adfuller(spread, maxlag = 1)
print(adf[0])
for key, value in adf[4].items():
    print(key, value)
print('p-value', adf[1])


# In[ ]:


# 下面这部分是随机选取一个pair然后visualize hedge ratio图表的，之后report可以用到，你们继续写backtesting的时候不用管

class trading_test_signal(pair_selection):
    def __init__(self, open_threshold, close_threshold, sectorName, corr_threshold, p_value_threshold, coint_start_date, coint_end_date, trade_start, trade_end, num_days):
        super().__init__(sectorName, corr_threshold, p_value_threshold, coint_start_date, coint_end_date)
        self.open_threshold = open_threshold
        self.close_threshold =close_threshold
        self.trade_start = trade_start
        self.trade_end = trade_end
        self.num_days = num_days
    

    def test_signal(self): #calculate ratio      
        #test one random pair
        pair = self.corr_coint_filter()
        test_pair = pair[random.randint(0,len(pair)-1)]
        print(test_pair)
    
        price = self.stock_price().loc[self.trade_start:self.trade_end]
        price = price.fillna(0)
        x = price[test_pair[0]]
        y = price[test_pair[1]] #log(price) or price ???
        
        ratio = x / y
        ratios_mavg90 = ratio.rolling(window=self.num_days,center=False).mean()
        std_90 = ratio.rolling(window=self.num_days,center=False).std()
        
        z_score = (ratio-ratios_mavg90)/std_90
        z_score_mean = np.mean(z_score)

        
#         plt.figure(figsize=(15,7))
#         plt.plot(ratio.index, ratio.values)
#         plt.plot(ratios_mavg90.index, ratios_mavg90.values)
#         plt.legend(['Ratio','90d Ratio MA'])
#         plt.ylabel('Ratio')
#         plt.show()  
        
       
#         z_score.plot()
#         plt.axhline(z_score_mean, color='black', linestyle='--')
#         plt.axhline(self.std_threshold, color='red', linestyle='--')
#         plt.axhline(-self.std_threshold, color='green', linestyle='--')
        
# #         z_score[z_score > self.std_threshold].plot(color = 'red')
# #         z_score[z_score < -self.std_threshold].plot(color = 'green') 
#         plt.legend(['Rolling Ratio z-Score', 'Mean', 'upper sd', 'lower sd'])
#         plt.show()

        trading_table = pd.DataFrame(index = z_score.index, columns = ['z_score', 'buy', 'sell'])
            
        for i in range(len(z_score)):
            #Selling ratio
            if z_score[i] > self.open_threshold: 
#                 print(f'Selling {test_pair[0]}, Buying {test_pair[1]}')
                trading_table['z_score'][i] = z_score[i]
                trading_table['buy'][i] = test_pair[1]
                trading_table['sell'][i] = test_pair[0]

            
            #Buying ratio
            elif z_score[i] < -self.open_threshold:
#                 print(f'Selling {test_pair[0]}, Buying {test_pair[1]}')
                trading_table['z_score'][i] = z_score[i]
                trading_table['buy'][i] = test_pair[0]
                trading_table['sell'][i] = test_pair[1]
            

        trading_table_adj = trading_table.dropna(how = 'all')
        
        return trading_table_adj
    
if __name__ == '__main__':
    trade = trading_test_signal(1.5, 0.5, 'Information Technology', 0.9, 0.05, '2014-01-01', '2016-01-01', '2016-01-01', '2021-01-01', 90)

trade.test_signal()

