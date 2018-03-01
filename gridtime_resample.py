#!/usr/bin/env python

"""
 Background:
 --------
 gridtime_resample.py
 
 
 Purpose:
 --------
 Resample and fill timegaps

 History:
 --------

"""

import argparse
import pandas as pd


"""---"""

parser = argparse.ArgumentParser(description='CTD plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,
	help='full path to directory of processed nc files')
parser.add_argument('resolution', metavar='resolution', type=str,
	help='choose: 1S, 60S, 3600S')

args = parser.parse_args()

df = pd.read_csv(args.DataPath,parse_dates=['DateTime'])
df.set_index(pd.DatetimeIndex(df['DateTime']),inplace=True,drop=True)

df.resample(args.resolution).to_csv(args.DataPath.replace('.csv','.resample.csv'))