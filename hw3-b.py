'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on July 2, 2016

@author: Jason Zhao
@contact: j7zhao@ucsd.edu
@summary: Analyze HW3 value outputs
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import decimal 
import csv
print "Pandas Version", pd.__version__

def simulate(startdate, enddate, sym):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(startdate, enddate, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, sym, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values

    # Normalizing the prices to start at 1 and see relative returns
    na_normalized_price = na_price / na_price[0, :]

    vol, daily_ret, sharpe, cum_ret = opt(na_normalized_price)
    return vol, daily_ret, sharpe, cum_ret
    
def opt(na_normalized_price): 
    # Allocate and provide according weights
    na_alloc = na_normalized_price 

    na_sum = na_alloc.transpose()
    na_sum = na_sum.sum(axis=0)
    na_sum_price = np.copy(na_sum)
    
    # Cumulative return is the last index cumulative array
    cum_ret = na_sum[-1]

    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = na_normalized_price.copy()

    
    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_sum)
    
    # Volatility is stdeviation of normalized daily return
    vol = np.std(na_sum)

    # Average daily return
    daily_ret = np.mean(na_sum)

    # Sharpe ratio
    sharpe = np.sqrt(252)*(daily_ret/(np.std(na_sum)))    

    return vol, daily_ret, sharpe, cum_ret

def main():
    ''' Main Function'''

    # SPX index
    ls_symbols = ['$SPX']
    
    # CSV Reader
    filename = 'output.csv'
    reader = csv.reader(open(filename, 'rU'), delimiter=',')
    
    # nparrays to hold dates and symbols of orders
    date = []
    val = []
    
    # csv reader
    for row in reader: 
        dt_log = dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16)
        date.append(dt_log)
        val.append(float(row[3]))
    
    # Define time period from start of 2011 to end of 2011
    dt_start = date[0]
    dt_end = date[-1]  
    val_price = np.asarray(val)
    
    # Fund statistics
    # Cumulative return
    cum_ret_fund = val[-1] / val[0]
    
    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    val[:] = [x / val[0] for x in val]
    val = np.asarray(val)
    tsu.returnize0(val)

    # Volatility is stdeviation of normalized daily return
    vol_fund = np.std(val)

    # Average daily return
    daily_ret_fund = np.mean(val)

    # Sharpe ratio
    sharpe_fund = np.sqrt(252)*(daily_ret_fund/(np.std(val)))  
    
    vol, daily_ret, sharpe, cum_ret = simulate(dt_start, dt_end, ls_symbols)
    
    print 'Details of the Performance of the portfolio :'
    print 'Data Range: %s to %s' %(dt_start, dt_end)

    print 'Sharpe Ratio of Fund: %s' %sharpe_fund
    print 'Sharpe Ratio of $SPX: %s' %sharpe
    
    print 'Total Return of Fund: %s' %cum_ret_fund
    print 'Total Return of $SPX: %s' %cum_ret
    
    print 'Standard Deviation of Fund: %s' %vol_fund
    print 'Standard Deviation of $SPX: %s' %vol
    
    print 'Average Daily Return of Fund: %s' %daily_ret_fund
    print 'Average Daily Return of $SPX: %s' %daily_ret

    print val_price
	
    # Plotting the prices with x-axis=timestamps
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))    
    plt.clf()
    plt.plot(ldt_timestamps, val_price )
    plt.legend(ls_symbols , 'Fund')
    plt.ylabel('Adjusted Close')
    plt.xlabel('Date')
    plt.savefig('adjustedclose.pdf', format='pdf')    

if __name__ == '__main__':
    main()
