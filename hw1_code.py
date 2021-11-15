# HW1
# Name:Chi Kang Kuo
# Email address:chikuo@bu.edu
#

#
# function building
#

import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from scipy.stats import norm

##problem 1
str1 = "advanced"
print(str1)

str2 = "programming"
print(str2)

str = str1 + str2
print (str)

test = "gram" in str
print (test)
print (str[3])

#str[1] = "p"
#print (str)


##problem 2
print (14 / 4 , 14 % 4)


##problem 3
tuple1 = (" SPY", "S&P Index ", 290.31)
tuple2 = (" XLF", " Financials ", 28.33)
tuple3 = (" XLK", " Technology ", 75.60)
tuples = [ tuple1 , tuple2 , tuple3 ]

spyClose = tuples [0][2]
print ( spyClose )


##problem 4
#read csv
spy = pd.read_csv("C:/Users/ryank/Desktop/1st Semester/Programming(703)/HW/hw1/SPY.csv")
dbc = pd.read_csv("C:/Users/ryank/Desktop/1st Semester/Programming(703)/HW/hw1/DBC.csv")
hyg = pd.read_csv("C:/Users/ryank/Desktop/1st Semester/Programming(703)/HW/hw1/HYG.csv")
eem = pd.read_csv("C:/Users/ryank/Desktop/1st Semester/Programming(703)/HW/hw1/EEM.csv")
eafe = pd.read_csv("C:/Users/ryank/Desktop/1st Semester/Programming(703)/HW/hw1/EFA.csv")
agg = pd.read_csv("C:/Users/ryank/Desktop/1st Semester/Programming(703)/HW/hw1/AGG.csv")
iagg = pd.read_csv("C:/Users/ryank/Desktop/1st Semester/Programming(703)/HW/hw1/IAGG.csv")
spy.index = spy['Date']
dbc.index = dbc['Date']
hyg.index = hyg['Date']
eem.index = eem['Date']
eafe.index = eafe['Date']
agg.index = agg['Date']
iagg.index = iagg['Date']

table = pd.DataFrame(data = np.zeros((len(spy), 7)), 
                     columns = ['spy', 'dbc', 'hyg', 'eem', 'eafe', 'agg', 'iagg'], 
                     index = spy.index)

table['spy'] = spy['Adj Close']
table['dbc'] = dbc['Adj Close']
table['hyg'] = hyg['Adj Close']
table['eem'] = eem['Adj Close']
table['eafe'] = eafe['Adj Close']
table['agg'] = agg['Adj Close']
table['iagg'] = iagg['Adj Close']

print(table.head())


#annulized ret and std
ret_std_table = pd.DataFrame(data = np.zeros((2, 7)), 
                     columns = ['spy', 'dbc', 'hyg', 'eem', 'eafe', 'agg', 'iagg'], 
                     index = ['annualized ret', 'annualized std'])
for i in range(0, 7):
    ret_std_table.iloc[0, i] = np.mean((table.iloc[:,i] / table.iloc[:,i].shift(1) - 1)) * 252
    ret_std_table.iloc[1, i] = np.std((table.iloc[:,i] / table.iloc[:,i].shift(1) - 1)) * math.sqrt(252)
    
print(ret_std_table)

#correlation matrix
corr_mat = pd.DataFrame(data = np.zeros((7, 7)), 
                     columns = ['spy', 'dbc', 'hyg', 'eem', 'eafe', 'agg', 'iagg'], 
                     index = ['spy', 'dbc', 'hyg', 'eem', 'eafe', 'agg', 'iagg'])

for i in range(0, 7):
    for j in range(0, 7):
       corr_mat.iloc[i, j]  = (table.iloc[:,i] / table.iloc[:,i].shift(1) - 1).corr(table.iloc[:,j] / table.iloc[:,j].shift(1) - 1)
       
print(corr_mat)


#cummulative retuen plot
cum_table = pd.DataFrame(data = np.zeros((len(spy), 8)), 
                     columns = ['spy', 'dbc', 'hyg', 'eem', 'eafe', 'agg', 'iagg', 'eql_weight'], 
                     index = spy.index)


for i in range(0, 7):
    cum_table.iloc[:, i] = table.iloc[:, i] / table.iloc[:,i].shift(1) - 1
    cum_table.iloc[:,i] = cum_table.iloc[:, i].cumsum()

cum_table['eql_weight'] = 1/7 * (cum_table['spy'] + cum_table['dbc'] + cum_table['hyg'] + cum_table['eem'] + cum_table['eafe'] + cum_table['agg'] + cum_table['iagg'])



cum_table.plot()

##problem 5
def pay_off_put(s, k, r, t, sigma, st):
    '''
    function that calculates option portfolio payoff under certain conditions and plot the payoff of each components
    s: asset price at t = 0
    k: execution price
    r: interest rate
    t: duration of call option
    sigma: volatility of asset
    st: asset price at t = T
    '''
    
    #premium calculation
    d1 = (math.log(s / k) + (r + (sigma ** 2) / 2) * t) / sigma * math.sqrt(t)
    d2 = d1 - sigma * math.sqrt(t)
    
    c = s * norm.cdf(d1) - k * math.exp(-r * t) * norm.cdf(d2)
    
    #calculate your payoff
    your_payoff_table = pd.DataFrame(np.zeros((1, 3)), columns = ['asset payoff', 'covered call payoff', 'overall payoff'], index = ['value'])
    your_payoff_table.iloc[0, 0] = st - s
    your_payoff_table.iloc[0, 1] = - max(st - k, 0) + c
    your_payoff_table.iloc[0, 2] = st - s - max(st - k, 0) + c
    
    #payoff calculation
    payoff_series = pd.Series(data = np.linspace(s - 50, s + 50, 50))
    

        
        
        

    
    



