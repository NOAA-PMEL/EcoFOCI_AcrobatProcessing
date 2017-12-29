"""
 prawler2netcdf_pico.py
 
 Description:
    Once the underway/acrobat data is converted to text files with the desired temporal
    resolution. This converts them into CF compliant NetCDF files

    Routine is based on the data format provided by the underway/acrobat realtime collection.
"""

# Standard library.
import datetime

# System Stack
import argparse

# Scientific stack.
import numpy as np
import pandas as pd
import seawater as sw
from netCDF4 import date2num, num2date

# User Stack
import io_utils.EcoFOCI_netCDF_write as EcF_write
import io_utils.ConfigParserLocal as ConfigParserLocal

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2017, 12, 19)
__modified__ = datetime.datetime(2017, 12, 19)
__version__  = "0.1.0"
__status__   = "Development"


"""-------------------------------------- Main ----------------------------------------------"""

parser = argparse.ArgumentParser(description='RUDICS PICO Prawler Data File')
parser.add_argument('DataPath', metavar='DataPath', type=str,
               help='full path to file')
parser.add_argument('ConfigFile', metavar='ConfigFile', type=str,
               help='full path to nc config file')
parser.add_argument('OutPreFix', metavar='OutPreFix', type=str,
               help='prefix for output file')
parser.add_argument('-is1D','--is1D', action="store_true",
               help='1D ragged arrays')

args = parser.parse_args()


data = pd.read_csv(args.DataPath)
data.set_index(pd.DatetimeIndex(data['DateTime']),inplace=True)
data['time'] = [date2num(x[1],'hours since 1900-01-01T00:00:00Z') for x in enumerate(data.index)]

EPIC_VARS_dict = ConfigParserLocal.get_config(args.ConfigFile,'yaml')

if args.is1D:
    #create new netcdf file
    ncinstance = EcF_write.NetCDF_Create_Profile_Ragged1D(savefile='data/' + args.OutPreFix + '.nc')
    ncinstance.file_create()
    ncinstance.sbeglobal_atts(raw_data_file=args.DataPath.split('/')[-1], 
        History='File Created.')
    ncinstance.dimension_init(recnum_len=len(data))
    ncinstance.variable_init(EPIC_VARS_dict)
    ncinstance.add_coord_data(recnum=range(1,len(data)+1))
    ncinstance.add_data(EPIC_VARS_dict,data_dic=data,missing_values=np.nan,pandas=True)
    ncinstance.close()

