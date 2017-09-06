#!/usr/bin/env python

"""
 Background:
 --------
 EcoFOCI_db_io.py
 
 
 Purpose:
 --------
 Various Routines and Classes to interface with the mysql database that houses EcoFOCI meta data
 
 History:
 --------
 2017-07-28 S.Bell - replace pymsyql with mysql.connector -> provides purepython connection and prepared statements

"""

import mysql.connector
import ConfigParserLocal 
import datetime
import numpy as np

__author__   = 'Shaun Bell'
__email__    = 'shaun.bell@noaa.gov'
__created__  = datetime.datetime(2017, 7, 28)
__modified__ = datetime.datetime(2017, 7, 28)
__version__  = "0.2.0"
__status__   = "Development"
__keywords__ = 'netCDF','meta','header','pymysql'

class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    def _float32_to_mysql(self, value):
        if np.isnan(value):
            return None
        return float(value)

    def _float64_to_mysql(self, value):
        if np.isnan(value):
            return None
        return float(value)

    def _int32_to_mysql(self, value):
        if np.isnan(value):
            return None
        return int(value)

    def _int64_to_mysql(self, value):
        if np.isnan(value):
            return None
        return int(value)

class EcoFOCI_db_acrobat(object):
    """Class definitions to access EcoFOCI Mooring Database"""

    def connect_to_DB(self, db_config_file=None):
        """Try to establish database connection

        Parameters
        ----------
        db_config_file : str
            full path to json formatted database config file    

        """
        db_config = ConfigParserLocal.get_config(db_config_file)
        try:
            self.db = mysql.connector.connect(**db_config)
        except mysql.connector.Error as err:
          """
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)
          """
          print("error - will robinson")
          
        self.db.set_converter_class(NumpyMySQLConverter)

        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor(dictionary=True)
        self.prepcursor = self.db.cursor(prepared=True)
        return(self.db,self.cursor)

    def manual_connect_to_DB(self, host='localhost', user='viewer', 
                             password=None, database='ecofoci', port=3306):
        """Try to establish database connection

        Parameters
        ----------
        host : str
            ip or domain name of host
        user : str
            account user
        password : str
            account password
        database : str
            database name to connect to
        port : int
            database port

        """
        db_config = {}     
        db_config['host'] = host
        db_config['user'] = user
        db_config['password'] = password
        db_config['database'] = database
        db_config['port'] = port

        try:
            self.db = mysql.connector.connect(**db_config)
        except:
            print "db error"
            
        # prepare a cursor object using cursor() method
        self.cursor = self.db.cursor(dictionary=True)
        self.prepcursor = self.db.cursor(prepared=True)
        return(self.db,self.cursor)


    def add_to_DB(self,table=None,verbose=True,**kwargs):
        """

        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        insert_stmt = "INSERT INTO {table} ({columns}) VALUES ({datapts})".format(
            table=table,
            columns= ','.join(kwargs.keys()),
            datapts=','.join(['?']*len(kwargs.keys())))
        data = (kwargs.values())
        try:
           # Execute the SQL command
           self.prepcursor.execute(insert_stmt,tuple(data))
           self.db.commit()
        except mysql.connector.Error as err:
           print err
           # Rollback in case there is any error
           print "No Bueno"
           print "Failed insert ###" + insert_stmt + "###"
           print tuple(data)



    def close(self):
        """close database"""
        self.prepcursor.close()
        self.cursor.close()
        self.db.close()

