'''
Created on July 22, 2016

@author: Jason Zhao
@contact: j7zhao@ucsd.edu
@summary: Bollinger Bands
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import copy
import csv 
from pprint import pprint

# List of symbols
ls_symbol = ["MSFT"]

# Start and End date of the charts
dt_start = dt.datetime(2010, 1, 1)
dt_end = dt.datetime(2010, 12, 31)

# We need closing prices so the timestamp should be hours=16.
dt_timeofday = dt.timedelta(hours=16)

# Get a list of trading days between the start and the end.
ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

# Creating an object of the dataaccess class with Yahoo as the source.
c_dataobj = da.DataAccess('Yahoo')

# Keys to be read from the data, it is good to read everything in one go.
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

# Reading the data, now d_data is a dictionary with the keys above.
# Timestamps and symbols are the ones that were specified before.
ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbol, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

# Filling the data for NAN
for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

# Getting the numpy ndarray of close prices.
na_price = d_data['close'].values

# Getting rolling mean of prices
mean = pd.rolling_mean(na_price, 20)

# Getting the rolling std of prices
std = pd.rolling_std(na_price, 20)

# Upper and lower band
upper = mean + std
lower = mean - std

# Bollinger value
bol = (na_price - mean) / std
boldf = pd.DataFrame(bol, ldt_timestamps)

# Plotting the prices with x-axis=timestamps
plt.clf()
plt.plot(ldt_timestamps, na_price, 'r', ldt_timestamps, mean,
         ldt_timestamps, upper, 'k', ldt_timestamps, lower, 'm')
plt.legend(ls_symbol)
plt.ylabel('Adjusted Close')
plt.xlabel('Date')
