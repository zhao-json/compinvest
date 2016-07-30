'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on July 29, 2016

@author: Sourabh Bajaj, Jason Zhao
@contact: sourabhbajaj@gatech.edu, j7zhao@ucsd.edu
@summary: Event Profiler Using Bollinger Band Values to feed into Price Simulator
'''

import csv
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""
    
def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    # Using actual close for better approximation
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']    

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    
    # Getting the numpy ndarray of close prices.
    na_price = df_close
    print na_price
    # Getting rolling mean of prices
    mean = pd.rolling_mean(na_price, 20)
    meanspy = pd.rolling_mean(ts_market, 20)
    
    # Getting the rolling std of prices
    std = pd.rolling_std(na_price, 20)
    stdspy = pd.rolling_std(ts_market, 20)
    
    # Upper and lower band
    upper = mean + std
    lower = mean - std
    
    # Bollinger value
    bol = (na_price - mean) / std
    boldf = pd.DataFrame(bol, ldt_timestamps)
    bolspy = (ts_market - meanspy) / stdspy
    bolspydf = pd.DataFrame(bolspy, ldt_timestamps)

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(boldf)
    df_events = df_events * np.NAN
    
    filename = open('orders_hw6.csv', 'wb')
    writer = csv.writer(filename, delimiter=',')    

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)-5):
            # Calculating the returns for this timestamp
            bol_today = boldf[s_sym].ix[ldt_timestamps[i]]
            bol_yest = boldf[s_sym].ix[ldt_timestamps[i - 1]]
            bolspy_today = bolspydf.ix[ldt_timestamps[i]]

            # Event is found if the symbol drops from above $5 to below $5
            if bol_today <= -2.0 and bol_yest >= -2.0 and bolspy_today >= 1.4:
                writer.writerow([ldt_timestamps[i].year, ldt_timestamps[i].month, ldt_timestamps[i].day, s_sym, 'Buy', 100])
                # Jump ahead to 5 days later
                future = ldt_timestamps[i+5]
                writer.writerow([future.year, future.month, future.day, s_sym, 'Sell', 100 ])
    
    filename.close()
    
    return df_events


if __name__ == '__main__':
    # Define time period from start of 2008 to end of 2009
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    # Using stocks from SP500 in 2008
    dataobj = da.DataAccess('Yahoo')

    # Using stocks from SP500 in 2012
    symbols = dataobj.get_symbols_from_list('sp5002012')
    symbols.append('SPY')
    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    
    ldf_data = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    for s_key in ls_keys:

        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
     

    df_events = find_events(ls_symbols, d_data)

    