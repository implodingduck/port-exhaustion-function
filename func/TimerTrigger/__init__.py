import datetime
import logging

import azure.functions as func


from time import sleep
import socket, threading

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



def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    for port in range(49152,65535):
        threading.Thread(target=check_port, args=['127.0.0.1', port]).start()
        #sleep(0.1)

        # limit the number of threads.
        while threading.active_count() > max_threads :
            sleep(1)

    sleep(1)
    print(final)
