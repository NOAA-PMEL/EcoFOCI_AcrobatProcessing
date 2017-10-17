#!/usr/bin/env python

"""
 Background:
 --------
 ACROBAT_raw2csv.py
 
 
 Purpose:
 --------
 Read and Parse GPS, Fastcat, SUNA, ECO feed from ACROBAT
 
 History:
 --------
 2017-03-16 - S.BELL: Add second pass option to files

"""

import argparse

from io_utils import ACROBAT_data_read

parser = argparse.ArgumentParser(description='CTD plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,
	help='full path to directory of processed nc files')
parser.add_argument('Instrument', metavar='Instrument', type=str,
	help='choose: ACROBAT, GPS, FastCAT, SUNA, ECOTriplet, AanOptode, ISUS, ECO')
parser.add_argument('-sp','--second_pass', action="store_true",
    help='second round of parsing if chosen')
parser.add_argument('-avestring','--averaging_string', type=str, default='1s',
    help='averaging string eg. 1s, 60s, 1h')

args = parser.parse_args()

if not args.second_pass:
	if args.Instrument in ['GPS','gps']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='gps')
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	elif args.Instrument in ['fastcat','FastCAT']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='fastcat')
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	elif args.Instrument in ['ECOTriplet']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='ECOTriplet')
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	elif args.Instrument in ['ACROBAT','acrobat']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='acrobat', UTC_offset_corr=7)
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	elif args.Instrument in ['AanOptode','optode']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='optode')
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	else:
		print "Instrument not identified.  See commandline help for options"
else:
	if args.Instrument in ['GPS','gps']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='gps', passnumber='second')
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	elif args.Instrument in ['fastcat','FastCAT']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='fastcat', passnumber='second')
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	elif args.Instrument in ['ECOTriplet']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='ECOTriplet', passnumber='second')
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	elif args.Instrument in ['ACROBAT','acrobat']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='acrobat', passnumber='second')	
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	elif args.Instrument in ['AanOptode','optode']:
		rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='optode', passnumber='second')
		print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
	else:
		print "Instrument not identified.  See commandline help for options"	