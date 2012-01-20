import os
import re
import urllib
import datetime
import sqlite3
import logging
from time import sleep

log_path = 'bicing.log'
db_path = 'bicing.sqlite3'

logging.basicConfig(filename=log_path, level=logging.INFO)

if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create table
    c.execute('create table Station (id int, name text)')
    c.execute('create table RackStatus(id int, full_anchors int, empty_anchors int, timestamp text)')
    f = urllib.urlopen("http://www.bicing.cat/localizaciones/localizaciones.php")
    text = f.read()
    stations = re.findall(r"<!\[CDATA\[([^\]]+)\]\]", text)
    for station in stations:
        prog = re.compile(r'.*?(\d+) - ([^<]+).*', re.UNICODE)
        m = prog.match(station)
        t = (int(m.groups()[0]), m.groups()[1].decode('iso_8859_1'))
        c.execute('insert into Station values (?,?)', t)
    conn.commit()    
    f.close()
    c.close()
    conn.close()
    logging.info("{0} database created.".format(db_path)) 

    
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
while True:
    sleep(50)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        f = urllib.urlopen("http://www.bicing.cat/localizaciones/localizaciones.php")
        text = f.read()
        stations = re.findall(r"<!\[CDATA\[([^\]]+)\]\]", text)
        for station in stations:
            #prog = re.compile(r'.*?(\d+) - ([^<]+).*>(\d+)<br />([-]?\d+)<br />',
            prog = re.compile(r'.*?(\d+) - .*>(\d+)<br />([-]?\d+)<br />',
                              re.UNICODE)
            m = prog.match(station)
            if m:
                t = (int(m.groups()[0]), int(m.groups()[1]), int(m.groups()[2]), timestamp)
                cursor.execute('insert into RackStatus values (?,?,?,?)', t)
            else:
                logging.error("Station doesn't match: \n{0}".format(station))
        conn.commit()        
        f.close()        
    except IOError:
        # Ignore erroneous HTTP requests.
        logging.warning("{0} request failed.".format(timestamp))
cursor.close()
conn.close()
