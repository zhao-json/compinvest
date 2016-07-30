'''
Created on July, 2, 2016

@author: Jason Zhao
@contact: j7zhao@ucsd.edu
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

# starting cash and file to be read
start = 100000
filename = 'orders_hw6.csv'

def sort_by_datetime(line):
    return datetime.strptime('{0}-{1}-{2}'.format(*line[0:3]), '%Y-%m-%d')
    
reader = csv.reader(open(filename, 'rU'), delimiter=',')
reader = sorted(reader, key=sort_by_datetime)
pprint(reader)
# nparrays to hold dates and symbols of orders
date = []
sym = []

# csv reader
for row in reader: 
    dt_log = dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16)
    date.append(dt_log)
    sym.append(row[3])

# No duplicates
sym_un = list(set(sym))

# Define time period from start of 2011 to end of 2011
dt_start = date[0]
dt_end = date[-1]
dt_end_read = dt_end + dt.timedelta(days=1)
ldt_timestamps = du.getNYSEdays(dt_start, dt_end_read, dt.timedelta(hours=16))

# Reading stocks from in 2011
dataobj = da.DataAccess('Yahoo')

ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

ldf_data = dataobj.get_data(ldt_timestamps, sym_un, ls_keys)
d_data = dict(zip(ls_keys, ldf_data))

for s_key in ls_keys:
    d_data[s_key] = d_data[s_key].fillna(method='ffill')
    d_data[s_key] = d_data[s_key].fillna(method='bfill')
    d_data[s_key] = d_data[s_key].fillna(1.0)

# Using actual close for better approximation
df_close = d_data['close']

# Storing order entries
dataframe = copy.deepcopy(df_close)
dataframe = pd.DataFrame(0, dataframe.index, dataframe.columns)

reader = csv.reader(open(filename, 'rU'), delimiter=',')
for row in reader: 
    dt_log = dt.datetime(int(row[0]), int(row[1]), int(row[2]), 16)
    if (row[4] == 'Buy'):
        dataframe[row[3]][dt_log] += int(row[5])
    if (row[4] == 'Sell'):
        dataframe[row[3]][dt_log] += -int(row[5])

transaction = df_close * dataframe

cash = pd.DataFrame(start, dataframe.index, columns=['CASH'])

for action in range(0, len(cash.index)):
    if action == 0:
        new = cash['CASH'][action] - sum(transaction.loc[cash.index[action]])
        cash.set_value(cash.index[action], 'CASH', new)
    else:
        new = cash['CASH'][action-1] - sum(transaction.loc[cash.index[action]])
        cash.set_value(cash.index[action], 'CASH', new)

holdframe = dataframe.cumsum(axis=0)

df_close['_CASH'] = 1.0
dataframe['_CASH'] = cash
holdframe['_CASH'] = cash

totalval = df_close * holdframe
totalval['Total'] = totalval.sum(axis=1)

filename = open('output.csv', 'wb')
writer = csv.writer(filename, delimiter=',')
for row_index in totalval.index:
    writer.writerow([row_index.year, row_index.month, row_index.day, totalval['Total'][row_index]])
    
filename.close()
print 'Complete'