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

"""

import argparse

from io_utils import ACROBAT_data_read

parser = argparse.ArgumentParser(description='CTD plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,
	help='full path to directory of processed nc files')
parser.add_argument('Instrument', metavar='Instrument', type=str,
	help='choose: ACROBAT, GPS, FastCAT/TSG, SUNA, ECOTriplet/ECO, AanOptode, ISUS, ECO')
parser.add_argument('-timecorr','--timecorr', type=int, default=0,
    help='time correction in seconds to match pc to gps')
parser.add_argument('-avestring','--averaging_string', type=str, default='1s',
    help='averaging string eg. 1s, 60s, 1h')
args = parser.parse_args()

if args.Instrument in ['GPS','gps']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='gps', time_correction_seconds=args.timecorr)
	print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
elif args.Instrument in ['fastcat','FastCAT']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='fastcat', time_correction_seconds=args.timecorr)
	print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
elif args.Instrument in ['TSG']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='tsg', time_correction_seconds=args.timecorr)
	print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
elif args.Instrument in ['ECOTriplet']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='ECOTriplet', time_correction_seconds=args.timecorr)
	print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
elif args.Instrument in ['ECO']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='eco', time_correction_seconds=args.timecorr)
	print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
elif args.Instrument in ['ACROBAT','acrobat']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='acrobat', time_correction_seconds=args.timecorr, UTC_offset_corr=7)
	print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
elif args.Instrument in ['AanOptode','optode']:
	rawdata = ACROBAT_data_read.get_inst_data(args.DataPath, source='optode', time_correction_seconds=args.timecorr)
	print rawdata.resample(args.averaging_string,label='right',closed='right').mean().to_csv()
else:
	print "Instrument not identified.  See commandline help for options"
