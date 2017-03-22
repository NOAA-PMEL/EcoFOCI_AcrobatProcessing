#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 09:27:55 2017

@author: bell
"""

import pandas as pd
import xarray as xa
import matplotlib.pyplot as plt
import seawater as sw
import datetime

from io_utils import ConfigParserLocal

def cond2salinity(conductivity=None, temperature=None, pressure=None):
    
    stand_sw_cond = 4.2914 #S*m-1

    condr = conductivity / stand_sw_cond

    return sw.salt(condr, temperature, pressure)

def counts2engr(coefs, rawdata):
    return coefs['ScaleFactor'] * (rawdata - coefs['DarkCounts'])

def var_att_update(ds,var,atts_dic):
	for key,value in atts_dic.iteritems():
		ds[var].attrs[key] = value
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


AllData=pd.concat([GPS, FastCat, Triplet, ACROBAT], axis=1)

### Apply Cals and Scaling Parameters
AllData['Salinity'] = cond2salinity(AllData['Conductivity'],AllData['Temperature'],AllData['Pressure'])
AllData = AllData.drop(['Conductivity'],1)

cal_file_path = '/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_AcrobatProcessing/inst_config/AQ1601.yaml'
cal_file = ConfigParserLocal.get_config_yaml(cal_file_path)

AllData['Wetlabs_CDOM'] = counts2engr(cal_file['Wetlabs_460nm_Coeffs'], AllData['460nm'])
AllData['Wetlabs_CHL']  = counts2engr(cal_file['Wetlabs_CHL_Coeffs'], AllData['695nm'])
AllData['Wetlabs_NTU']  = counts2engr(cal_file['Wetlabs_700nm_Coeffs'], AllData['700nm'])
AllData = AllData.drop(['460nm','695nm','700nm'],1)




AllData_x = pd.DataFrame.to_xarray(AllData)
AllData_x.rename({'DateTime':'time',
				  'vn':'velocity_north_ACROBAT',
                  've':'velocity_east_ACROBAT',
                  'wc':'watercolumn_depth_ACROBAT',
                  'vd':'vehicle_depth_ACROBAT',
                  'wa':'wing_angle_ACROBAT',
                  'sv':'vehicle_vertical_speed_ACROBAT',
                  'Latitude':'Latitude_GPS',
                  'Longitude':'Longitude_GPS',
                  'Temperature':'Temperature_SBE49',
                  'Salinity':'Salinity_SBE49',
                  'Pressure':'Pressure_SBE49'}, inplace=True)

#drop acrobat details
AllData_x = AllData_x.drop(['k1','k2','k3','lb','alt','ul','ll',
                            'roll','pitch','heading','temperature',
                            'latdd','lathhmm','londd','lonhhmm','altitude'])

### Update NetCDF attributes (global/variable)
ncatts_file_path = '/Volumes/WDC_internal/Users/bell/Programs/Python/EcoFOCI_AcrobatProcessing/inst_config/AQ1601_nc_atts.yaml'
netcdf_attrs = ConfigParserLocal.get_config_yaml(ncatts_file_path)

for variable_name in AllData_x.keys():
	try:
		var_att_update(AllData_x,variable_name,netcdf_attrs[variable_name])
	except KeyError:
		print "Variable:{var} is not in nc_atts.yaml file.  Attributes wont be updated for it".format(var=variable_name)

### global attributes
for gatts in netcdf_attrs['Global_Attributes']:
	AllData_x.attrs[gatts] = netcdf_attrs['Global_Attributes'][gatts]


### Save as NetCDF for all data and daily (as a function of time)
date_r = pd.date_range('2016-09-01', freq='D', periods=31)
for day in date_r:
    t =AllData_x.isel(time=AllData_x['time.day'] == day.day)
    if t.dims['time'] !=0:
        t.to_netcdf('ACROBAT_AQ1601_'+str(day).split()[0]+'.nc',format='NETCDF4')


#### Coordinate test


### Sample Figures
verbose_figures = False

if verbose_figures:
	plt.figure()
	plt.subplot(1,1,1)
	ACROBAT.plot(x=ACROBAT.index,y='vd', ax=plt.gca())
	AllData.plot(x=AllData.index,y='Pressure', ax=plt.gca())