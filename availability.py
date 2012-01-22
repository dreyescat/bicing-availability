import os
import re
import urllib2
import datetime
import sqlite3
import logging
from time import sleep

LOG_FILENAME = 'bicing.log'
DB_FILENAME = 'bicing.sqlite3'

SCHEME = 'https'
AUTHORITY = 'www.bicing.cat'
STATIONS_PATH = '/localizaciones/localizaciones.php'
RACK_STATUS_PATH = '/CallWebService/StationBussinesStatus_Cache.php'

STATIONS_URI = SCHEME + '://' + AUTHORITY + STATIONS_PATH
RACK_STATUS_URI = SCHEME + '://' + AUTHORITY + RACK_STATUS_PATH

logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)

def create_database_schema(filename):
    connection = sqlite3.connect(filename)
    cursor = connection.cursor()

    cursor.execute('create table Station (id int, name text)')
    cursor.execute('create table RackStatus(id int, full_anchors int, empty_anchors int, timestamp text)')
    f = urllib2.urlopen(STATIONS_URI)
    text = f.read()
    stations = re.findall(
        r'<a href="javascript:ada\(\'\d+\'\)">(\d+) - ([^<]+).*' , text)
    for station in stations:
        cursor.execute('insert into Station values (?,?)', (int(station[0]),
            station[1].decode('iso_8859_1')))
    connection.commit()    
    f.close()
    cursor.close()
    connection.close()
    logging.info('{0} database created.'.format(DB_FILENAME)) 
    
if not os.path.exists(DB_FILENAME):
    create_database_schema(DB_FILENAME)

connection = sqlite3.connect(DB_FILENAME)
cursor = connection.cursor()
cursor.execute('select id from Station')
codes = [t[0] for t in cursor]

while True:
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for code in codes:
        try:
            f = urllib2.urlopen(RACK_STATUS_URI, 'idStation={0}'.format(code))
            data = f.read()
            status = re.findall(r': (\d+)<br>', data)
            if len(status) == 2:
                t = (code, int(status[0]), int(status[1]), timestamp)
                cursor.execute('insert into RackStatus values (?,?,?,?)', t)
            else:
                logging.error('Station doesn\'t match: \n{0}'.format(data))
            connection.commit()
            f.close()
        except IOError:
            # Ignore erroneous HTTP requests.
            logging.warning('{0} request failed.'.format(timestamp))
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sleep(60)
cursor.close()
connection.close()
