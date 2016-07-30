'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 23, 2013

@author: Sourabh Bajaj, Jason Zhao
@contact: sourabhbajaj@gatech.edu, j7zhao@ucsd.edu
@summary: Event Profiler Using Actual Close Price Threshold 
'''


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

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]

            # Event is found if the symbol drops from above $5 to below $5
            if f_symprice_yest >= 9.0 and f_symprice_today < 9.0:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


if __name__ == '__main__':
    # Define time period from start of 2008 to end of 2009
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    # Using stocks from SP500 in 2008
    dataobj = da.DataAccess('Yahoo')

    ls_symbols = dataobj.get_symbols_from_list('sp5002008')
    ls_symbols.append('SPY')

    # Using stocks from SP500 in 2012
    symbols = dataobj.get_symbols_from_list('sp5002012')
    symbols.append('SPY')
    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    ldf_data2 = dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data2 = dict(zip(ls_keys, ldf_data2))
    
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

        d_data2[s_key] = d_data2[s_key].fillna(method='ffill')
        d_data2[s_key] = d_data2[s_key].fillna(method='bfill')
        d_data2[s_key] = d_data2[s_key].fillna(1.0)        

    df_events = find_events(ls_symbols, d_data)


    df_events2 = find_events(symbols, d_data2)
    
    print "Creating Study"
    
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')
    
    print "Creating Study 2"

    ep.eventprofiler(df_events2, d_data2, i_lookback=20, i_lookforward=20,
                s_filename='MyEventStudy2.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY') 
