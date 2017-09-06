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
 2017-03-16 - S.BELL: Add second pass option to files

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
	help='choose: ACROBAT, GPS, FastCAT, SUNA, ECOTriplet, AanOptode')
parser.add_argument('-ini','--ini_file', type=str,
               help='complete path to yaml instrument ini (state) file')

args = parser.parse_args()

#######################
#
# Data Ingest and Processing
state_config = ConfigParserLocal.get_config_yaml(args.ini_file)

###
#
# load database
config_file = 'EcoFOCI_config/db_config/db_config_acrobat_root.pyini'
EcoFOCI_db = EcoFOCI_db_acrobat()
(db,cursor) = EcoFOCI_db.connect_to_DB(db_config_file=config_file)

if args.Instrument in ['GPS','gps']:
	instid = 'gps'
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=instid)
	for index, row in rawdata.iterrows():
		EcoFOCI_db.add_to_DB(table=state_config['db_table'][instid],verbose=False,pctime=row['DateTime'],
																				  latitude=row['Latitude'],
																				  longitude=row['Longitude'])
elif args.Instrument in ['fastcat','FastCAT','sbe49']:
	instid = 'ctd'
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=instid)
	rawdata = rawdata.where((pd.notnull(rawdata)), None)
	for index, row in rawdata.iterrows():
		EcoFOCI_db.add_to_DB(table=state_config['db_table'][instid],verbose=False,pctime=row['DateTime'],
																				  temperature=row['Temperature'],
																				  conductivity=row['Conductivity'],
																				  pressure=row['Pressure'])
elif args.Instrument in ['ECOTriplet','triplet','wetlabs']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=Acrobat_ECOTriplet)
	instid = 'triplet'
elif args.Instrument in ['ACROBAT','acrobat']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=Acrobat_System, UTC_offset_corr=7)
	instid = 'acrobat'
elif args.Instrument in ['AanOptode','optode']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source=Acrobat_AanOptode)
	instid = 'oxy'
else:
	print "Instrument not identified.  See commandline help for options"



db.close() 

