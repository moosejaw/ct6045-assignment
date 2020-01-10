#!/usr/bin/env python3
'''
This script is designed to emulate normal web traffic. Therefore, it will
request the server page in a randomly-assigned interval. The request is sent
as normal using Python's built-in urllib library. The request is opened and
closed as normal.
'''
import time
import random
from urllib import request
from threading import Thread

# Set the target as defined by the container name and port
TARGET   = 'http://target/'
THREADS  = 5 # 5 simulations of normal traffic
TIME_MIN = 1
TIME_MAX = 8

def simulateTraffic():
    while True:
        # Pause for a random time in the given range
        time.sleep(random.randrange(TIME_MIN, TIME_MAX))
        # Open the request
        request.urlopen(TARGET)

if __name__ == '__main__':
    # Wait a few seconds for the target container to spin up
    time.sleep(10)

    # Create threads and join them
    threads = []
    for i in range(THREADS):
        proc = Thread(target=simulateTraffic)
        proc.start()
        threads.append(proc)
    for thread in threads: thread.join()    
