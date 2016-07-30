'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on June 29, 2016

@author: Jason Zhao
@contact: j7zhao@ucsd.edu
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

    # Optimizer and optimized values
    sharpe_init = 0
    tmp = []
    # Optimizer
    for i in np.arange(0, 1.1, 0.1):
        for j in np.arange(0, 1 - i + 0.1, 0.1):
            for k in np.arange(0, 1 - i - j + 0.1, 0.1):
                for l in np.arange(0, 1 - i - j - k + 0.1, 0.1):
                    if (i + j + k + l == 1.0):
                        alloc = [i, j, k, l]
                        
                        vol, daily_ret, sharpe, cum_ret = opt(na_normalized_price, alloc)
                        
                        if (sharpe > sharpe_init):
                            sharpe_init = sharpe
                            tmp = alloc
                
    vol, daily_ret, sharpe, cum_ret = opt(na_normalized_price, tmp)
    return vol, daily_ret, sharpe, cum_ret, tmp
    
def opt(na_normalized_price, alloc): 
    # Allocate and provide according weights
    na_alloc = na_normalized_price * alloc

    na_sum = na_alloc.transpose()
    na_sum = na_sum.sum(axis=0)

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

    # List of symbols
    ls_symbols = ['C', 'GS', 'IBM', 'HNZ']
    # Start and End date of the charts
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    
    vol, daily_ret, sharpe, cum_ret, alloc = simulate(dt_start, dt_end, ls_symbols)
    print 'Start Date: %s' %dt_start
    print 'End Date: %s' %dt_end
    print 'Symbols: %s' %ls_symbols
    print 'Allocation: %s' %alloc 
    print 'Sharpe Ratio: %s' %sharpe
    print 'Volalitity: %s' %vol
    print 'Average Daily Return: %s' %daily_ret
    print 'Cumulative Return: %s' %cum_ret

if __name__ == '__main__':
    main()
