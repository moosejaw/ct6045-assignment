#!/usr/bin/env python3
'''
This is a Python frontend which will run all of the packet scripts as
subprocesses.

The scripts to be run are:
- normal_traffic.py - a script which generates a request every so often,
and is designed to simulate normal web traffic.

- slowloris.py - a script from https://github.com/gkbrk/slowloris designed
to implement a slowloris DDoS attack.

- ddos.py - a script designed to simulate a DDoS attack by sending a high
volume of packets.
'''
import os
import time
import threading
import subprocess

TIME_TO_RUN = 3600 # Set time to let threads run in seconds before killing them

def printRunningFunction(func):
    print(f'Running the {func} function')

def runSlowloris():
    '''
    Runs the slowloris script in a subprocess.
    The slowloris uses 5 sockets.

    The slowloris script has some default output which we will redirect
    to /dev/null to keep docker container logs clean.
    '''
    printRunningFunction('slowloris')
    commands = ['python3',
        './slowloris/slowloris.py',
        '-s',
        '5',
        'http://target/'
    ]
    proc = subprocess.Popen(commands, stdout=open(os.devnull),
        stderr=open(os.devnull))
    proc.communicate()
    time.sleep(TIME_TO_RUN)
    proc.kill()

def runDdos():
    '''Runs the DDoS attack script.'''
    printRunningFunction('ddos')
    commands = ['./ddos.py']
    proc     = subprocess.Popen(commands)
    proc.communicate()
    time.sleep(TIME_TO_RUN)
    proc.kill()

def runNormalTraffic():
    '''Runs the script to simulate normal traffic.'''
    printRunningFunction('normal traffic')
    commands = ['./normal_traffic.py']
    proc     = subprocess.Popen(commands)
    proc.communicate()
    time.sleep(TIME_TO_RUN)
    proc.kill()


if __name__ == '__main__':
    # Get functions to run and execute a thread for each
    functions = [runSlowloris, runDdos, runNormalTraffic]
    for function in functions:
        thread = threading.Thread(target=function)
        thread.start()
