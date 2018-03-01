#!/usr/bin/env python

"""
 Background:
 --------
 ACROBAT_raw2db.py
 
 
 Purpose:
 --------
 Read and Parse GPS, Fastcat, SUNA, ECO feed from ACROBAT
 
 History:
 --------

"""

import argparse
import pandas as pd

from io_utils import ACROBAT_data_read
from io_utils.EcoFOCI_db_io import EcoFOCI_db_acrobat
from io_utils import ConfigParserLocal 


"""---"""

parser = argparse.ArgumentParser(description='CTD plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,
	help='full path to directory of processed nc files')
parser.add_argument('Instrument', metavar='Instrument', type=str,
	help='choose: ACROBAT, GPS, FastCAT/TSG, SUNA, ECOTriplet/ECO, AanOptode')
parser.add_argument('-ini','--ini_file', type=str,
               help='complete path to yaml instrument ini (state) file')

args = parser.parse_args()

#######################
#
# Data Ingest and Processing
state_config = ConfigParserLocal.get_config(args.ini_file,ftype='yaml')

###
#
# load database
config_file = 'EcoFOCI_config/db_config/db_config_underway.yaml'
EcoFOCI_db = EcoFOCI_db_acrobat()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file,ftype='yaml')

if args.Instrument in ['GPS','gps']:
	instid = 'gps'
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=instid)
	for index, row in rawdata.iterrows():
		try:
			EcoFOCI_db.add_to_DB(table=state_config['db_table'][instid],verbose=True,
																  PCTime=row['PCTime'],
																  GPSTime=row['DateTime'],
																  Latitude=row['Latitude'],
																  Longitude=row['Longitude'],
																  Spd_Over_Grnd=row['SOG'])
		except:
			pass
elif args.Instrument in ['fastcat','FastCAT','sbe49']:
	instid = 'ctd'
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=instid)
	rawdata = rawdata.where((pd.notnull(rawdata)), None)
	for index, row in rawdata.iterrows():
		try:
			EcoFOCI_db.add_to_DB(table=state_config['db_table'][instid],verbose=False,pctime=row['DateTime'],
																				  temperature=row['Temperature'],
																				  conductivity=row['Conductivity'],
																				  pressure=row['Pressure'])
		except:
			pass

elif args.Instrument in ['TSG']:
	instid = 'tsg'
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=instid)
	rawdata = rawdata.where((pd.notnull(rawdata)), None)
	for index, row in rawdata.iterrows():
		try:
			EcoFOCI_db.add_to_DB(table=state_config['db_table'][instid],verbose=False,PCTime=row['DateTime'],
																				  Temperature=row['Temperature'],
																				  Conductivity=row['Conductivity'],
																				  Salinity=row['Salinity'])
		except:
			pass

elif args.Instrument in ['ECOTriplet','triplet','wetlabs']:
	instid = 'triplet'
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=instid)
	rawdata = rawdata.where((pd.notnull(rawdata)), None)
	for index, row in rawdata.iterrows():
		try:
			EcoFOCI_db.add_to_DB(table=state_config['db_table'][instid],verbose=False,pctime=row['DateTime'],
																				  sig700nm=row['700nm'],
																				  sig695nm=row['695nm'],
																				  sig460nm=row['460nm'])
		except:
			pass

elif args.Instrument in ['ECO']:
	instid = 'eco'
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=instid)
	rawdata = rawdata.where((pd.notnull(rawdata)), None)
	for index, row in rawdata.iterrows():
		try:
			EcoFOCI_db.add_to_DB(table=state_config['db_table'][instid],verbose=False,pctime=row['DateTime'],
																				  sig695nm=row['695nm'])
		except:
			pass

elif args.Instrument in ['ACROBAT','acrobat']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=Acrobat_System, UTC_offset_corr=7)
	instid = 'acrobat'

elif args.Instrument in ['AanOptode','optode']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=Acrobat_AanOptode)
	instid = 'oxy'
else:
	print "Instrument not identified.  See commandline help for options"



db.close() 

