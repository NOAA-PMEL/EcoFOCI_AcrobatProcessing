#!/usr/bin/env python

"""
 Background:
 --------
 ACROBAT_data_read.py
 
 
 Purpose:
 --------
 Read and Parse GPS, Fastcat, SUNA, ECO feed from ACROBAT
 
 History:
 --------

"""
import datetime
import numpy as np
import pandas as pd
import argparse
from io import BytesIO


def get_inst_data(filename, **kwargs):
	r"""

	Parameters
	----------
	filename : string
		complete path to file to be ingested

	kwargs
		Arbitrary keyword arguments to use to initialize source

	Returns
	-------
	Dataset : dictionary of dictionaries
		time : dictionary
			key: 	dataindex
			value:	datetime type
		variables : dictionary of dictionaries
			key: 	dataindex
			value:	float, int, string (depending on instrument)

	"""
	src = kwargs['source']
	fobj = src.get_data(filename)
	Dataset = src.parse(fobj, **kwargs)


class Acrobat_GPS(object):

	@staticmethod
	def get_data(filename=None, **kwargs):
		r"""
		Basic Method to open files.  Specific actions can be passes as kwargs for instruments
		"""

		fobj = open(filename)
		data = fobj.read()


		buf = data
		return BytesIO(buf.strip())

	@staticmethod	
	def parse(fobj, **kwargs):
		r"""
		Method to parse gps data from ACROBAT
		"""

		rawdata = pd.DataFrame(columns=['DateTime','Latitude','Longitude'])
		for k, line in enumerate(fobj.readlines()):

			line = line.strip()

			if '$GPRMC' in line:  # Get end of header.
				line_parse = line.split(',')
				nofrag, frag = line_parse[0].split('.')
				dt_nofrag = datetime.datetime.strptime(nofrag,'%Y-%m-%dT%H:%M:%S')
				dt_msec = dt_nofrag.replace(microsecond=int(frag))
				strlat = line_parse[4]
				strlon = line_parse[6]

				rawdata =rawdata.append(pd.DataFrame([[dt_msec,
										float(strlat[0:2]) + float(strlat[2:])/60,
										float(strlon[0:3]) + float(strlon[3:])/60]],
										columns=['DateTime','Latitude','Longitude']),
										ignore_index=True)

		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		print rawdata.resample('1s',label='right',closed='right').mean().to_csv()

class Acrobat_FastCAT(object):

	@staticmethod
	def get_data(filename=None, **kwargs):
		r"""
		Basic Method to open files.  Specific actions can be passes as kwargs for instruments
		"""

		fobj = open(filename)
		data = fobj.read()


		buf = data
		return BytesIO(buf.strip())

	@staticmethod	
	def parse(fobj, sal_output=False, press_output=False, **kwargs):
		r"""
		Method to parse FastCat data from ACROBAT
		"""

		rawdata = pd.read_csv(fobj, names=['DateTime','Temperature','Conductivity','Pressure'], usecols=[0,1,3,5,7])       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%dT%H:%M:%S')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		print rawdata.resample('1s',label='right',closed='right').mean().to_csv()

class Acrobat_ECOTriplet(object):

	@staticmethod
	def get_data(filename=None, **kwargs):
		r"""
		Basic Method to open files.  Specific actions can be passes as kwargs for instruments
		"""

		fobj = open(filename)
		data = fobj.read()


		buf = data
		return BytesIO(buf.strip())

	@staticmethod	
	def parse(fobj, **kwargs):
		r"""
		Method to parse FastCat data from ACROBAT
		"""

		rawdata = pd.read_csv(fobj, names=['DateTime','EcoDate','EcoTime','700nm','695nm','460nm'],
									usecols=[0,1,2,4,6,8],sep='\s+|,',engine='python')       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%dT%H:%M:%S')
		#rawdata.EcoDateTime = pd.to_datetime(rawdata.EcoDateTime,format='%m/%d/%y %H:%M:%S')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		print rawdata.resample('1s',label='right',closed='right').mean().to_csv()


"""--------------------------------------------------------------------------------------"""
parser = argparse.ArgumentParser(description='CTD plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,
	help='full path to directory of processed nc files')
parser.add_argument('Instrument', metavar='Instrument', type=str,
	help='choose: GPS, FastCAT, SUNA, ECOTriplet')

args = parser.parse_args()

if args.Instrument in ['GPS','gps']:
	get_inst_data(args.DataPath, source=Acrobat_GPS)
elif args.Instrument in ['fastcat','FastCAT']:
	get_inst_data(args.DataPath, source=Acrobat_FastCAT)
elif args.Instrument in ['ECOTriplet']:
	get_inst_data(args.DataPath, source=Acrobat_ECOTriplet)
else:
	print "Instrument not identified.  See commandline help for options"
