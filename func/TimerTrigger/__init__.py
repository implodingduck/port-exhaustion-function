import datetime
import logging

import azure.functions as func


from time import sleep
import socket, threading

import pyodbc
import os
import json

max_threads = 50
final = {}
def check_port(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        socket.setdefaulttimeout(2.0) # seconds (float)
        result = sock.connect_ex((ip,port))
        if result == 0:
            # print ("Port is open")
            final[port] = "OPEN"
        #else:
            ## print ("Port is closed/filtered")
            #final[port] = "CLOSED"
        sock.close()
    except:
        pass


def do_stuff(cursor):
    cursor.execute("SELECT TOP 3 name, collation_name FROM sys.databases")
    row = cursor.fetchone()
    while row:
        logging.info(str(row[0]) + " " + str(row[1]))
        row = cursor.fetchone()

global_conn = None
global_cursor = None

def main(mytimer: func.TimerRequest) -> None:
    global global_conn
    global global_cursor

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    server = os.environ.get('DB_HOST')
    database = os.environ.get('DB_NAME')
    username = os.environ.get('DB_USER')
    
    driver= '{ODBC Driver 17 for SQL Server}'

    func_type = os.environ.get('FUNC_TYPE')
    
    if func_type == 'USEWITH':
      logging.info('Using the with keyword logic')
      with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';Authentication=ActiveDirectoryMsi;') as wconn:
        with wconn.cursor() as wcursor:
          do_stuff(wcursor)
    elif func_type == 'USEGLOBAL':
        logging.info('Using the global logic')
        if global_conn == None:
            logging.info('creating a new connection...')
            global_conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';Authentication=ActiveDirectoryMsi;')
        if global_cursor == None:
            logging.info('creating a new cursor...')
            global_cursor = global_conn.cursor()        
        do_stuff(global_cursor)
    else:
        logging.info('Using the local logic')
        conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';Authentication=ActiveDirectoryMsi;')
        cursor = conn.cursor()
        do_stuff(cursor)
            

    for port in range(49152,65535):
        threading.Thread(target=check_port, args=['127.0.0.1', port]).start()
        #sleep(0.1)

        # limit the number of threads.
        while threading.active_count() > max_threads :
            sleep(1)

    sleep(1)
    
    logging.info(json.dumps(final))
    logging.info(f"Number of ports used: {len(final)}")
    
    