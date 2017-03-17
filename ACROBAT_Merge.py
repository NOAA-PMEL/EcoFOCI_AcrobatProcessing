#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 09:27:55 2017

@author: bell
"""

import pandas as pd
import matplotlib.pyplot as plt
import seawater as sw

from io_utils import ConfigParserLocal

def cond2salinity(conductivity=None, temperature=None, pressure=None):
    
    stand_sw_cond = 4.2914 #S*m-1

    condr = conductivity / stand_sw_cond

    return sw.salt(condr, temperature, pressure)

def counts2engr(coefs, rawdata):
    return coefs['ScaleFactor'] * (rawdata - coefs['DarkCounts'])
"""-------------------------------- Main -----------------------------------------------"""


GPS = pd.read_csv('/Volumes/WDC_internal/Users/bell/ecoraid/2016/AlongTrack/AQ1601/ACROBAT/working/Acrobat_GPS_clean_160912.csv')
GPS.DateTime = pd.to_datetime(GPS.DateTime,format='%Y-%m-%dT%H:%M:%S')
GPS = GPS.set_index(pd.DatetimeIndex(GPS['DateTime']))
GPS.drop('DateTime', axis=1, inplace=True)

FastCat = pd.read_csv('/Volumes/WDC_internal/Users/bell/ecoraid/2016/AlongTrack/AQ1601/ACROBAT/working/Acrobat_FastCat_clean_160912.csv')
FastCat.DateTime = pd.to_datetime(FastCat.DateTime,format='%Y-%m-%dT%H:%M:%S')
FastCat = FastCat.set_index(pd.DatetimeIndex(FastCat['DateTime']))
FastCat.drop('DateTime', axis=1, inplace=True)

Triplet = pd.read_csv('/Volumes/WDC_internal/Users/bell/ecoraid/2016/AlongTrack/AQ1601/ACROBAT/working/Acrobat_Triplet_clean_160912.csv')
Triplet.DateTime = pd.to_datetime(Triplet.DateTime,format='%Y-%m-%dT%H:%M:%S')
Triplet = Triplet.set_index(pd.DatetimeIndex(Triplet['DateTime']))
Triplet.drop('DateTime', axis=1, inplace=True)

ACROBAT = pd.read_csv('/Volumes/WDC_internal/Users/bell/ecoraid/2016/AlongTrack/AQ1601/ACROBAT/working/Acrobat_clean_160912.csv')
ACROBAT.DateTime = pd.to_datetime(ACROBAT.DateTime,format='%Y-%m-%dT%H:%M:%S')
ACROBAT = ACROBAT.set_index(pd.DatetimeIndex(ACROBAT['DateTime']))
ACROBAT.drop('DateTime', axis=1, inplace=True)


AllData=pd.concat([GPS, FastCat, Triplet], axis=1)

### Apply Cals and Scaling Parameters
AllData['Salinity'] = cond2salinity(AllData['Conductivity'],AllData['Temperature'],AllData['Pressure'])

cal_file_path = '/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_AcrobatProcessing/inst_config/AQ1601.yaml'
cal_file = ConfigParserLocal.get_config_yaml(cal_file_path)

#AllData['Wetlabs_CDOM'] = counts2engr(cal_file['Wetlabs_460nm_Coeffs'], AllData['460nm'])
#AllData['Wetlabs_CHL']  = counts2engr(cal_file['Wetlabs_CHL_Coeffs'], AllData['695nm'])
#AllData['Wetlabs_NTU']  = counts2engr(cal_file['Wetlabs_700nm_Coeffs'], AllData['700nm'])

### Save as NetCDF for all data and daily (as a function of time)



### Sample Figures

plt.figure()
plt.subplot(1,1,1)
ACROBAT.plot(x=ACROBAT.index,y='vd', ax=plt.gca())
AllData.plot(x=AllData.index,y='Pressure', ax=plt.gca())