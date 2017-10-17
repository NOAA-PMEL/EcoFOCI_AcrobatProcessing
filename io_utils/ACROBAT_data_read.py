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
 2017-10-16 - S.BELL: update nmea parsing
 2017-03-16 - S.BELL: Add second pass option to files

"""
import datetime
import numpy as np
import pandas as pd
import mysql.connector

from io import BytesIO

import pynmea2

def available_data_sources():
	r"""List of acronyms and options for names for instruments"""
	sources = {
			   'gps':Acrobat_GPS,'ctd':Acrobat_FastCAT,'triplet':Acrobat_ECOTriplet,
			   'tsg':Acrobat_TSG,'eco':Acrobat_ECO
			   }
	return sources

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
		src = available_data_sources().get(kwargs['source'])
		fobj = src.get_data(filename)
		Dataset = src.parse(fobj, **kwargs)
		return Dataset
	elif passnumber == 'second':
		src = available_data_sources().get(kwargs['source'])
		fobj = src.get_data(filename)
		Dataset = src.parse_second(fobj, **kwargs)
		return Dataset
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
	def parse(fobj, use_pynmea2=True, **kwargs):
		r"""
		Method to parse gps data from ACROBAT
		"""

		rawdata = pd.DataFrame(columns=['DateTime','Latitude','Longitude','SOG'])
		for k, line in enumerate(fobj.readlines()):

			line = line.strip()

			if use_pynmea2:
				#only good to the second... uses most recent gps data and ignores
				#all other data if frequency is > 1hz
				if '$GPRMC' in line:  # Get end of header.
					line_parse = line.split(',')

					try:
						nofrag, frag = line_parse[0].split('.')
						dt_nofrag = datetime.datetime.strptime(nofrag,'%Y-%m-%dT%H:%M:%S')
						dt_msec = dt_nofrag.replace(microsecond=int(frag))
					except:
						nofrag = line_parse[0]
						dt_nofrag = datetime.datetime.strptime(nofrag,'%Y-%m-%dT%H:%M:%S')

					data=pynmea2.parse(",".join(line_parse[1:]))

					rawdata =rawdata.append(pd.DataFrame([[dt_msec,
											data.datetime,
											data.latitude,
											data.longitude,
											data.spd_over_grnd]],
											columns=['PCTime','DateTime','Latitude','Longitude','SOG']),
											ignore_index=True)
			else:
				if '$GPRMC' in line:  # Get end of header.
					line_parse = line.split(',')
					try:
						nofrag, frag = line_parse[0].split('.')
						dt_nofrag = datetime.datetime.strptime(nofrag,'%Y-%m-%dT%H:%M:%S')
						dt_msec = dt_nofrag.replace(microsecond=int(frag))
					except:
						nofrag = line_parse[0]
						dt_nofrag = datetime.datetime.strptime(nofrag,'%Y-%m-%dT%H:%M:%S')

					strlat = line_parse[4]
					strlon = line_parse[6]

					rawdata =rawdata.append(pd.DataFrame([[dt_msec,
											float(strlat[0:2]) + float(strlat[2:])/60,
											float(strlon[0:3]) + float(strlon[3:])/60],
											float(line_parse[8])],
											columns=['DateTime','Latitude','Longitude','SOG']),
											ignore_index=True)

		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))

		if kwargs['time_correction_seconds']:
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(seconds=kwargs['time_correction_seconds'])

		return rawdata

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

		if kwargs['time_correction_seconds']:
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(seconds=kwargs['time_correction_seconds'])

		return rawdata

class Acrobat_TSG(object):

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

		rawdata = pd.read_csv(fobj, names=['DateTime','Temperature','Conductivity','Salinity'])       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%dT%H:%M:%S')
		rawdata['Temperature'] = pd.to_numeric(rawdata['Temperature'],errors='coerce',downcast='float')
		rawdata['Conductivity'] = pd.to_numeric(rawdata['Conductivity'],errors='coerce',downcast='float')
		rawdata['Salinity'] = pd.to_numeric(rawdata['Salinity'],errors='coerce',downcast='float')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))

		if kwargs['time_correction_seconds']:
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(seconds=kwargs['time_correction_seconds'])

		return rawdata

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

		rawdata = pd.read_csv(fobj, names=columns, usecols=columns_ind,sep='\s+|,',engine='python', error_bad_lines=False)       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%dT%H:%M:%S')
		rawdata['700nm'] = pd.to_numeric(rawdata['700nm'],errors='coerce',downcast='integer')
		rawdata['695nm'] = pd.to_numeric(rawdata['695nm'],errors='coerce',downcast='integer')
		rawdata['460nm'] = pd.to_numeric(rawdata['460nm'],errors='coerce',downcast='integer')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))

		if kwargs['time_correction_seconds']:
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(seconds=kwargs['time_correction_seconds'])

		return rawdata


class Acrobat_ECO(object):

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
		columns = ['DateTime','695']
		columns_ind = [0,4]		

		rawdata = pd.read_csv(fobj, names=columns, usecols=columns_ind,sep='\s+|,',engine='python', error_bad_lines=False)       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%dT%H:%M:%S')
		rawdata['695nm'] = pd.to_numeric(rawdata['695nm'],errors='coerce',downcast='integer')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))

		if kwargs['time_correction_seconds']:
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(seconds=kwargs['time_correction_seconds'])

		return rawdata

class Acrobat_AanOptode(object):

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
		Method to parse Aandera Optode data from ACROBAT
		"""
		columns = ['DateTime','O2Concentration[uM]','AirSaturation[%]','Temperature[Deg.C]']
		columns_ind = [0,5,7,9]		

		rawdata = pd.read_csv(fobj, names=columns, usecols=columns_ind,sep='\s+|,',engine='python')       
		rawdata.DateTime = pd.to_datetime(rawdata.DateTime,format='%Y-%m-%dT%H:%M:%S')
		rawdata['O2Concentration[uM]'] = pd.to_numeric(rawdata['O2Concentration[uM]'],errors='coerce',downcast='integer')
		rawdata['AirSaturation[%]'] = pd.to_numeric(rawdata['AirSaturation[%]'],errors='coerce',downcast='integer')
		rawdata['Temperature[Deg.C]'] = pd.to_numeric(rawdata['Temperature[Deg.C]'],errors='coerce',downcast='integer')
		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))

		if kwargs['time_correction_seconds']:
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(seconds=kwargs['time_correction_seconds'])

		return rawdata

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

		rawdata = pd.read_csv(fobj, names=columns,skiprows=18, error_bad_lines=False)       
		rawdata['DateTime'] = pd.to_datetime((rawdata.yyyy).apply(str)+' '+(rawdata.ddd).apply(str)+' '+rawdata['hh:mm:ss'],format='%Y %j %H:%M:%S')
		
		if kwargs['UTC_offset_corr']:
			toff = str(kwargs['UTC_offset_corr']) + ' hours'
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(toff)

		if kwargs['time_correction_seconds']:
			rawdata['DateTime'] = rawdata['DateTime']+pd.Timedelta(seconds=kwargs['time_correction_seconds'])

		rawdata = rawdata.set_index(pd.DatetimeIndex(rawdata['DateTime']))
		rawdata.drop(['yyyy','ddd','gps time'], axis=1, inplace=True)
		return rawdata


