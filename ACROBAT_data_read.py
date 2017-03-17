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
 2017-03-16 - S.BELL: Add second pass option to files

"""
import datetime
import numpy as np
import pandas as pd
import argparse
from io import BytesIO


def get_inst_data(filename, passnumber='first', **kwargs):
	r"""

	Parameters
	----------
	filename : string
		complete path to file to be ingested
	passnumber : string
		'first','second'
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
	if passnumber == 'first':
		src = kwargs['source']
		fobj = src.get_data(filename)
		Dataset = src.parse(fobj, **kwargs)
	elif passnumber == 'second':
		src = kwargs['source']
		fobj = src.get_data(filename)
		Dataset = src.parse_second(fobj, **kwargs)
	else:
		raise RuntimeError('Invalid passnumber')

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
		print rawdata.resample('1s',label='right',closed='right').mean().interpolate().to_csv()

	@staticmethod	
	def parse_second(fobj, **kwargs):
		r"""
		Method to parse gps data from ACROBAT after first pass
		"""
		rawdata = pd.read_csv(fobj)       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%d %H:%M:%S')
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

		rawdata = pd.read_csv(fobj, names=['DateTime','Temperature','Conductivity','Pressure'])       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%dT%H:%M:%S')
		rawdata['Temperature'] = pd.to_numeric(rawdata['Temperature'],errors='coerce',downcast='float')
		rawdata['Conductivity'] = pd.to_numeric(rawdata['Conductivity'],errors='coerce',downcast='float')
		rawdata['Pressure'] = pd.to_numeric(rawdata['Pressure'],errors='coerce',downcast='float')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		print rawdata.resample('1s',label='right',closed='right').mean().interpolate().to_csv()

	@staticmethod	
	def parse_second(fobj, **kwargs):
		r"""
		Method to parse gps data from ACROBAT after first pass
		"""
		rawdata = pd.read_csv(fobj)       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%d %H:%M:%S')
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
		#columns = ['DateTime','EcoDate','EcoTime','700nm','695nm','460nm']
		#columns_ind = [0,1,2,4,6,8]
		##use following if gps feed exists... rely on gps for time syncing
		columns = ['DateTime','700nm','695nm','460nm']
		columns_ind = [0,4,6,8]		

		rawdata = pd.read_csv(fobj, names=columns, usecols=columns_ind,sep='\s+|,',engine='python')       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%dT%H:%M:%S')
		rawdata['700nm'] = pd.to_numeric(rawdata['460nm'],errors='coerce',downcast='integer')
		rawdata['695nm'] = pd.to_numeric(rawdata['460nm'],errors='coerce',downcast='integer')
		rawdata['460nm'] = pd.to_numeric(rawdata['460nm'],errors='coerce',downcast='integer')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		print rawdata.resample('1s',label='right',closed='right').mean().interpolate().to_csv()

	@staticmethod	
	def parse_second(fobj, **kwargs):
		r"""
		Method to parse gps data from ACROBAT after first pass
		"""
		rawdata = pd.read_csv(fobj)       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%d %H:%M:%S')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		print rawdata.resample('1s',label='right',closed='right').mean().to_csv()

class Acrobat_System(object):

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
		Method to parse Acrobat internal data from ACROBAT
		"""

		columns = ['yyyy','ddd','hh:mm:ss','latdd','lathhmm','latNS','londd','lonhhmm','lonEW',
			'S:004','vn','ve','wc','vd','lb','wa','alt','sv','md','ul','ll','k1','k2','k3',
			'roll','pitch','heading','temperature','altitude','gps time']

		rawdata = pd.read_csv(fobj, names=columns,skiprows=18)       
		rawdata['DateTime'] = pd.to_datetime((rawdata.yyyy).apply(str)+' '+(rawdata.ddd).apply(str)+' '+rawdata['hh:mm:ss'],format='%Y %j %H:%M:%S')
		
		if kwargs['UTC_offset_corr']:
			toff = str(kwargs['UTC_offset_corr']) + ' hours'
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(toff)
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		rawdata.drop(['yyyy','ddd','gps time'], axis=1, inplace=True)
		print rawdata.resample('1s',label='right',closed='right').mean().to_csv()

	@staticmethod	
	def parse_second(fobj, **kwargs):
		r"""
		Method to parse gps data from ACROBAT after first pass
		"""
		rawdata = pd.read_csv(fobj)       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%d %H:%M:%S')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		print rawdata.resample('1s',label='right',closed='right').mean().to_csv()

"""--------------------------------------------------------------------------------------"""
parser = argparse.ArgumentParser(description='CTD plots')
parser.add_argument('DataPath', metavar='DataPath', type=str,
	help='full path to directory of processed nc files')
parser.add_argument('Instrument', metavar='Instrument', type=str,
	help='choose: ACROBAT, GPS, FastCAT, SUNA, ECOTriplet')
parser.add_argument('-sp','--second_pass', action="store_true",
    help='second round of parsing if chosen')

args = parser.parse_args()

if not args.second_pass:
	if args.Instrument in ['GPS','gps']:
		get_inst_data(args.DataPath, source=Acrobat_GPS)
	elif args.Instrument in ['fastcat','FastCAT']:
		get_inst_data(args.DataPath, source=Acrobat_FastCAT)
	elif args.Instrument in ['ECOTriplet']:
		get_inst_data(args.DataPath, source=Acrobat_ECOTriplet)
	elif args.Instrument in ['ACROBAT','acrobat']:
		get_inst_data(args.DataPath, source=Acrobat_System, UTC_offset_corr=7)
	else:
		print "Instrument not identified.  See commandline help for options"
else:
	if args.Instrument in ['GPS','gps']:
		get_inst_data(args.DataPath, source=Acrobat_GPS, passnumber='second')
	elif args.Instrument in ['fastcat','FastCAT']:
		get_inst_data(args.DataPath, source=Acrobat_FastCAT, passnumber='second')
	elif args.Instrument in ['ECOTriplet']:
		get_inst_data(args.DataPath, source=Acrobat_ECOTriplet, passnumber='second')
	elif args.Instrument in ['ACROBAT','acrobat']:
		get_inst_data(args.DataPath, source=Acrobat_System, passnumber='second')	
	else:
		print "Instrument not identified.  See commandline help for options"	